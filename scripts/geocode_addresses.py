#!/usr/bin/env python3
"""
Geocode addresses from Jekyll posts and save to _data/geocoded_addresses.json

This script:
1. Reads all posts from _posts/
2. Extracts addresses using the same patterns as the JavaScript
3. Geocodes new/missing addresses using Nominatim
4. Saves results to _data/geocoded_addresses.json
5. Respects rate limits (1 request per second)
"""

import json
import os
import re
import time
from pathlib import Path
from typing import Dict, Set, Tuple
import urllib.request
import urllib.parse

# Configuration
POSTS_DIR = "_posts"
DATA_FILE = "_data/geocoded_addresses.json"
RATE_LIMIT_DELAY = 1.0  # seconds between geocoding requests
USER_AGENT = "Derby City Watch Event Map"

def extract_addresses_from_content(content: str) -> Set[str]:
    """Extract addresses from post content using same patterns as JavaScript."""
    addresses = set()

    # Pattern 1: "block of Street Name" (e.g., "100 block of Sears Ave")
    block_pattern = r'(\d+)\s+block\s+of\s+([^–\n]+?)(?=\s*–|\s*\n|$)'
    for match in re.finditer(block_pattern, content, re.IGNORECASE):
        addr = f"{match.group(1)} {match.group(2).strip()}, Louisville, KY"
        addresses.add(addr)

    # Pattern 2: "Street and Street" intersections
    intersection_pattern = r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Parkway|Pky|Lane|Ln))\s+and\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Parkway|Pky|Lane|Ln))'
    for match in re.finditer(intersection_pattern, content):
        addr = f"{match.group(1).strip()} and {match.group(2).strip()}, Louisville, KY"
        addresses.add(addr)

    # Pattern 3: Full addresses (e.g., "4512 Tray Place")
    full_address_pattern = r'\b(\d+)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Place|Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Parkway|Pky|Lane|Ln))\b'
    for match in re.finditer(full_address_pattern, content):
        addr = f"{match.group(1)} {match.group(2).strip()}, Louisville, KY"
        # Avoid duplicates from block addresses
        if not any(addr.split(',')[0] in existing for existing in addresses):
            addresses.add(addr)

    return addresses

def read_all_posts() -> Set[str]:
    """Read all Jekyll posts and extract addresses."""
    all_addresses = set()
    posts_path = Path(POSTS_DIR)

    if not posts_path.exists():
        print(f"Warning: {POSTS_DIR} directory not found")
        return all_addresses

    # Recursively find all .md files
    post_files = list(posts_path.rglob("*.md"))
    print(f"Found {len(post_files)} post files")

    for post_file in post_files:
        try:
            with open(post_file, 'r', encoding='utf-8') as f:
                content = f.read()

                # Skip daily-digest posts
                if 'daily-digest' in content:
                    continue

                addresses = extract_addresses_from_content(content)
                all_addresses.update(addresses)
        except Exception as e:
            print(f"Error reading {post_file}: {e}")

    return all_addresses

def load_geocode_cache() -> Dict[str, Dict]:
    """Load existing geocoded addresses from data file."""
    data_file = Path(DATA_FILE)

    if data_file.exists():
        try:
            with open(data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading {DATA_FILE}: {e}")

    return {}

def save_geocode_cache(cache: Dict[str, Dict]):
    """Save geocoded addresses to data file."""
    data_file = Path(DATA_FILE)
    data_file.parent.mkdir(parents=True, exist_ok=True)

    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(cache, f, indent=2, sort_keys=True)

    print(f"Saved {len(cache)} geocoded addresses to {DATA_FILE}")

def geocode_address(address: str) -> Tuple[float, float, None]:
    """Geocode an address using Nominatim API."""
    url = f"https://nominatim.openstreetmap.org/search?format=json&q={urllib.parse.quote(address)}&limit=1"

    try:
        req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())

            if data and len(data) > 0:
                lat = float(data[0]['lat'])
                lng = float(data[0]['lon'])
                print(f"  ✓ Geocoded: {address[:50]}... -> ({lat:.4f}, {lng:.4f})")
                return {'lat': lat, 'lng': lng}
            else:
                print(f"  ✗ No results for: {address[:50]}...")
                return None
    except Exception as e:
        print(f"  ✗ Error geocoding {address[:50]}...: {e}")
        return None

def main():
    """Main function to geocode addresses from posts."""
    print("=" * 60)
    print("Derby City Watch Address Geocoding")
    print("=" * 60)

    # Load existing cache
    print("\n1. Loading existing geocode cache...")
    cache = load_geocode_cache()
    print(f"   Found {len(cache)} cached addresses")

    # Extract all addresses from posts
    print("\n2. Extracting addresses from posts...")
    all_addresses = read_all_posts()
    print(f"   Found {len(all_addresses)} unique addresses")

    # Find addresses that need geocoding
    new_addresses = [addr for addr in all_addresses if addr not in cache]
    print(f"\n3. Need to geocode {len(new_addresses)} new addresses")

    if not new_addresses:
        print("   All addresses already cached!")
        return

    # Geocode new addresses with rate limiting
    print("\n4. Geocoding new addresses (1 per second)...")
    geocoded_count = 0

    for i, address in enumerate(new_addresses, 1):
        print(f"   [{i}/{len(new_addresses)}]", end=" ")

        coords = geocode_address(address)
        if coords:
            cache[address] = coords
            geocoded_count += 1
        else:
            # Store null to avoid retrying failed addresses
            cache[address] = None

        # Rate limiting - wait 1 second between requests
        if i < len(new_addresses):
            time.sleep(RATE_LIMIT_DELAY)

    # Save updated cache
    print(f"\n5. Saving results...")
    save_geocode_cache(cache)

    # Summary
    print("\n" + "=" * 60)
    print("Summary:")
    print(f"  Total addresses: {len(all_addresses)}")
    print(f"  Previously cached: {len(all_addresses) - len(new_addresses)}")
    print(f"  Newly geocoded: {geocoded_count}")
    print(f"  Failed: {len(new_addresses) - geocoded_count}")
    print(f"  Total in cache: {len(cache)}")
    print("=" * 60)

if __name__ == "__main__":
    main()
