# File Reference Guide

## Key Files for Geocoding & Mapping

### Python Geocoding Scripts
- `/home/user/Louisville/scripts/geocode_addresses.py` (391 lines)
  - Main geocoding script with 5-tier fallback strategy
  - Extracts addresses, cleans them, geocodes with Nominatim
  
- `/home/user/Louisville/scripts/retry_failed_geocodes.py` (88 lines)
  - Manual retry script for failed addresses
  
- `/home/user/Louisville/scripts/track_geocoding_success.py` (327 lines)
  - Tracks metrics and generates reports
  
- `/home/user/Louisville/scripts/test_sample_improvements.py` (48 lines)
  - Tests geocoding on sample failed addresses

### Data Files
- `/home/user/Louisville/_data/geocoded_addresses.yml` (7,632 lines, 319KB)
  - Cache of all geocoded addresses and their coordinates
  - Format: YAML with lat/lng or null
  - 3,056 total addresses: 1,154 successful (37.76%), 1,902 failed (62.24%)
  
- `/home/user/Louisville/_data/geocoding_success_metrics.yml` (43KB)
  - Historical metrics tracking improvements over time
  - Contains failure pattern analysis

### Report Files
- `/home/user/Louisville/geocoding_success_report.md`
  - Generated markdown report with current status
  - Shows failure patterns and recommendations
  - Updated automatically after each geocoding run

### HTML/JavaScript Map Layout
- `/home/user/Louisville/_layouts/map.html` (1,023 lines)
  - Interactive Leaflet.js map with all plotting logic
  - Address extraction via JavaScript
  - Marker creation, grouping, and filtering
  - Lines 284-299: eventsData from Jekyll posts
  - Lines 369-405: Caching strategy (3-layer)
  - Lines 342-367: Marker colors and icons
  - Lines 662-678: Location grouping logic
  - Lines 700-728: Popup content generation
  - Lines 895-930: Date filtering

### Configuration Files
- `/home/user/Louisville/_config.yml`
  - Jekyll site configuration
  - Excludes `scripts/` and `.github/` from build
  
- `/home/user/Louisville/.github/workflows/geocode-addresses.yml` (72 lines)
  - GitHub Actions automation
  - Triggers on new posts or manual workflow_dispatch
  - Runs Python geocoding script
  - Auto-commits results

### Post Templates
- `/home/user/Louisville/_posts/*.md`
  - Scanner update posts with addresses in text
  - Some tagged with `daily-digest` category (excluded from map)
  - Contains event descriptions with geographic references

---

## Key Code Sections

### Address Extraction Patterns
**File:** `geocode_addresses.py` lines 60-90 (Python) and `map.html` lines 305-339 (JavaScript)

Three regex patterns:
1. Block: `(\d+)\s+block\s+of\s+([^–\n]+?)...`
2. Intersection: `...\s+and\s+...` 
3. Full address: `\b(\d+)\s+([A-Z][a-z]+...)`

### Geocoding Fallback Chain
**File:** `geocode_addresses.py` lines 264-311

```
Strategy 1: Original Address
  → Strategy 2: Cleaned (remove extra text)
    → Strategy 3: Highway format (I-65 → Interstate 65)
      → Strategy 4: Landmark extraction (near/at location)
        → Strategy 5: Intersection format (and → &)
          → NULL (store as failed)
```

### Caching Implementation
**Server-side:** `_data/geocoded_addresses.yml` (YAML format)
**Browser-side:** `localStorage` with key `derby_city_watch_geocode_cache`
**Merge:** `_layouts/map.html` line 404: `{...serverGeocodeData, ...getGeocodeCache()}`

### Filtering Logic
- **Daily Digest:** `scripts/geocode_addresses.py` line 111 and `map.html` line 286
- **Failed Geocodes:** `map.html` lines 812-817 checks if coords exist
- **Date Range:** `map.html` lines 895-930 applies user-selected filters
- **Popup Text:** `map.html` lines 617-624 excludes generic phrases

---

## Statistics from November 18, 2025

- **Total Addresses Extracted:** 3,056
- **Successfully Geocoded:** 1,154 (37.76%)
- **Failed Geocoding:** 1,902 (62.24%)
- **Geocoding Data File Size:** 319 KB
- **Number of Recent Commits:** Multiple auto-updates per day

**Top Failure Patterns:**
1. Location qualifiers (near/at): 910 failures (47.8%)
2. Incomplete/vague address: 293 failures (15.4%)
3. Other/Unknown: 290 failures (15.2%)
4. Intersection format: 229 failures (12.0%)
5. Extra sentences/context: 178 failures (9.4%)
6. Police codes: 2 failures (0.1%)

---

## Execution Flow Diagram

```
User visits /map/ page
    ↓
Jekyll renders map.html layout
    ↓
JavaScript loads:
├─ Site data: site.data.geocoded_addresses (server-side cache)
├─ Local storage: browser cache
└─ eventsData: all posts from Jekyll (except daily-digest)
    ↓
extractAddresses() on each post (3 regex patterns)
    ↓
For each extracted address:
├─ Check server cache → if found, use coordinates
├─ Check browser cache → if found, use coordinates
└─ Call geocodeAddress() via Nominatim API (rate limited 1/sec)
    ↓
addEventToLocationGroup() - group by coordinates
    ↓
createMarkerForLocation() - one marker per unique location
    ↓
Detect category (fire/medical/police) from event content
    ↓
Create popup with event details and link
    ↓
Apply date filters (default: last 24 hours)
    ↓
Display on map with legend and stats
```

**Automation Flow:**

```
New post committed to _posts/
    ↓
GitHub Actions triggered (geocode-addresses.yml)
    ↓
1. Checkout repo
2. Setup Python + PyYAML
3. Run geocode_addresses.py
    ├─ read_all_posts()
    ├─ extract_addresses_from_content()
    ├─ load_geocode_cache()
    ├─ For each new address:
    │  └─ geocode_address() with 5-tier fallback
    └─ save_geocode_cache()
4. Run track_geocoding_success.py
    ├─ Analyze addresses
    └─ Generate report.md
5. Check for changes
6. If changed: Commit and push
    ↓
GitHub Pages rebuilds
    ↓
Live map updates instantly (new addresses already in cache)
```

