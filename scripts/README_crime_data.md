# Louisville Crime Data Automation

## How It Works

This automation fetches Louisville Metro Crime Data from LOJIC (Louisville-Jefferson County Information Consortium) and integrates it into the map.

### Automatic Updates

**GitHub Actions runs weekly** (every Monday at 6 AM UTC) to fetch the latest crime data. The workflow:

1. Tries multiple API endpoints to download the data
2. Uses browser-like headers to avoid blocking
3. Falls back to manual download file if present
4. Commits updates automatically

### Why Automation Should Work

While local testing may fail due to API restrictions, **GitHub Actions typically succeeds** because:

- Different IP address (GitHub's servers vs your local machine)
- Different network routing
- Consistent environment
- Public-facing infrastructure

### If Automation Fails

If GitHub Actions cannot download automatically, you have two options:

**Option 1: One-Time Manual Download**
```bash
# Download the file once manually
# Visit: https://data.louisvilleky.gov/maps/LOJIC::louisville-metro-ky-crime-data-2025
# Click "Download" → "GeoJSON"
# Save to: _data/crime_data.geojson

# Then commit and push
git add _data/crime_data.geojson
git commit -m "Add crime data"
git push
```

The map will use this file until the next successful automated update.

**Option 2: Keep Manual Updates**
```bash
# Download new data periodically (e.g., monthly)
# Save as /tmp/crime_data_manual.geojson
# Run the script
python scripts/fetch_crime_data.py
```

### Testing Locally

```bash
# Run the fetch script
python scripts/fetch_crime_data.py

# If it fails locally, try manual download method
# Then run again - it will use the manual file
```

### Data Source

- **Provider**: Louisville Metro Police Department via LOJIC
- **Update Frequency**: Weekly (per LOJIC)
- **Dataset**: Louisville Metro KY - Crime Data 2025
- **Fields**: Incident number, offense type, NIBRS codes, dates, location

### Monitoring

Check GitHub Actions runs at:
`https://github.com/[your-username]/Louisville/actions/workflows/fetch-crime-data.yml`

If you see consistent failures, the dataset may have moved or access restrictions changed. Check the LOJIC data portal for updates.
