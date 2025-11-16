# Geocoding Scripts

## Overview

This directory contains scripts for geocoding addresses from Derby City Watch posts.

## How It Works

### Automatic Geocoding (Recommended)

GitHub Actions automatically geocodes new addresses when posts are created:

1. **New post is created** in `_posts/`
2. **GitHub Actions triggers** (`.github/workflows/geocode-addresses.yml`)
3. **Script runs** (`geocode_addresses.py`)
4. **Addresses are extracted** from all posts
5. **New addresses are geocoded** using Nominatim API (1/second)
6. **Results are saved** to `_data/geocoded_addresses.json`
7. **Changes are auto-committed** to the repository
8. **GitHub Pages rebuilds** with updated coordinates
9. **Map loads instantly** for all users

### Manual Geocoding

You can also run the script manually:

```bash
cd /path/to/Louisville
python scripts/geocode_addresses.py
```

This will:
- Read all posts from `_posts/`
- Extract addresses using regex patterns
- Check `_data/geocoded_addresses.json` for existing coordinates
- Geocode only new/missing addresses
- Update the data file
- Show a summary of results

### File Structure

```
scripts/
├── geocode_addresses.py    # Main geocoding script
└── README.md               # This file

_data/
└── geocoded_addresses.json # Server-side coordinate cache

.github/workflows/
└── geocode-addresses.yml   # GitHub Actions workflow
```

## How the Map Uses This Data

The map (`_layouts/map.html`) loads coordinates in this priority:

1. **Server-side cache** (`site.data.geocoded_addresses`) - Instant, no API calls
2. **Browser localStorage** - Cached from previous visits
3. **Live geocoding** - Only for brand new addresses not in either cache

This means:
- **First-time users**: Instant load (server-side cache)
- **Returning users**: Instant load (server + browser cache)
- **New addresses**: Only those need geocoding (rare)

## Rate Limiting

The script respects Nominatim's usage policy:
- Maximum 1 request per second
- User-Agent header: "Derby City Watch Event Map"
- Results are cached to avoid re-requesting

## Address Extraction Patterns

The script uses the same regex patterns as the JavaScript map:

1. **Block addresses**: "100 block of Sears Ave"
2. **Intersections**: "30th Street and Market Street"
3. **Full addresses**: "4512 Tray Place"

All addresses are normalized with ", Louisville, KY" suffix.

## Troubleshooting

### Script fails with "No module named 'xyz'"

The script uses only Python standard library, no dependencies needed.

### Geocoding fails for some addresses

Some addresses (especially intersections and block addresses) may not geocode successfully. These are stored as `null` in the cache to avoid retrying.

### Want to re-geocode all addresses

Delete `_data/geocoded_addresses.json` and run the script again. This will re-geocode everything (takes ~30 minutes for 2000 addresses).

### GitHub Actions not running

Check:
1. Workflow file is in `.github/workflows/`
2. Permissions are set correctly in workflow
3. Check Actions tab in GitHub for errors

## Testing

To test the script locally without saving:

```python
# Add at the end of geocode_addresses.py before save_geocode_cache():
print(json.dumps(cache, indent=2))
# Then comment out the save_geocode_cache() line
```

## Performance

- **Script runtime**: ~1 second per new address (rate limit)
- **2000 addresses**: ~33 minutes (one-time)
- **Daily updates**: Usually <30 seconds (only new addresses)
- **Map load time**: Instant (all coordinates pre-computed)
