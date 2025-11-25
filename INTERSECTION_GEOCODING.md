# Intersection Geocoding Enhancement

## Overview

Enhanced the geocoding system to better handle street intersections like "Newburg Rd and Travillion Way".

## What Changed

### 1. Enhanced Address Extraction Patterns

**Python** (`scripts/geocode_addresses.py`):
- Added support for "&" in addition to "and" for intersections
- Added support for "at the intersection of X and Y" format
- Extended street types to include: Way, Court, Ct, Circle, Cir
- Added support for directional prefixes (N, S, E, W)

**JavaScript** (`_layouts/map.html`):
- Mirrored Python changes for consistency
- Updated regex patterns to match backend extraction

### 2. New Specialized Intersection Geocoding Function

Added `geocode_intersection()` function with 5 strategies:

1. **Try with "&" symbol**: `Street1 & Street2, Louisville, KY`
2. **Try with "@" symbol**: `Street1 @ Street2, Louisville, KY` (Nominatim intersection format)
3. **Try reversed order**: `Street2 & Street1, Louisville, KY`
4. **Try without street types**: `Newburg & Travillion, Louisville, KY`
5. **Midpoint calculation**: Geocode each street separately and calculate the midpoint between them
   - Only used if streets are within ~5km of each other
   - Provides approximate intersection location when exact match fails

### 3. Integration into Main Geocoding Pipeline

The specialized intersection geocoding now runs as **Strategy 2** (right after trying the original address), ensuring intersections are handled before falling back to generic cleaning strategies.

## Benefits

- Better recognition of intersection formats in post content
- Multiple fallback strategies specifically designed for intersections
- Intelligent midpoint calculation as last resort
- Consistent handling between backend Python and frontend JavaScript

## Example Intersections Now Supported

- "Newburg Rd and Travillion Way"
- "Broadway & 4th Street"
- "N 5th and Main Street"
- "at the intersection of Bardstown Road and Eastern Parkway"
- "Zorn Avenue & Country Club Road"

## Testing

### Basic Test
```bash
python3 scripts/test_intersection.py
```

This tests three sample intersections and shows which geocoding strategy succeeded.

### Note on Rate Limiting

Nominatim has a strict 1 request/second limit. If you see 403 Forbidden errors during testing:
1. Wait a few minutes before retrying
2. The production script (`geocode_addresses.py`) respects this limit with proper delays
3. Manual rapid testing can trigger temporary blocks

### Production Usage

The geocoding scripts automatically use these improvements:
```bash
python3 scripts/geocode_addresses.py
```

This will:
- Extract all addresses from posts (including intersections)
- Try the enhanced geocoding strategies
- Cache results in `_data/geocoded_addresses.yml`
- Update success metrics

## Technical Details

### Midpoint Calculation

When individual streets can be geocoded but not the intersection:
```python
mid_lat = (street1_lat + street2_lat) / 2
mid_lng = (street1_lng + street2_lng) / 2
```

Safety check: Only uses midpoint if streets are within 0.05 degrees (~5.5km), preventing invalid results for streets that are too far apart.

### Rate Limiting

The geocoding system:
- Waits 1.0 seconds between primary queries
- Waits 1.5 seconds between individual street queries during midpoint calculation
- Backs off on 403/429 errors

## Files Modified

1. `scripts/geocode_addresses.py` - Core geocoding engine
2. `_layouts/map.html` - Frontend address extraction
3. `scripts/test_intersection.py` - Test script for intersections

## Future Improvements

Potential enhancements:
- Use alternative geocoding services as fallback
- Cache common intersection patterns
- Pre-process known intersection abbreviations
- Integration with Louisville GIS data for more accurate intersections
