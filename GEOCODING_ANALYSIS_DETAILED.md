# Derby City Watch: Geocoding & Map Plotting Analysis

## Overview

This is a Jekyll-based public safety event tracking system for Louisville, KY. The system automatically extracts addresses from scanner update posts and geocodes them to plot on an interactive map.

---

## 1. GEOCODING WORKFLOW

### Architecture

```
Post Created → GitHub Actions Triggered → Python Script → Nominatim API → Cached Results → JavaScript Map
```

### Step-by-Step Process

#### 1.1 Address Extraction (Python & JavaScript)
**Script:** `scripts/geocode_addresses.py` (Python) & `_layouts/map.html` (JavaScript)

**Three regex patterns extract addresses:**

1. **Block Pattern**: "100 block of Sears Ave"
   - Pattern: `(\d+)\s+block\s+of\s+([^–\n]+?)(?=\s*–|\s*\n|$)`
   - Example: "100 block of Sears Ave, Louisville, KY"

2. **Intersection Pattern**: "30th Street and Market Street"
   - Pattern: `([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Street|St|Avenue|Ave|...))\s+and\s+(...)`
   - Example: "30th Street and Market Street, Louisville, KY"

3. **Full Address Pattern**: "4512 Tray Place"
   - Pattern: `\b(\d+)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Place|Street|...))\b`
   - Example: "4512 Tray Place, Louisville, KY"

#### 1.2 Address Normalization (Cleaning)

Before geocoding, addresses are normalized to fix OCR/extraction errors:

**Patterns Fixed:**
- `\bat(\d{2,3})\b` → `I-\1` (e.g., "at65" → "I-65")
- `\b([A-Z])\s+\1\b` → `\1` (e.g., "W W W Cardinal" → "W Cardinal")
- Multiple spaces normalized
- Trailing periods and extra context removed
- "near", "at", "adjacent to" phrases cleaned up

**Failure Patterns Filtered:**
- Empty addresses
- "ground plane", "mile marker"
- "Bravo Papa" (police phonetic codes)
- "an unspecified location"
- Malformed blocks: `^\d+\s+and\s+\d+\s+block\s+of\s*$`

#### 1.3 Geocoding Process with Fallback Strategies

**File:** `scripts/geocode_addresses.py` (lines 264-311)

The system uses **5-tier fallback strategy** with Nominatim OpenStreetMap API:

```python
Strategy 1: Original Address
  ↓ if fails
Strategy 2: Cleaned Address (remove extra text)
  ↓ if fails
Strategy 3: Highway Format (e.g., "Interstate 64" instead of "I-64")
  ↓ if fails
Strategy 4: Landmark-Based (extract "near", "at" location)
  ↓ if fails
Strategy 5: Intersection Format ("&" instead of "and")
  ↓ if fails
Result: Store as NULL to avoid retrying
```

**Code Details:**
- Service: Nominatim OpenStreetMap API
- Endpoint: `https://nominatim.openstreetmap.org/search?format=json&q={address}&limit=1`
- User-Agent: "Derby City Watch Event Map"
- Rate Limit: 1 request/second (enforced between requests)
- Timeout: 10 seconds per request
- Returns: `{lat: float, lng: float}` or `null`

### Caching Strategy (3-Layer)

**File:** `_layouts/map.html` (lines 369-405)

1. **Server-Side Cache** (`_data/geocoded_addresses.yml`)
   - Pre-computed during GitHub Actions build
   - Loaded instantly on page load
   - ~3,056 addresses with 37.76% success rate (as of 2025-11-18)

2. **Browser Cache** (`localStorage`)
   - Stores new geocodes from user's browser
   - Key: `derby_city_watch_geocode_cache`
   - Includes version number to invalidate on updates

3. **Live Geocoding** (Nominatim API)
   - Only for addresses not in caches
   - Respects rate limits (1/second)
   - Saves results to localStorage

**Code:** Lines 376-405 show merge logic
```javascript
let geocodeCache = { ...serverGeocodeData, ...getGeocodeCache() };
```

---

## 2. PLOTTING ON MAPS

### Map Technology Stack

**File:** `_layouts/map.html`

- **Library:** Leaflet.js v1.9.4
- **Tile Provider:** OpenStreetMap
- **Map Center:** Louisville, KY (38.2527°N, -85.7585°W)
- **Default Zoom:** 12

### Marker System

#### 2.1 Marker Colors (Lines 342-367)

Three categories based on event type detection:

1. **Red Markers** - Fire & Rescue events
   - Keywords: "fire", "structure fire", "brush fire", "smoke", "alarm fire", "vehicle fire"
   
2. **Yellow Markers** - Medical events
   - Keywords: "medical", "ems", "ambulance", "overdose", "cardiac", "stroke", "injury", "injured", "sick", "mental health", "crisis", "suicide", "unconscious", "breathing", "chest pain", "seizure", "fall victim"
   
3. **Blue Markers** - Police events (default)
   - Everything else: suspicious activity, burglary, assault, traffic, etc.

#### 2.2 Location Grouping (Lines 662-678)

Multiple events at the same location are **grouped together**:

```javascript
function addEventToLocationGroup(event, address, coords) {
  const locationKey = `${coords.lat},${coords.lng}`;
  // All events at same coordinates displayed on one marker
}
```

**Behavior:**
- One marker per unique coordinate
- Multiple events shown in popup
- Most recent event determines marker color
- All events sorted by date (newest first)

#### 2.3 Popup Content (Lines 700-728)

Popup shows:
- Location address (bold header)
- Count of events if multiple
- For each event:
  - Event type (extracted from content)
  - Time (if available)
  - Date
  - Description (2-3 lines, ~250 chars)
  - Link to full report

**Excluded Phrases** (lines 617-624):
```javascript
const excludePhrases = [
  'we will post our full 24-hour summary',
  'look out for one another',
  'stay safe',
  'stay vigilant',
  'errors in transcription or interpretation may occur',
  'information provided is for community awareness'
];
```

### Filtering & Display (Lines 894-930)

**Date Range Filter:**
- Default: Yesterday to today (24-hour window)
- User can customize start and end dates
- String comparison on YYYY-MM-DD format
- "Show All" button resets to all data

**Stats Display:**
- Shows: "Showing: X of Y locations"
- Updates when markers added/removed
- Updated after each geocoding result

---

## 3. WHAT PREVENTS GEOCODING/PLOTTING

### Current Failure Rate: **62.24%** (1,902 of 3,056 addresses)

**File:** `geocoding_success_report.md`

### Failure Pattern Analysis

| Pattern | Count | % of Failures | Issue |
|---------|-------|---------------|----|
| **Contains location qualifiers (near/at)** | 910 | 47.8% | "100 Crop St, near Croft Ct..." |
| **Incomplete/vague address** | 293 | 15.4% | Single street name, incomplete numbers |
| **Other/Unknown** | 290 | 15.2% | Unclassified extraction errors |
| **Intersection format** | 229 | 12.0% | "Street and Street" format issues |
| **Contains extra sentences/context** | 178 | 9.4% | "100 Broad St. Officers dispatched..." |
| **Police phonetic codes** | 2 | 0.1% | "Bravo Papa X-Ray Romeo" |

### Specific Failure Scenarios

#### 3.1 Address with Extra Text (Most Common)

**Source Text:**
```
"100 Crop St, near Croft Ct. The activation indicated that 
one round had been discharged."
```

**Extracted Address:**
```
"100 Crop St, near Croft Ct. The activation indicated that 
one round had been discharged., Louisville, KY"
```

**Why it fails:**
- Nominatim doesn't understand extra sentences
- "near Croft Ct" makes address ambiguous
- Extra context confuses the API

**Geocoding attempt:**
- Strategy 2 removes some extra text with `address.split('.')[0]`
- But still contains "near Croft Ct"
- Nominatim returns no results

#### 3.2 Highway Addresses

**Examples:** "100 I 64 East", "1000 I-71 South"

**Why it fails:**
- Initial format not standard
- Nominatim expects "Interstate 64, Louisville, KY"
- Handled by Strategy 3: `format_highway_address()` (lines 188-206)
- But some still fail if format is unusual

#### 3.3 Intersections

**Example:** "Zorn Avenue and Country Club Road"

**Why it fails:**
- Nominatim struggles with "and" format
- Strategy 5 tries "&" instead (line 301-307)
- But many still don't have unique coordinates
- Two streets intersect at a point, hard for API

#### 3.4 Incomplete Addresses

**Examples:**
- "100 Adam Rue" (street name may be missing suffix like "Street")
- "100 E W Kingston Ave" (corrupted extraction: "E W" = East/West?)
- "100 East Centennial Walk" (incomplete)

**Why it fails:**
- Nominatim requires full street names
- Missing type: "Avenue", "Street", "Road", etc.
- Ambiguous prefixes

#### 3.5 Landmark-Based Addresses

**Example:** "100 River Rd at Joe's Crab Shack, Louisville, KY"

**How it's handled:**
- Strategy 4 extracts: "Joe's Crab Shack, Louisville, KY"
- Geocodes the landmark instead
- Works for well-known businesses
- Fails for obscure/closed businesses

#### 3.6 Police Phonetic Codes

**Example:** "100 Bravo Papa X-Ray Romeo"

**Why it fails:**
- Phonetic alphabet confusion in extraction
- Not actual street names
- Filtered by `clean_address()` on line 177-184
- Returns empty string → not geocoded

#### 3.7 Duplicate Addresses Confusing the Cache

**Example:**
```yaml
100 Indian Legends Dr, Louisville, KY:
  lat: 38.294999
  lng: -85.5519612
  
100 Indian Legends Dr. Responding units were assigned to 
manage the scene and clear the roadway., Louisville, KY:
  null
```

**Issue:**
- Same address with different extraction variations
- Second version includes extra text
- Stored as separate cache entries
- First geocodes, second fails
- Appears as two separate cache keys

### Missing Address Prevention Points

#### 3.8 Daily Digest Post Exclusion (Line 111-112)

**File:** `scripts/geocode_addresses.py`

```python
# Skip daily-digest posts
if 'daily-digest' in content:
    continue
```

**Map JavaScript** (line 286-297):
```javascript
{% unless post.categories contains 'daily-digest' %}
  // Add to map
{% endunless %}
```

**Effect:** Daily digest posts completely excluded from:
- Address extraction
- Geocoding
- Map display

#### 3.9 Addresses with NULL Cache Values

**File:** `_data/geocoded_addresses.yml`

Addresses that failed are stored as:
```yaml
100 Adam Rue, Louisville, KY: null
100 Colonial Oaks Ct near South 1st Street, Louisville, KY: null
```

**Map behavior** (lines 812-817):
```javascript
allItems.forEach(item => {
  if (geocodeCache[item.address]) {
    // Has coordinates (success or being processed)
  } else {
    // Not in cache - will attempt live geocoding
  }
});
```

**Result:** If `null` is in cache, marker is not created

---

## 4. GEOCODING DATA FILES

### Location: `/home/user/Louisville/_data/`

#### 4.1 `geocoded_addresses.yml` (319KB, 7,632 lines)

**Structure:**
```yaml
address_string, Louisville, KY:
  lat: 38.xxxx
  lng: -85.xxxx
```

Or for failed addresses:
```yaml
address_string, Louisville, KY: null
```

**Statistics:**
- Total lines: 7,632
- Total addresses: 3,056
- Successfully geocoded: 1,154 (37.76%)
- Failed: 1,902 (62.24%)

**Format:** YAML
**Generated by:** `scripts/geocode_addresses.py`
**Loaded by:** `_layouts/map.html` line 370

#### 4.2 `geocoding_success_metrics.yml` (43KB)

**Structure:**
```yaml
history:
  - timestamp: '2025-11-18T22:14:22...'
    total_addresses: 3056
    successful: 1154
    failed: 1902
    success_rate: 37.76
    failure_rate: 62.24
    failure_patterns:
      Contains location qualifiers (near/at): 910
      Incomplete/vague address: 293
      ...
    batch_success_rate: 0.00
    batch_new_addresses: 2
    batch_new_successes: 0
  - timestamp: ...
```

**Purpose:** Historical tracking of geocoding improvements

**Generated by:** `scripts/track_geocoding_success.py`

---

## 5. GEOCODING SCRIPTS & CONFIGURATION

### Script Files

#### 5.1 `scripts/geocode_addresses.py` (391 lines)

**Main Script - Runs on every new post**

Key functions:
- `extract_addresses_from_content()` - Uses 3 regex patterns
- `read_all_posts()` - Scans all `_posts/` files
- `load_geocode_cache()` - Reads YAML cache
- `save_geocode_cache()` - Writes YAML cache
- `clean_address()` - Removes extra text and fixes errors
- `format_highway_address()` - Converts highway notation
- `extract_landmark()` - Finds "near/at" landmarks
- `try_geocode_query()` - Single Nominatim API call
- `geocode_address()` - 5-tier fallback strategy
- `main()` - Orchestrates the process

**Rate Limiting:**
```python
RATE_LIMIT_DELAY = 1.0  # seconds
time.sleep(RATE_LIMIT_DELAY)
```

**Automation:**
- Triggered by `.github/workflows/geocode-addresses.yml`
- Runs on push to `_posts/**/*.md`
- Commits results automatically

#### 5.2 `scripts/retry_failed_geocodes.py` (88 lines)

**Manual re-attempt of failed addresses**

- Loads cache
- Finds addresses with `null` values
- Re-geocodes with improved strategies
- Prompts user confirmation (rate limiting warning)
- Saves progress every 50 addresses

**Usage:**
```bash
python scripts/retry_failed_geocodes.py
```

#### 5.3 `scripts/track_geocoding_success.py` (327 lines)

**Tracks metrics and generates reports**

Functions:
- `analyze_addresses()` - Calculates success rates
- `load_metrics_history()` - Reads historical data
- `calculate_improvements()` - Batch vs cumulative metrics
- `generate_report()` - Creates markdown report
- `main()` - Generates `geocoding_success_report.md`

**Output:**
- `geocoding_success_report.md` - Markdown report with trends
- `geocoding_success_metrics.yml` - Historical data

**Generated:** Runs as part of main geocoding workflow (line 371-388 in geocode_addresses.py)

#### 5.4 `scripts/test_sample_improvements.py` (48 lines)

**Tests improvements on sample failed addresses**

Sample test cases:
```python
"100 Indian Legends Dr. Responding units were assigned...",
"100 North 45th Street",  # Missing space
"100 Colonial Oaks Ct near South 1st Street",
"100 River Rd at Joe's Crab Shack",
"100 I 64 East",  # Highway
"Zorn Avenue and Country Club Road",  # Intersection
```

---

## 6. FILTERING LOGIC

### What Gets EXCLUDED from Maps

#### 6.1 Daily Digest Posts

**Python Filter** (`geocode_addresses.py`, line 111-112):
```python
if 'daily-digest' in content:
    continue  # Skip this post entirely
```

**JavaScript Filter** (`map.html`, line 286):
```javascript
{% unless post.categories contains 'daily-digest' %}
  {
    title: ...,
    date: ...,
    // Only included if NOT daily-digest
  }
{% endunless %}
```

**Effect:** Posts categorized with `daily-digest` are:
- NOT extracted for addresses
- NOT displayed on map
- NOT counted in statistics

#### 6.2 Addresses with NULL Geocoding Results

**Map JavaScript** (lines 841-847):
```javascript
cachedItems.forEach(item => {
  const coords = geocodeCache[item.address];
  if (coords) {
    // Only add if coords exist (not null)
    addEventToLocationGroup(item.event, item.address, coords);
  }
});
```

**Result:**
- Addresses geocoded as `null` create NO marker
- Event still exists in post but invisible on map

#### 6.3 Date Range Filtering

**User-Controlled Filter** (lines 895-930):
```javascript
function applyFilters() {
  const startDate = startDateInput.value;  // YYYY-MM-DD
  const endDate = endDateInput.value;      // YYYY-MM-DD

  markers.forEach(marker => {
    if (startDate && event.date < startDate) {
      markerLayer.removeLayer(marker);
    }
    if (endDate && event.date > endDate) {
      markerLayer.removeLayer(marker);
    }
  });
}
```

**Default:** Yesterday to today (24 hours)

#### 6.4 Generic Text Exclusion from Popups

**Excluded Phrases** (lines 617-624):
```javascript
const excludePhrases = [
  'we will post our full 24-hour summary',
  'look out for one another',
  'stay safe',
  'stay vigilant',
  'errors in transcription or interpretation may occur',
  'information provided is for community awareness'
];
```

**Effect:** These generic closing lines don't appear in marker popups, only specific event descriptions are shown.

---

## 7. COMMON FAILURE POINTS SUMMARY

### High-Level Failure Modes

| Failure Mode | Frequency | Root Cause | Can Be Fixed |
|-------------|-----------|-----------|-------------|
| Location qualifiers (near/at) | 910 (47.8%) | OCR extraction includes location context | Yes - better cleaning |
| Incomplete addresses | 293 (15.4%) | Extraction regex incomplete | Yes - improve regex |
| Intersection format | 229 (12.0%) | Nominatim struggles with "and" | Partially - try "&" format |
| Extra sentences/context | 178 (9.4%) | Text after address not removed | Yes - better sentence detection |
| Unknown/Other | 290 (15.2%) | Unclassified errors | Maybe - need analysis |
| Police codes | 2 (0.1%) | Phonetic alphabet mistaken for address | Yes - filter them |

### Quick Fix Opportunities

**Highest Impact:**
1. **Location qualifiers** (910 failures)
   - Remove everything after "near", "at", "adjacent to"
   - Try landmark-based geocoding if available
   - Code exists in `extract_landmark()` but may need tweaking

2. **Extra sentences** (178 failures)
   - Improve sentence boundary detection
   - Use period + capital letter as split point
   - Code exists in `clean_address()` but incomplete

3. **Intersection format** (229 failures)
   - Could try different geocoding services
   - Nominatim struggles with intersections inherently
   - Alternative: Use center of two street endpoints

### Automation

The system has **automatic retry capability** (GitHub Actions):
- New posts trigger geocoding workflow
- Only new addresses are processed
- Failed addresses stored as `null`
- Manual retry script available

**Next Steps for Improvement:**
- Run `scripts/retry_failed_geocodes.py` to attempt failed addresses with improved strategies
- Or manually delete `_data/geocoded_addresses.yml` and re-geocode everything
- Or improve regex patterns and strategies in `geocode_addresses.py`

---

## 8. WORKFLOW AUTOMATION

### GitHub Actions Workflow

**File:** `.github/workflows/geocode-addresses.yml`

**Trigger:** Push to `_posts/**/*.md` or manual workflow_dispatch

**Steps:**
1. Wait 60 seconds for pages deployment
2. Checkout repo (full history)
3. Set up Python 3.x
4. Install PyYAML
5. Run `scripts/geocode_addresses.py`
6. Check for changes in:
   - `_data/geocoded_addresses.yml`
   - `_data/geocoding_success_metrics.yml`
   - `geocoding_success_report.md`
7. If changed: Commit and push
8. Auto-commit message: "Auto-update geocoded addresses and success metrics [skip ci]"

**Concurrency:**
- Only one geocoding run at a time
- Prevents conflicts from rapid posts
- New runs queue instead of canceling

---

## CONCLUSION

The system is a robust, automated geocoding pipeline with:

✅ **Strengths:**
- Multi-layer caching (server, browser, live)
- 5-tier fallback strategy for resilience
- Automatic retry capability
- Historical tracking and reporting
- Proper rate limiting (1 req/sec)
- Duplicate address detection
- Daily digest exclusion

⚠️ **Limitations:**
- 62% failure rate, mainly from:
  - Location qualifiers (47.8%)
  - Incomplete extraction (15.4%)
  - Intersection format issues (12.0%)
- Nominatim API limitations for edge cases
- No reverse geocoding for vague locations
- No manual address correction interface

🎯 **Improvement Opportunities:**
1. Enhanced cleaning of "near/at" phrases
2. Better intersection geocoding
3. Landmark extraction improvement
4. Machine learning for failed address classification
5. User-contributed coordinate corrections

