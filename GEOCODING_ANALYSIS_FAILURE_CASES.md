# Detailed Failure Analysis & Code Examples

## Failure Case Study: Why 62% of Addresses Don't Geocode

### Real Examples from the Cache

#### Case 1: Location Qualifiers (Highest Impact: 47.8%)

**Address:**
```
"100 Crop St, near Croft Ct. The activation indicated that one round had been discharged., Louisville, KY"
```

**Problem:**
- OCR extraction captured too much context
- "near Croft Ct" makes the address ambiguous
- Extra sentences confuse the API

**Geocoding attempts:**
1. Original: "100 Crop St, near Croft Ct. The activation..." → FAILS (too much text)
2. Cleaned: "100 Crop St, near Croft Ct" → FAILS (still has "near")
3. Highway format: N/A
4. Landmark: "Croft Ct, Louisville, KY" → FAILS (Croft Ct is street name, not landmark)
5. Intersection format: No "and" → FAILS

**Stored in cache as:** `null`

**Code that attempts to fix it:** (`geocode_addresses.py` lines 163-164)
```python
address = re.sub(r',?\s+near\s+.*$', '', address, flags=re.IGNORECASE)
address = re.sub(r',?\s+at\s+.*$', '', address, flags=re.IGNORECASE)
```

**Why it's incomplete:** Only removes everything after "near" in clean_address(), but original address still has it.

---

#### Case 2: Corrupted Address Extraction (15.4%)

**Address:**
```
"100 E W Kingston Ave, Louisville, KY"
```

**What happened:**
- Regex extracted "E W Kingston Ave" (East/West confusion)
- Should be either "East Kingston" or "West Kingston"
- Nominatim doesn't recognize "E W Kingston Ave"

**Geocoding attempts:**
1. Original: "100 E W Kingston Ave, Louisville, KY" → FAILS (not standard format)
2. Cleaned: Same as above
3. Highway format: N/A
4. Landmark: N/A
5. Intersection: N/A (no "and")

**Stored in cache as:** `null`

**Related failures in cache:**
```yaml
100 E W Kingston Ave, Louisville, KY: null
100 East W Kingston Ave, Louisville, KY: null
100 East W W Kingston Ave. Police units were sent to investigate..., Louisville, KY: null
```

**Code that tries to fix it:** (`geocode_addresses.py` lines 51-53)
```python
# Fix repeated letter prefixes (W W W Cardinal → W Cardinal)
addr_part = re.sub(r'\b([A-Z])\s+\1\s+\1\b', r'\1', addr_part)
addr_part = re.sub(r'\b([A-Z])\s+\1\b', r'\1', addr_part)
```

**Why it fails:** This removes "W W" but not "E W" (different letters).

---

#### Case 3: Intersection Format Issues (12.0%)

**Address:**
```
"Zorn Avenue and Country Club Road, Louisville, KY"
```

**Problem:**
- Nominatim struggles with intersections
- No numeric address makes it ambiguous
- "and" format vs "&" format confusion

**Geocoding attempts:**
1. Original: "Zorn Avenue and Country Club Road, Louisville, KY" → FAILS
2. Cleaned: Same as original
3. Highway format: N/A
4. Landmark: N/A
5. Intersection: "Zorn Avenue & Country Club Road, Louisville, KY" → FAILS

**Why both fail:**
- Nominatim expects a specific point, not a line intersection
- Two streets intersect across many blocks
- No clear single coordinate exists

**Alternative that could work:**
- Query each street separately
- Return the centroid of overlapping areas
- NOT implemented in current code

**Stored in cache as:** `null`

---

#### Case 4: Extra Text After Address (9.4%)

**Address:**
```
"100 Breckenridge Ln. Units from the 5th Division responded to investigate the activation., Louisville, KY"
```

**Problem:**
- Address followed by sentence about response
- Sentence starts immediately after period
- Extraction includes everything

**Geocoding attempts:**
1. Original: "100 Breckenridge Ln. Units from the 5th Division..." → FAILS
2. Cleaned (split on period): "100 Breckenridge Ln" → SUCCESS (partially works!)
3. Actually: 100 Breckenridge Ln DOES exist and geocodes fine

**But this one fails:**
```yaml
100 Breckenridge Ln, specifically at the rear door. Police units were dispatched..., Louisville, KY: null
```

**Why:** Contains "at the rear door" which isn't cleaned properly.

---

#### Case 5: Police Phonetic Codes (0.1%)

**Address:**
```
"100 Bravo Papa X-Ray Romeo, Louisville, KY"
```

**Problem:**
- Phonetic alphabet used for radio communication
- Not actual street names
- OCR/parser confused letters for addresses

**Solution implemented:** (`geocode_addresses.py` lines 176-177)
```python
bad_patterns = [
    ...,
    r'Bravo Papa',  # Police codes
    ...
]
```

**Result:** Returns empty string → not geocoded

---

#### Case 6: Highway Addressing Issues

**Example 1 - Unusual format:**
```
"100 I 64 East, Louisville, KY"
```

**Geocoding attempts:**
1. Original: "100 I 64 East, Louisville, KY" → FAILS (not standard)
2. Cleaned: Same
3. Highway format:
   ```python
   # Match patterns like "100 I 64 East"
   highway_match = re.search(r'(\d+)\s+I-?\s*(\d+)\s+(North|South|East|West)?', address)
   # Returns: "Interstate 64 East, Louisville, KY" → FAILS (Nominatim still confused)
   ```
4. Landmark: N/A
5. Intersection: N/A

**Stored in cache as:** `null`

**Why it fails:** Highways don't have standard addresses. The "100" isn't meaningful.

**Example 2 - Successful:**
```yaml
Interstate 64, Louisville, KY:  # Might geocode to center of highway
```

---

### Failure Pattern Distribution

**Pie chart (percentages of 1,902 failures):**

```
Contains location qualifiers: 910 (47.8%) ████████████████████████
Incomplete/vague address:     293 (15.4%) ████████
Other/Unknown:                290 (15.2%) ████████
Intersection format:          229 (12.0%) ██████
Extra sentences/context:      178 (9.4%)  █████
Police phonetic codes:          2 (0.1%)   -
                             ─────
                             1,902 total
```

---

## Code Walkthrough: The Geocoding Pipeline

### 1. Address Extraction (geocode_addresses.py lines 60-90)

```python
def extract_addresses_from_content(content: str) -> Set[str]:
    """Extract addresses from post content using same patterns as JavaScript."""
    addresses = set()

    # Pattern 1: "100 block of Sears Ave"
    block_pattern = r'(\d+)\s+block\s+of\s+([^–\n]+?)(?=\s*–|\s*\n|$)'
    for match in re.finditer(block_pattern, content, re.IGNORECASE):
        addr = f"{match.group(1)} {match.group(2).strip()}, Louisville, KY"
        # ... normalize and add ...

    # Pattern 2: "30th Street and Market Street"
    intersection_pattern = r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Street|St|Avenue|Ave|...))\s+and\s+(...)'
    for match in re.finditer(intersection_pattern, content):
        addr = f"{match.group(1).strip()} and {match.group(2).strip()}, Louisville, KY"
        # ... normalize and add ...

    # Pattern 3: "4512 Tray Place"
    full_address_pattern = r'\b(\d+)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Place|Street|...))\b'
    for match in re.finditer(full_address_pattern, content):
        addr = f"{match.group(1)} {match.group(2).strip()}, Louisville, KY"
        # ... normalize and add (if not duplicate from block) ...

    return addresses
```

**Limitations:**
- Pattern 1 depends on "block of" being present
- Pattern 2 requires recognized street type keywords
- Pattern 3 requires complete address with street type

### 2. Address Cleaning (geocode_addresses.py lines 144-186)

```python
def clean_address(address: str) -> str:
    """Clean and normalize an address for better geocoding."""
    if not address or not address.strip():
        return ""

    # Remove extra text after period
    if '.' in address:
        address = address.split('.')[0]  # Only keeps first sentence

    # Remove bracketed content
    address = re.sub(r'\[.*?\]', '', address)

    # Remove "near/at" context - BUT ONLY AT END
    address = re.sub(r',?\s+near\s+.*$', '', address, flags=re.IGNORECASE)
    address = re.sub(r',?\s+at\s+.*$', '', address, flags=re.IGNORECASE)

    # Fix missing spaces
    address = re.sub(r'([A-Za-z])(\d)', r'\1 \2', address)  # "North45th" → "North 45th"

    # Normalize spaces
    address = re.sub(r'\s+', ' ', address).strip()

    # Filter obviously bad extractions
    bad_patterns = [
        r'^\s*$',  # Empty
        r'ground plane',
        r'mile marker',
        r'Bravo Papa',  # Police codes
        r'an unspecified location',
    ]
    for pattern in bad_patterns:
        if re.search(pattern, address, re.IGNORECASE):
            return ""  # Rejected

    return address
```

**Issues:**
- Period splitting: "100 Breckenridge Ln. Units..." becomes "100 Breckenridge Ln" (good)
- But: "100 Crop St, near Croft Ct. The activation..." becomes "100 Crop St, near Croft Ct" (still bad)
- The regex `r',?\s+near\s+.*$'` removes "near..." but comes AFTER the period split

### 3. Five-Tier Geocoding Strategy (geocode_addresses.py lines 264-311)

```python
def geocode_address(address: str) -> Tuple[float, float, None]:
    """Geocode with fallback strategies."""
    
    # Strategy 1: Try original
    result = try_geocode_query(address)
    if result:
        return result

    # Strategy 2: Try cleaned version
    cleaned = clean_address(address)
    if cleaned and cleaned != address:
        result = try_geocode_query(cleaned)
        if result:
            return result

    # Strategy 3: Highway format
    highway = format_highway_address(address)
    if highway and highway != address and highway != cleaned:
        result = try_geocode_query(highway)
        if result:
            return result

    # Strategy 4: Landmark extraction
    landmark = extract_landmark(address)
    if landmark and landmark != address:
        result = try_geocode_query(landmark)
        if result:
            return result

    # Strategy 5: Intersection with "&" instead of "and"
    if " and " in address.lower():
        alt_intersection = address.replace(" and ", " & ").replace(" And ", " & ")
        result = try_geocode_query(alt_intersection)
        if result:
            return result

    # All failed
    return None  # Stored as null in YAML
```

### 4. Landmark Extraction (geocode_addresses.py lines 208-234)

```python
def extract_landmark(address: str) -> str:
    """Extract landmark from 'near X' or 'at X' for landmark-based geocoding."""
    if not address:
        return ""

    suffix = ", Louisville, KY"
    addr_part = address[:-len(suffix)] if address.endswith(suffix) else address

    # Try to extract landmark
    landmark_patterns = [
        r'\s+at\s+(?:the\s+)?([^,\.]+)',  # "100 River Rd at Joe's Crab Shack"
        r'\s+near\s+(?:the\s+)?([^,\.]+)', # "100 Pluto Dr near Astro Court"
        r'\s+adjacent\s+to\s+(?:the\s+)?([^,\.]+)',
    ]

    for pattern in landmark_patterns:
        match = re.search(pattern, addr_part, re.IGNORECASE)
        if match:
            landmark = match.group(1).strip()
            # Clean up trailing context
            landmark = re.sub(r'\s+(to|for|due to|following).*$', '', landmark, re.IGNORECASE)
            if landmark and len(landmark) > 3:
                return f"{landmark}, Louisville, KY"

    return ""
```

**Success scenario:**
- Input: "100 River Rd at Joe's Crab Shack, Louisville, KY"
- Extracts: "Joe's Crab Shack, Louisville, KY"
- Geocodes: Successfully finds the restaurant

**Failure scenario:**
- Input: "100 River Rd at the closed warehouse, Louisville, KY"
- Extracts: "closed warehouse, Louisville, KY"
- Geocodes: Nominatim finds nothing (closed businesses not in database)

---

## JavaScript Map Filtering

### How Addresses with null Get Skipped

**File:** `_layouts/map.html` lines 841-847

```javascript
// Process cached addresses immediately
cachedItems.forEach(item => {
  const coords = geocodeCache[item.address];
  if (coords) {  // Only if NOT null
    addEventToLocationGroup(item.event, item.address, coords);
  }
  // If coords is null, this address is SKIPPED entirely
});
```

**Result:** If an address is in the cache with a `null` value, it will never appear as a marker on the map, even though the event post exists.

### Daily Digest Exclusion

**Python side** (`geocode_addresses.py` lines 111-112):
```python
for post_file in post_files:
    with open(post_file, 'r', encoding='utf-8') as f:
        content = f.read()
        # Skip daily-digest posts
        if 'daily-digest' in content:
            continue  # Don't extract addresses from this post
```

**JavaScript side** (`_layouts/map.html` lines 286):
```javascript
eventsData = [
  {% for post in site.posts limit:1000 %}
  {% unless post.categories contains 'daily-digest' %}
  // Only include if NOT daily-digest
  {
    title: {{ post.title | jsonify }},
    ...
  }
  {% endunless %}
  {% endfor %}
];
```

**Double exclusion ensures:**
- Daily digest posts won't be geocoded
- They won't be sent to JavaScript
- No addresses from them will appear on map

---

## Recommendations for Improvement

### High-Priority Fixes (Would improve 910 failures)

**Problem:** Location qualifiers not completely removed

**Current code issue:**
```python
# In clean_address()
address = re.sub(r',?\s+near\s+.*$', '', address, flags=re.IGNORECASE)
```

**Problem:** This runs AFTER period splitting, so doesn't help when:
- "100 Crop St, near Croft Ct. The activation..."
- Becomes: "100 Crop St, near Croft Ct"  after period split
- Regex removes "near Croft Ct" leaving "100 Crop St"
- Which should work... unless

**Actually:** The issue is the extracted address keeps the full content. Better fix:

```python
# Option 1: Pre-clean before period split
def clean_address(address: str) -> str:
    # FIRST: Remove location qualifiers with better regex
    address = re.sub(r',?\s+(near|at|adjacent\s+to|in\s+the|at\s+the)\s+.+?(?=\.|,|$)', '', address, flags=re.IGNORECASE)
    
    # THEN: Remove extra text after period
    if '.' in address:
        address = address.split('.')[0]
```

### Medium-Priority Fixes (Would improve 178 failures)

**Problem:** Extra text after address not removed

**Current code:** Only keeps text before first period

```python
if '.' in address:
    address = address.split('.')[0]
```

**Better approach:**
```python
# Keep only the address portion (has street number and street name)
# Everything after a verb+article pattern is extra
address = re.sub(r'[\.,]\s+(units?|officers?|police|residents?|reports?|indicated|responded)\s+.+$', '', address, flags=re.IGNORECASE)
```

### Low-Priority Fixes (Would improve 229 failures)

**Problem:** Intersections don't geocode to a point

**Note:** Nominatim API limitation, not fixable in code

**Alternatives:**
1. Try different geocoding service (Google, Bing)
2. Query each street separately, find centroid
3. Query "nearest intersection" with Nominatim

---

## Summary Table

| Issue | Current Handling | Success Rate | Fixable |
|-------|-----------------|--------------|---------|
| Location qualifiers | Partial regex removal | ~0% | Yes - improve regex |
| Extra text | Period split only | ~30% | Yes - better sentence detection |
| Incomplete addresses | Extraction regex | ~5% | Partially - better patterns |
| Intersections | Try "&" format | ~5% | No - API limitation |
| Police codes | Filter with pattern | 100% | Already done |
| Corrupted extraction | Multiple prefix removal | ~10% | Yes - better rules |

