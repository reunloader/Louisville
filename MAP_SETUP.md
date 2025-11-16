# Event Map Setup Instructions

## Overview
The Event Map feature displays all Derby City Watch events on an interactive map using **OpenStreetMap** and **Leaflet.js** - completely free and open source with no API keys required!

## Features

### 100% Free & Open Source
- ✅ No API keys needed
- ✅ No credit card required
- ✅ No usage limits or quotas
- ✅ No billing setup
- ✅ Uses OpenStreetMap data and Nominatim geocoding

### Map Markers
- **Red markers**: Police events
- **Blue markers**: Medical emergencies
- **Orange markers**: Fire & Rescue

### Filtering Options
- **Category filter**: Show only specific event types (Police, Medical, Fire & Rescue)
- **Date range filter**: Display events within a specific timeframe
- Default view shows the last 7 days of events

### Interactive Features
Click any marker to see:
- Event date and time
- Location address
- Category and status
- Brief description
- Link to full event report

## No Setup Required!

The map works out of the box with no configuration needed. Just deploy your Jekyll site and the map will be available at `/map/`.

### Deploy to GitHub Pages

```bash
git add .
git commit -m "Add OpenStreetMap event visualization"
git push
```

GitHub Pages will automatically rebuild your site and the map will be live!

### Test Locally (Optional)

To test the map locally before deploying:

```bash
bundle install
bundle exec jekyll serve
```

Then visit `http://localhost:4000/map/`

## How It Works

### 1. Data Extraction
The layout uses Jekyll Liquid templating to extract the 500 most recent non-digest posts at build time.

### 2. Address Parsing
JavaScript parses event content to find:
- **Block addresses**: "100 block of Sears Ave"
- **Intersections**: "30th Street and Market Street"
- **Full addresses**: "4512 Tray Place"

### 3. Geocoding
Uses **Nominatim** (OpenStreetMap's free geocoding service) to convert addresses to coordinates.

### 4. Mapping
**Leaflet.js** library creates interactive markers with popups containing event details.

## Usage Policy

### Nominatim Fair Use
The map uses OpenStreetMap's Nominatim geocoding service, which requires:
- Maximum 1 request per second (already implemented in the code)
- User-Agent header (already included: "Derby City Watch Event Map")

These requirements are already built into the implementation, so no action is needed on your part.

### What This Means
- Geocoding happens in the visitor's browser when they load the page
- There's a 1-second delay between each address lookup
- For 100 addresses, expect ~100 seconds of loading time
- Progress indicator shows geocoding status

## Customization

### Change the Map Center
Edit line 302 in `_layouts/map.html`:

```javascript
map = L.map('map').setView([38.2527, -85.7585], 12);
//                           ↑ latitude  ↑ longitude  ↑ zoom level
```

### Change Default Zoom Level
Same line as above - the third parameter:
- Lower number = more zoomed out (e.g., 10 shows wider area)
- Higher number = more zoomed in (e.g., 14 shows street level)

### Change Number of Events Shown
Edit line 135 in `_layouts/map.html`:

```javascript
{% for post in site.posts limit:500 %}
//                              ↑ change this number
```

### Modify Address Extraction Patterns
Edit the regex patterns in the `extractAddresses()` function (lines 160-166) to match different address formats specific to your area.

### Change Marker Colors
Edit the `markerIcons` object (lines 192-217) to use different colors. Available colors:
- red, blue, orange, green, yellow, violet, grey, black, gold

Color marker URLs:
```
https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-{color}.png
```

### Change Map Tiles
Edit line 305 in `_layouts/map.html` to use different map styles:

```javascript
// Current (default OpenStreetMap):
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '&copy; OpenStreetMap contributors'
}).addTo(map);

// Alternative: Humanitarian map style
L.tileLayer('https://{s}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png', {
  attribution: '&copy; OpenStreetMap contributors'
}).addTo(map);

// Alternative: Black and white
L.tileLayer('https://{s}.tiles.wmflabs.org/bw-mapnik/{z}/{x}/{y}.png', {
  attribution: '&copy; OpenStreetMap contributors'
}).addTo(map);
```

## Performance Optimization

### Reduce Loading Time
If geocoding takes too long, you can:

1. **Limit the number of posts** (line 135):
   ```javascript
   {% for post in site.posts limit:200 %}  // Reduced from 500
   ```

2. **Pre-cache coordinates**: Add lat/lng to post frontmatter:
   ```yaml
   ---
   title: "Derby City Watch"
   location:
     lat: 38.2527
     lng: -85.7585
   ---
   ```
   Then modify the code to read coordinates instead of geocoding.

### Browser Caching
Browsers will cache the Leaflet library and map tiles, so subsequent page loads will be faster.

## Troubleshooting

### Map doesn't appear
- Check browser console (F12) for JavaScript errors
- Ensure your site is properly deployed to GitHub Pages
- Verify the page is accessible at `yoursite.github.io/map/`

### Addresses not geocoding correctly
- Some addresses may be ambiguous (especially intersections and block addresses)
- Nominatim automatically adds "Louisville, KY" to improve accuracy
- Check browser console for specific geocoding errors
- Consider adding more context to addresses in the regex patterns

### Slow loading
- This is expected with many addresses (1 second delay per address)
- Progress indicator shows geocoding status
- Consider reducing the post limit or pre-caching coordinates

### Markers not showing
- Ensure events have properly formatted addresses in their content
- Check that categories match exactly (case-sensitive)
- Use browser console to debug address extraction

## Technical Details

### Libraries Used
- **Leaflet.js 1.9.4**: Open-source JavaScript library for interactive maps
- **OpenStreetMap**: Free, editable map of the world
- **Nominatim**: Free geocoding service by OpenStreetMap

### CDN Resources
All resources are loaded from trusted CDNs with integrity checks:
- Leaflet CSS/JS: unpkg.com (with SRI hashes)
- Map tiles: tile.openstreetmap.org
- Marker icons: GitHub raw content (pointhi/leaflet-color-markers)

### Browser Compatibility
Works in all modern browsers:
- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Opera 76+

## Benefits Over Google Maps

✅ **No cost**: Completely free, no billing required
✅ **No API key**: No registration or key management
✅ **Privacy**: No tracking or user data collection
✅ **Open source**: Full control over the implementation
✅ **Community-driven**: Data maintained by OpenStreetMap contributors
✅ **No quotas**: No monthly limits or usage restrictions (within fair use)

## Support

For issues or questions about the map implementation, check:
- [Leaflet.js Documentation](https://leafletjs.com/)
- [OpenStreetMap Wiki](https://wiki.openstreetmap.org/)
- [Nominatim Usage Policy](https://operations.osmfoundation.org/policies/nominatim/)

For issues specific to this Derby City Watch implementation, please open an issue on the GitHub repository.
