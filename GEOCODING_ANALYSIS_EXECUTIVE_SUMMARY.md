# Executive Summary: Derby City Watch Geocoding & Mapping System

## What This System Does

The Derby City Watch system automatically extracts addresses from public safety event posts and plots them on an interactive map. When a new event post is created:

1. **Python script** extracts addresses using regex patterns
2. **Nominatim API** (OpenStreetMap) converts addresses to coordinates
3. **Results cached** in YAML file for instant map loading
4. **JavaScript map** displays markers with color coding by event type
5. **Users filter** by date range to see recent events

---

## Current Performance (Nov 18, 2025)

- **3,056 unique addresses extracted**
- **1,154 successfully geocoded (37.76%)**
- **1,902 failed (62.24%)**
- **Cache size: 319 KB**
- **Map loads instantly** with pre-computed coordinates

---

## How It Works: The Pipeline

### 1. Address Extraction Phase

Three regex patterns capture different address formats:

| Pattern | Example | Success Rate |
|---------|---------|--------------|
| "Block of" format | "100 block of Sears Ave" | Good |
| Intersection format | "30th and Market" | Medium (many fail to geocode) |
| Full address | "4512 Tray Place" | Good |

**Problem:** Extraction sometimes includes extra text from OCR errors

### 2. Geocoding Phase (5-Tier Fallback)

Each address tries strategies in sequence:

1. Original address → Nominatim API
2. Cleaned address (remove extra text)
3. Highway format (I-65 → Interstate 65)
4. Landmark extraction (geocode "Joe's Crab Shack" if "at Joe's Crab Shack")
5. Intersection format (try "&" instead of "and")

If all fail → Stored as `null` (never appears on map)

**Rate Limiting:** 1 request per second (OpenStreetMap policy)

### 3. Caching Strategy (3-Layer)

```
Server-Side Cache          Browser Cache          Live Geocoding
(instant load)   ────→    (saved sessions)  ────→  (rate-limited)
   ~/.yml                    localStorage          Nominatim API
   1,154 coords                new coords               fallback
```

### 4. Map Display Phase

- **Colors:** Red (fire), Yellow (medical), Blue (police)
- **Grouping:** Multiple events at same location = 1 marker
- **Filtering:** Date range (default: last 24 hours)
- **Popups:** Event details + full report link

---

## Why 62% of Addresses Fail

### Failure Breakdown

```
Location qualifiers (47.8%)  ████████████████████  910 addresses
  "100 Crop St, near Croft Ct. The activation indicated..."
  
Incomplete/vague (15.4%)     ████████              293 addresses
  "100 E W Kingston Ave" (corrupted extraction)
  "Zorn Avenue" (no number)
  
Unknown/Other (15.2%)        ████████              290 addresses
  Uncategorized extraction errors
  
Intersection format (12.0%)  ██████                229 addresses
  Nominatim can't geocode "Street and Street" without number
  
Extra text/sentences (9.4%)  █████                 178 addresses
  "100 Breckenridge Ln. Units responded to..."
  
Police codes (0.1%)          -                       2 addresses
  "100 Bravo Papa X-Ray Romeo" (phonetic alphabet)
```

### Root Causes

| Cause | Primary Impact | Why It Happens |
|-------|---|---|
| **OCR Over-Capture** | 47.8% | Police scanner text includes location context ("near Croft Ct") |
| **Regex Limitations** | 15.4% | Extraction patterns can't distinguish "E W" vs "East West" |
| **Nominatim Limitations** | 12.0% | API doesn't handle intersections without a numeric address |
| **Sentence Boundaries** | 9.4% | "100 Broad St. Officers arrived..." needs better splitting |
| **Malformed Input** | 15.2% | Various edge cases not specifically handled |

---

## What Prevents Geocoding/Plotting

### Automatic Exclusions

1. **Daily Digest Posts**
   - Posts tagged with `daily-digest` category
   - Excluded at EXTRACTION stage (Python)
   - Excluded at DISPLAY stage (JavaScript)
   - Result: Zero addresses from these posts appear on map

2. **Addresses with NULL Results**
   - Stored in cache as `null`
   - JavaScript checks: `if (coords)` before creating marker
   - Result: Failed addresses create no marker (but post still exists)

3. **Failed Geocoding Attempts**
   - 5 strategies exhausted → returns None
   - Caching prevents re-trying (stored as null)
   - Manual retry needed: `python scripts/retry_failed_geocodes.py`

### User-Controlled Filtering

- **Date range:** Default 24 hours (yesterday to today)
- **Manual show/hide:** Via "Show All" button or date inputs
- **Browser cache:** Clearing localStorage erases new address geocodes

---

## Key Files & Their Roles

### Python Scripts
```
geocode_addresses.py       Main script - runs on new posts via GitHub Actions
retry_failed_geocodes.py   Manual tool - re-attempt failed addresses
track_geocoding_success.py Metrics tracker - generates reports
test_sample_improvements.py Testing utility
```

### Data Files
```
_data/geocoded_addresses.yml      3,056 addresses with lat/lng or null
_data/geocoding_success_metrics.yml Historical tracking (improvements over time)
geocoding_success_report.md        Human-readable status report
```

### HTML/JavaScript
```
_layouts/map.html          1,023 lines - entire map implementation
  - Address extraction (JavaScript regex)
  - Marker creation and grouping
  - Date filtering
  - Popup generation
```

### Automation
```
.github/workflows/geocode-addresses.yml  Triggers on new posts
  - Runs Python geocoding
  - Commits results
  - Triggers GitHub Pages rebuild
```

---

## Common Failure Points (Examples)

### Example 1: Location Qualifier Failure

**Text in post:**
```
"100 Crop St, near Croft Ct. The activation indicated that one round had been discharged."
```

**Extracted address:** `"100 Crop St, near Croft Ct. The activation indicated that one round had been discharged., Louisville, KY"`

**Geocoding attempts:**
1. Original (full text) → FAILS
2. Cleaned (period split) → "100 Crop St, near Croft Ct" → FAILS
3. Highway format → N/A
4. Landmark ("Croft Ct") → FAILS
5. Intersection format → N/A

**Result:** `null` in cache

---

### Example 2: Corrupted Extraction

**Text in post:** "East 45th Street"

**Extracted as:** "E W Kingston Ave" (OCR/parsing error)

**Geocoding attempts:**
1. Original "100 E W Kingston Ave" → FAILS (not recognized)
2. Cleaned → Same as original
3-5. All fail

**Result:** `null` in cache

---

### Example 3: Intersection Without Number

**Text:** "30th Street and Market Street"

**Extracted:** `"30th Street and Market Street, Louisville, KY"`

**Geocoding attempts:**
1. Original → FAILS (no specific point)
2. Cleaned → FAILS
3. Highway format → N/A
4. Landmark → N/A
5. With "&" → `"30th Street & Market Street, Louisville, KY"` → FAILS

**Why:** Nominatim needs either a house number ("123 30th and Market") or specific intersection query.

**Result:** `null` in cache

---

## Improvement Opportunities

### Quick Wins (Could fix ~1,100+ failures)

**1. Better "near/at" handling** (910 failures)
   - Pre-clean location qualifiers BEFORE period split
   - Use regex: `r',?\s+(near|at|adjacent\s+to)\s+.+?(?=\.|,|$)'`

**2. Improved sentence detection** (178 failures)
   - Split on period + capital letter pattern
   - Not just first period

**3. Address validation** (290 failures)
   - Query result validation
   - Reverse-geocode to verify address type

### Medium Complexity (Could fix ~229 failures)

**4. Better intersection handling**
   - Query each street separately, find centroid
   - Alternative geocoding service (Google, Bing)
   - Extract building addresses from intersection descriptions

**5. Corrupted extraction fix** (293 failures)
   - Better regex for "E W" vs "East West"
   - Phonetic code detection (already partially done)
   - City directory lookup for validation

### Automation Improvements

**6. Daily metric tracking** (already implemented)
   - `geocoding_success_metrics.yml` has history
   - `geocoding_success_report.md` auto-generated

**7. Automatic retry mechanism** (already available)
   - Run `retry_failed_geocodes.py` periodically
   - Or when new strategies implemented

---

## System Strengths

- **Robust caching** - 3-layer strategy ensures instant map loads
- **Rate-limit compliant** - Respects Nominatim usage policy
- **Automated** - GitHub Actions handles new posts automatically
- **Fallback strategies** - Multiple approaches to geocoding
- **Data quality tracking** - Historical metrics and reports
- **Duplicate handling** - Doesn't re-geocode known addresses
- **Daily digest exclusion** - Prevents noise from summaries

---

## System Limitations

- **Low success rate** - 62% failure due to data quality and API limitations
- **No manual correction** - Users can't fix bad addresses
- **No reverse-geocoding** - Can't resolve vague locations
- **Single API** - Nominatim limitations (intersections, edge cases)
- **No ML/NLP** - Simple regex-based extraction
- **Browser cache** - Large list of addresses could exceed storage limits

---

## How to Run Improvements

### Option 1: Retry Failed Addresses
```bash
cd /home/user/Louisville
python scripts/retry_failed_geocodes.py
# Attempts 1,902 failed addresses with current strategies
# Takes ~30 minutes (1 request/second)
```

### Option 2: Implement Better Strategies
```bash
# Edit scripts/geocode_addresses.py
# Improve clean_address() function (lines 144-186)
# Run on all posts:
rm _data/geocoded_addresses.yml
python scripts/geocode_addresses.py
# ~50 minutes for full re-geocoding
```

### Option 3: Manual Fixes
- Edit `_data/geocoded_addresses.yml` directly
- Add lat/lng for specific addresses
- JSON format: `address: {lat: #, lng: #}`

---

## File Locations Summary

```
/home/user/Louisville/
├── scripts/
│   ├── geocode_addresses.py           (main script)
│   ├── retry_failed_geocodes.py       (manual retry)
│   ├── track_geocoding_success.py     (metrics)
│   └── test_sample_improvements.py    (testing)
├── _data/
│   ├── geocoded_addresses.yml         (cache: 3,056 addresses)
│   └── geocoding_success_metrics.yml  (history)
├── _layouts/
│   └── map.html                       (1,023 line map code)
├── .github/workflows/
│   └── geocode-addresses.yml          (automation)
├── geocoding_success_report.md        (status report)
└── _posts/                            (source data)
    └── *.md                           (event posts)
```

---

## Conclusion

The Derby City Watch geocoding system is a well-engineered, automated solution with:

✅ **Working:** Caching, filtering, automation, metrics tracking  
⚠️ **Challenge:** 62% failure rate from data quality and API limitations  
🎯 **Opportunity:** Incremental improvements could reach 80%+ success rate

The main blockers are:
1. OCR errors in address extraction (47.8% of failures)
2. Nominatim API limitations (12% of failures)
3. Incomplete extraction patterns (15.4% of failures)

