#!/usr/bin/env python3
"""
Fetch Louisville Metro Crime Data from ArcGIS Open Data Portal

This script:
1. Automatically detects the current year for the dataset
2. Downloads crime data from Louisville Open Data Portal
3. Saves to _data/crime_data.geojson for use by the map
4. Falls back to previous year if current year unavailable

MANUAL DOWNLOAD OPTION:
If automatic download fails due to access restrictions, you can manually download:
1. Go to: https://data.louisvilleky.gov/maps/LOJIC::louisville-metro-ky-crime-data-2025
2. Click "Download" → "GeoJSON"
3. Save as: /tmp/crime_data_manual.geojson
4. Run this script - it will use the manual download
"""

import json
import os
import sys
import time
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Configuration
DATA_FILE = "_data/crime_data.geojson"
USER_AGENT = "Derby City Watch Event Map"

# Dataset item IDs for different years (from data.louisvilleky.gov)
# Format: item_id (without the _0 suffix)
DATASET_IDS_BY_YEAR = {
    2025: "9de5b1d74b8140c5a99a40c613161fd4",
    2024: "a220289a40c945298d7f9d5c8dc7b3c0",
    2023: "46c4964747074431bea21e119b4b7294",
}

def get_years_to_try() -> List[int]:
    """Get list of years to try, starting with current year."""
    current_year = datetime.now().year
    # Try current year and recent years we have IDs for
    years = [current_year, current_year + 1, current_year - 1, current_year - 2]
    # Filter to only years we have IDs for
    return [y for y in years if y in DATASET_IDS_BY_YEAR]

def download_geojson(dataset_id: str, year: int) -> Optional[Dict]:
    """Download GeoJSON from Louisville Open Data Portal using dataset ID."""

    # Try multiple download methods
    download_urls = [
        # Method 1: CSV download (often less restricted)
        f"https://opendata.arcgis.com/api/v3/datasets/{dataset_id}_0/downloads/data?format=csv&spatialRefId=4326",

        # Method 2: Direct GeoJSON export
        f"https://opendata.arcgis.com/api/v3/datasets/{dataset_id}_0/downloads/data?format=geojson&spatialRefId=4326",

        # Method 3: FeatureServer query
        f"https://services1.arcgis.com/79kfd2K6fskCAkyg/arcgis/rest/services/Louisville_Metro_KY_Crime_Data_{year}/FeatureServer/0/query?where=1%3D1&outFields=*&f=geojson",

        # Method 4: Alternative open data CDN
        f"https://opendata.arcgis.com/datasets/{dataset_id}_0.geojson",

        # Method 5: Hub API
        f"https://louisville-metro-opendata-lojic.hub.arcgis.com/datasets/{dataset_id}.geojson",
    ]

    for i, url in enumerate(download_urls, 1):
        try:
            print(f"    Method {i}: ", end='', flush=True)

            req = urllib.request.Request(url, headers={
                'User-Agent': USER_AGENT,
                'Accept': 'application/json, application/geo+json',
                'Referer': 'https://data.louisvilleky.gov/'
            })

            print("Downloading...", end='', flush=True)

            with urllib.request.urlopen(req, timeout=300) as response:
                # Check content type
                content_type = response.headers.get('Content-Type', '')

                # Read response
                data = response.read()

                # Check if it's an error page or redirect
                if len(data) < 1000 and b'<!DOCTYPE' in data:
                    print(" ✗ (HTML error page)")
                    continue

                if len(data) < 100:
                    print(f" ✗ (Too small: {len(data)} bytes)")
                    continue

                # Try to parse as JSON
                try:
                    geojson = json.loads(data.decode('utf-8'))

                    # Validate it's actually GeoJSON
                    if geojson.get('type') == 'FeatureCollection' and 'features' in geojson:
                        feature_count = len(geojson['features'])
                        size_mb = len(data) / (1024 * 1024)
                        print(f" ✓ ({feature_count:,} features, {size_mb:.1f} MB)")

                        # Add metadata
                        geojson['metadata'] = {
                            'source': 'Louisville Metro KY - LOJIC',
                            'year': year,
                            'dataset_id': dataset_id,
                            'fetched_at': datetime.now().isoformat(),
                            'total_features': feature_count,
                            'download_url': url
                        }

                        return geojson
                    else:
                        print(f" ✗ (Invalid GeoJSON structure)")
                        continue

                except json.JSONDecodeError as e:
                    print(f" ✗ (JSON parse error: {e})")
                    continue

        except urllib.error.HTTPError as e:
            print(f" ✗ (HTTP {e.code})")
        except urllib.error.URLError as e:
            print(f" ✗ (URL error: {e.reason})")
        except Exception as e:
            print(f" ✗ ({type(e).__name__})")

    return None

def find_and_download_crime_data() -> Optional[tuple]:
    """Find and download the most recent available crime data."""
    print("Looking for Louisville crime data...")

    for year in get_years_to_try():
        if year not in DATASET_IDS_BY_YEAR:
            continue

        dataset_id = DATASET_IDS_BY_YEAR[year]
        print(f"\n  Trying {year} (ID: {dataset_id}):")

        geojson = download_geojson(dataset_id, year)

        if geojson:
            return (geojson, year)

    print("\n  No crime data could be downloaded")
    return None

def save_geojson(geojson: Dict):
    """Save GeoJSON data to file."""
    data_file = Path(DATA_FILE)
    data_file.parent.mkdir(parents=True, exist_ok=True)

    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(geojson, f, indent=2, ensure_ascii=False)

    # Calculate file size
    file_size = data_file.stat().st_size
    size_mb = file_size / (1024 * 1024)

    print(f"\n  Saved to {DATA_FILE}")
    print(f"  File size: {size_mb:.2f} MB")

def analyze_crime_data(geojson: Dict):
    """Analyze and print statistics about the crime data."""
    features = geojson.get('features', [])

    if not features:
        return

    print(f"\n  Crime Data Statistics:")
    print(f"  {'─' * 50}")

    # Count by NIBRS Group
    nibrs_counts = {}
    offense_counts = {}
    date_counts = {}

    for feature in features:
        props = feature.get('properties', {})

        # NIBRS Group
        nibrs = props.get('NIBRS_GROUP') or props.get('nibrs_group') or 'Unknown'
        nibrs_counts[nibrs] = nibrs_counts.get(nibrs, 0) + 1

        # Offense Classification
        offense = props.get('OFFENSE_CLASSIFICATION') or props.get('offense_classification') or 'Unknown'
        offense_counts[offense] = offense_counts.get(offense, 0) + 1

        # Date reporting
        date_reported = props.get('DATE_REPORTED') or props.get('date_reported') or ''
        if date_reported:
            # Extract month if possible (handle various date formats)
            try:
                if 'T' in str(date_reported):
                    month = str(date_reported)[:7]  # YYYY-MM
                else:
                    month = str(date_reported)[:7]
                date_counts[month] = date_counts.get(month, 0) + 1
            except:
                pass

    # Print top NIBRS groups
    print(f"\n  Top Crime Categories (NIBRS Group):")
    for nibrs, count in sorted(nibrs_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
        pct = (count / len(features)) * 100
        print(f"    {nibrs[:40]:40s}: {count:6,} ({pct:5.1f}%)")

    # Print recent monthly trend if available
    if date_counts:
        print(f"\n  Recent Monthly Trend:")
        for month in sorted(date_counts.keys(), reverse=True)[:6]:
            count = date_counts[month]
            print(f"    {month}: {count:,}")

def load_manual_download() -> Optional[Dict]:
    """Check for and load manually downloaded GeoJSON file."""
    manual_paths = [
        "/tmp/crime_data_manual.geojson",
        "crime_data_manual.geojson",
        "_data/crime_data_manual.geojson",
    ]

    for path in manual_paths:
        if Path(path).exists():
            print(f"  Found manual download: {path}")
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    geojson = json.load(f)

                if geojson.get('type') == 'FeatureCollection' and 'features' in geojson:
                    feature_count = len(geojson['features'])
                    print(f"  ✓ Loaded {feature_count:,} features from manual download")

                    # Add metadata if missing
                    if 'metadata' not in geojson:
                        geojson['metadata'] = {}
                    geojson['metadata'].update({
                        'source': 'Louisville Metro KY - LOJIC (manual download)',
                        'fetched_at': datetime.now().isoformat(),
                        'total_features': feature_count,
                    })

                    return geojson
            except Exception as e:
                print(f"  ✗ Error loading manual download: {e}")

    return None

def main():
    """Main function to download and save crime data."""
    print("=" * 60)
    print("Derby City Watch - Crime Data Fetcher")
    print("=" * 60)

    # Check for manual download first
    print("\nChecking for manual download...")
    geojson = load_manual_download()

    if geojson:
        year = geojson.get('metadata', {}).get('year', datetime.now().year)
        print(f"\n✓ Using manually downloaded crime data")
    else:
        print("  No manual download found")

        # Find and download crime data automatically
        result = find_and_download_crime_data()

        if not result:
            print("\n❌ Could not download crime data automatically")
            print("   Tried years:", get_years_to_try())
            print("\n   MANUAL DOWNLOAD INSTRUCTIONS:")
            print("   1. Go to: https://data.louisvilleky.gov/maps/LOJIC::louisville-metro-ky-crime-data-2025")
            print("   2. Click 'Download' → 'GeoJSON'")
            print("   3. Save as: /tmp/crime_data_manual.geojson")
            print("   4. Run this script again")
            sys.exit(1)

        geojson, year = result
        print(f"\n✓ Successfully downloaded {year} crime data")

    # Analyze the data
    analyze_crime_data(geojson)

    # Save to file
    save_geojson(geojson)

    # Summary
    print("\n" + "=" * 60)
    print("Summary:")
    print(f"  Year: {year}")
    print(f"  Features: {len(geojson['features']):,}")
    print(f"  Saved to: {DATA_FILE}")
    print("=" * 60)
    print("\n✅ Crime data fetch complete!")

if __name__ == "__main__":
    main()
