# Event Map Setup Instructions

## Overview
The Event Map feature displays all Derby City Watch events on an interactive Google Map. Events are automatically geocoded from their address information and displayed with color-coded markers.

## Google Maps API Key Setup

To enable the map functionality, you need to add a Google Maps API key:

### 1. Get a Google Maps API Key

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the following APIs:
   - Maps JavaScript API
   - Geocoding API
4. Go to "Credentials" and create an API key
5. (Recommended) Restrict the API key to:
   - HTTP referrers (websites): `*.github.io/*` or your domain
   - API restrictions: Maps JavaScript API and Geocoding API

### 2. Add the API Key to Your Site

Edit `_layouts/map.html` and replace `YOUR_API_KEY` on line 247:

```html
<!-- Replace this line -->
<script async defer
  src="https://maps.googleapis.com/maps/api/js?key=YOUR_API_KEY&callback=initMap">
</script>

<!-- With your actual key -->
<script async defer
  src="https://maps.googleapis.com/maps/api/js?key=AIzaSyAbc123YourActualKeyHere&callback=initMap">
</script>
```

### 3. Test Locally (Optional)

To test the map locally before deploying:

```bash
bundle install
bundle exec jekyll serve
```

Then visit `http://localhost:4000/map/`

### 4. Deploy

Commit your changes and push to GitHub. GitHub Pages will automatically rebuild your site.

```bash
git add _layouts/map.html map.md _config.yml
git commit -m "Add event map feature with Google Maps integration"
git push
```

## Features

### Map Markers
- **Red markers**: Police events
- **Blue markers**: Medical emergencies
- **Orange markers**: Fire & Rescue

### Filtering
- **Category filter**: Show only specific event types
- **Date range filter**: Display events within a specific timeframe
- Default view shows the last 7 days of events

### Event Details
Click any marker to see:
- Event date and time
- Location address
- Category and status
- Brief description
- Link to full event report

## How It Works

1. **Data Extraction**: The layout uses Jekyll Liquid templating to extract the 500 most recent non-digest posts
2. **Address Parsing**: JavaScript parses event content to find:
   - Block addresses (e.g., "100 block of Sears Ave")
   - Intersections (e.g., "30th Street and Market Street")
   - Full addresses (e.g., "4512 Tray Place")
3. **Geocoding**: The Google Geocoding API converts addresses to latitude/longitude coordinates
4. **Mapping**: Markers are placed on the map with info windows containing event details

## Rate Limiting

The free Google Maps API tier includes:
- 28,000 map loads per month
- 40,000 geocoding requests per month

The implementation includes a 100ms delay between geocoding requests to avoid rate limiting. If you have many events, consider:
- Caching geocoded coordinates in post frontmatter
- Reducing the number of posts processed (currently limited to 500)
- Upgrading to a paid Google Maps plan

## Customization

### Change the Map Center
Edit line 193 in `_layouts/map.html`:

```javascript
const louisville = { lat: 38.2527, lng: -85.7585 };
```

### Change Default Zoom Level
Edit line 196 in `_layouts/map.html`:

```javascript
zoom: 12,  // Lower number = more zoomed out
```

### Modify Address Patterns
Edit the regex patterns in the `extractAddresses()` function (lines 140-153) to match different address formats.

## Troubleshooting

### Map doesn't load
- Check browser console for API key errors
- Verify APIs are enabled in Google Cloud Console
- Check API key restrictions

### Addresses not geocoding
- Some addresses may be ambiguous (intersections, block addresses)
- Check browser console for geocoding errors
- Louisville, KY is automatically appended to all addresses

### Performance issues
- Reduce the post limit in line 68: `{% for post in site.posts limit:500 %}`
- Increase geocoding delay in line 165: `}, index * 100);`

## Support

For issues or questions, please open an issue on the GitHub repository.
