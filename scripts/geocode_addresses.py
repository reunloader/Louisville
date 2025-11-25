#!/usr/bin/env python3
"""
Geocode addresses from Jekyll posts and save to _data/geocoded_addresses.yml

This script:
1. Reads all posts from _posts/
2. Extracts addresses using the same patterns as the JavaScript
3. Geocodes new/missing addresses using Nominatim
4. Saves results to _data/geocoded_addresses.yml
5. Respects rate limits (1 request per second)
"""

import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Dict, Set, Tuple
import urllib.request
import urllib.parse

try:
    import yaml
except ImportError:
    print("PyYAML not found, installing...")
    import subprocess
    subprocess.check_call(['pip', 'install', '--quiet', 'pyyaml'])
    import yaml

# Configuration
POSTS_DIR = "_posts"
DATA_FILE = "_data/geocoded_addresses.yml"
RATE_LIMIT_DELAY = 1.0  # seconds between geocoding requests
USER_AGENT = "Derby City Watch Event Map"

def normalize_address(address: str) -> str:
    """Normalize extracted addresses to fix common extraction issues."""
    if not address:
        return address

    # Remove ", Louisville, KY" suffix to work with address part
    suffix = ", Louisville, KY"
    addr_part = address[:-len(suffix)] if address.endswith(suffix) else address

    # Remove extra text after the address by stopping at common separators
    # These words typically indicate the address has ended and context has begun
    separators = [
        r'\s+for\s+',         # "600 South 40th Street for a 64-year-old"
        r'\s+to\s+',          # "100 Main St to investigate"
        r'\s+where\s+',       # "100 Main St where officers found"
        r'\s+following\s+',   # "100 Main St following a report"
        r'\s+after\s+',       # "100 Main St after receiving"
        r'\s+regarding\s+',   # "100 Main St regarding an incident"
        r'\s+on\s+',          # "100 Main St on a report" (but keep "on Street")
        r'\s+in\s+response\s+', # "100 Main St in response to"
        r'\s+due\s+to\s+',    # "100 Main St due to"
        r'\.',                # Stop at periods (likely new sentence)
    ]

    for sep_pattern in separators:
        match = re.search(sep_pattern, addr_part, re.IGNORECASE)
        if match:
            # Special case: don't split on "on" if it's part of a street name like "Main on Street"
            if sep_pattern == r'\s+on\s+':
                # Check if "on" is followed by a street type (Street, Ave, etc)
                after_on = addr_part[match.end():]
                if not re.match(r'^(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Parkway|Pky|Lane|Ln)\b', after_on, re.IGNORECASE):
                    addr_part = addr_part[:match.start()]
                    break
            else:
                addr_part = addr_part[:match.start()]
                break

    # Fix common OCR/typo errors for highways
    # "at65" or "at64" → "I-65", "I-64"
    addr_part = re.sub(r'\bat(\d{2,3})\b', r'I-\1', addr_part, flags=re.IGNORECASE)

    # Fix repeated letter prefixes (W W W Cardinal → W Cardinal)
    # Match patterns like "W W W" or "S S S" or "E E E"
    addr_part = re.sub(r'\b([A-Z])\s+\1\s+\1\b', r'\1', addr_part)
    addr_part = re.sub(r'\b([A-Z])\s+\1\b', r'\1', addr_part)

    # Normalize multiple spaces
    addr_part = re.sub(r'\s+', ' ', addr_part).strip()

    return addr_part + suffix if addr_part else ""

def extract_addresses_from_content(content: str) -> Set[str]:
    """Extract addresses from post content using same patterns as JavaScript."""
    addresses = set()

    # Pattern 1: "block of Street Name" (e.g., "100 block of Sears Ave")
    block_pattern = r'(\d+)\s+block\s+of\s+([^–\n]+?)(?=\s*–|\s*\n|$)'
    for match in re.finditer(block_pattern, content, re.IGNORECASE):
        addr = f"{match.group(1)} {match.group(2).strip()}, Louisville, KY"
        addr = normalize_address(addr)
        if addr:
            addresses.add(addr)

    # Pattern 2: "Street and Street" intersections (multiple formats)
    # Match: "Street and Street", "Street & Street", "at the intersection of Street and Street"
    street_types = r'(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Parkway|Pky|Lane|Ln|Way|Court|Ct|Circle|Cir)'
    street_pattern = r'(?:[NSEW]\.?\s+)?[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+' + street_types

    # Format 1: "Street and/& Street"
    intersection_pattern = f'({street_pattern})\\s+(?:and|&)\\s+({street_pattern})'
    for match in re.finditer(intersection_pattern, content):
        addr = f"{match.group(1).strip()} and {match.group(2).strip()}, Louisville, KY"
        addr = normalize_address(addr)
        if addr:
            addresses.add(addr)

    # Format 2: "at the intersection of Street and Street"
    intersection_at_pattern = r'at\s+the\s+intersection\s+of\s+(' + street_pattern + r')\s+and\s+(' + street_pattern + r')'
    for match in re.finditer(intersection_at_pattern, content, re.IGNORECASE):
        addr = f"{match.group(1).strip()} and {match.group(2).strip()}, Louisville, KY"
        addr = normalize_address(addr)
        if addr:
            addresses.add(addr)

    # Pattern 3: Full addresses (e.g., "4512 Tray Place")
    full_address_pattern = r'\b(\d+)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Place|Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Parkway|Pky|Lane|Ln))\b'
    for match in re.finditer(full_address_pattern, content):
        addr = f"{match.group(1)} {match.group(2).strip()}, Louisville, KY"
        # Avoid duplicates from block addresses
        if not any(addr.split(',')[0] in existing for existing in addresses):
            addr = normalize_address(addr)
            if addr:
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
                return yaml.safe_load(f) or {}
        except Exception as e:
            print(f"Error loading {DATA_FILE}: {e}")

    return {}

def save_geocode_cache(cache: Dict[str, Dict]):
    """Save geocoded addresses to data file."""
    data_file = Path(DATA_FILE)
    data_file.parent.mkdir(parents=True, exist_ok=True)

    with open(data_file, 'w', encoding='utf-8') as f:
        yaml.dump(cache, f, default_flow_style=False, allow_unicode=True, sort_keys=True)

    print(f"Saved {len(cache)} geocoded addresses to {DATA_FILE}")

def clean_address(address: str) -> str:
    """Clean and normalize an address for better geocoding."""
    if not address or not address.strip():
        return ""

    # Remove ", Louisville, KY" suffix temporarily to work with address part
    original = address
    suffix = ", Louisville, KY"
    if address.endswith(suffix):
        address = address[:-len(suffix)]

    # Remove everything after first period (extra context/sentences)
    if '.' in address:
        address = address.split('.')[0]

    # Remove bracketed content like [Date], [Time], [Street Name Redacted]
    address = re.sub(r'\[.*?\]', '', address)

    # Remove extra location qualifiers
    address = re.sub(r',?\s+near\s+.*$', '', address, flags=re.IGNORECASE)
    address = re.sub(r',?\s+at\s+.*$', '', address, flags=re.IGNORECASE)

    # Fix missing spaces before street numbers (e.g., "North45th" -> "North 45th")
    address = re.sub(r'([A-Za-z])(\d)', r'\1 \2', address)

    # Normalize multiple spaces
    address = re.sub(r'\s+', ' ', address).strip()

    # Filter out obviously bad extractions
    bad_patterns = [
        r'^\s*$',  # Empty
        r'ground plane',
        r'mile marker',
        r'Bravo Papa',  # Police codes
        r'an unspecified location',
        r'^\d+\s+and\s+\d+\s+block\s+of\s*$',  # Malformed block
    ]

    for pattern in bad_patterns:
        if re.search(pattern, address, re.IGNORECASE):
            return ""

    return address + suffix if address else ""

def format_highway_address(address: str) -> str:
    """Convert highway addresses to a format Nominatim understands better."""
    if not address:
        return ""

    # Match patterns like "100 I 64 East" or "1000 I-71 South"
    highway_match = re.search(r'(\d+)\s+I-?\s*(\d+)\s+(North|South|East|West)?', address, re.IGNORECASE)

    if highway_match:
        highway_num = highway_match.group(2)
        direction = highway_match.group(3)

        # Try simplified format: "I-64, Louisville, KY"
        if direction:
            return f"Interstate {highway_num} {direction}, Louisville, KY"
        else:
            return f"Interstate {highway_num}, Louisville, KY"

    return address

def extract_landmark(address: str) -> str:
    """Extract landmark from 'near X' or 'at X' patterns for landmark-based geocoding."""
    if not address:
        return ""

    # Remove ", Louisville, KY" suffix to work with address part
    suffix = ", Louisville, KY"
    addr_part = address[:-len(suffix)] if address.endswith(suffix) else address

    # Try to extract landmark after "at", "near", or "adjacent to"
    # Pattern: "address at/near/adjacent to landmark"
    landmark_patterns = [
        r'\s+at\s+(?:the\s+)?([^,\.]+)',  # "100 River Rd at Joe's Crab Shack" or "at the Walgreens"
        r'\s+near\s+(?:the\s+)?([^,\.]+)', # "100 Pluto Dr near Astro Court"
        r'\s+adjacent\s+to\s+(?:the\s+)?([^,\.]+)', # "1800 Lincoln Ave adjacent to the German American Club"
    ]

    for pattern in landmark_patterns:
        match = re.search(pattern, addr_part, re.IGNORECASE)
        if match:
            landmark = match.group(1).strip()
            # Clean up any trailing context
            landmark = re.sub(r'\s+(to|for|due to|following).*$', '', landmark, flags=re.IGNORECASE)
            if landmark and len(landmark) > 3:  # Avoid very short/useless landmarks
                return f"{landmark}, Louisville, KY"

    return ""

def try_geocode_query(query: str) -> Dict:
    """Single geocoding attempt with Nominatim."""
    if not query or not query.strip():
        return None

    url = f"https://nominatim.openstreetmap.org/search?format=json&q={urllib.parse.quote(query)}&limit=1"

    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': USER_AGENT,
            'Accept': 'application/json'
        })
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())

            if data and len(data) > 0:
                lat = float(data[0]['lat'])
                lng = float(data[0]['lon'])
                return {'lat': lat, 'lng': lng}
    except urllib.error.HTTPError as e:
        if e.code == 403 or e.code == 429:
            # Rate limit hit - wait and let caller handle
            time.sleep(2)
    except Exception as e:
        pass  # Silent fail, will be logged at higher level

    return None

def geocode_intersection(address: str) -> Tuple[Dict, str, None]:
    """
    Specialized geocoding for street intersections with multiple strategies.
    Returns tuple of (result, strategy_used) or (None, None) if all fail.
    """
    if " and " not in address.lower() and " & " not in address:
        return None, None

    # Remove ", Louisville, KY" suffix to work with address part
    suffix = ", Louisville, KY"
    addr_part = address[:-len(suffix)] if address.endswith(suffix) else address

    # Normalize to use "and" for processing
    addr_part = addr_part.replace(" & ", " and ").replace(" And ", " and ")

    # Extract the two street names
    if " and " not in addr_part.lower():
        return None, None

    parts = re.split(r'\s+and\s+', addr_part, flags=re.IGNORECASE)
    if len(parts) != 2:
        return None, None

    street1 = parts[0].strip()
    street2 = parts[1].strip()

    # Strategy 1: Try with "&" symbol
    query = f"{street1} & {street2}, Louisville, KY"
    result = try_geocode_query(query)
    if result:
        return result, f"Intersection & format: {query}"

    # Strategy 2: Try with "@" symbol (Nominatim intersection format)
    query = f"{street1} @ {street2}, Louisville, KY"
    result = try_geocode_query(query)
    if result:
        return result, f"Intersection @ format: {query}"

    # Strategy 3: Try reversed order with "&"
    query = f"{street2} & {street1}, Louisville, KY"
    result = try_geocode_query(query)
    if result:
        return result, f"Intersection reversed: {query}"

    # Strategy 4: Try without street types (e.g., "Newburg and Travillion")
    street1_base = re.sub(r'\s+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Parkway|Pky|Lane|Ln|Way|Court|Ct|Circle|Cir)$', '', street1, flags=re.IGNORECASE)
    street2_base = re.sub(r'\s+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Parkway|Pky|Lane|Ln|Way|Court|Ct|Circle|Cir)$', '', street2, flags=re.IGNORECASE)

    if street1_base != street1 or street2_base != street2:
        query = f"{street1_base} & {street2_base}, Louisville, KY"
        result = try_geocode_query(query)
        if result:
            return result, f"Intersection without types: {query}"

    # Strategy 5: Try geocoding each street separately and calculate midpoint
    query1 = f"{street1}, Louisville, KY"
    query2 = f"{street2}, Louisville, KY"

    result1 = try_geocode_query(query1)
    if result1:
        time.sleep(RATE_LIMIT_DELAY)  # Rate limit between queries
        result2 = try_geocode_query(query2)
        if result2:
            # Calculate midpoint between the two streets
            mid_lat = (result1['lat'] + result2['lat']) / 2
            mid_lng = (result1['lng'] + result2['lng']) / 2

            # Only use midpoint if streets are reasonably close (within ~5km)
            # Simple distance check: 0.05 degrees ≈ 5.5km at this latitude
            lat_diff = abs(result1['lat'] - result2['lat'])
            lng_diff = abs(result1['lng'] - result2['lng'])

            if lat_diff < 0.05 and lng_diff < 0.05:
                return {'lat': mid_lat, 'lng': mid_lng}, f"Midpoint of {street1} and {street2}"

    return None, None

def geocode_address(address: str) -> Tuple[float, float, None]:
    """Geocode an address using Nominatim API with fallback strategies."""

    # Strategy 1: Try original address
    result = try_geocode_query(address)
    if result:
        print(f"  ✓ [Original] {address[:60]}... -> ({result['lat']:.4f}, {result['lng']:.4f})")
        return result

    # Strategy 2: For intersections, use specialized intersection geocoding
    if " and " in address.lower() or " & " in address:
        result, strategy = geocode_intersection(address)
        if result:
            print(f"  ✓ [Intersection] {address[:60]}...")
            print(f"                -> {strategy[:60]}... -> ({result['lat']:.4f}, {result['lng']:.4f})")
            return result

    # Strategy 3: Try cleaned address
    cleaned = clean_address(address)
    if cleaned and cleaned != address:
        result = try_geocode_query(cleaned)
        if result:
            print(f"  ✓ [Cleaned] {address[:60]}...")
            print(f"           -> {cleaned[:60]}... -> ({result['lat']:.4f}, {result['lng']:.4f})")
            return result

    # Strategy 4: Try highway-formatted address
    highway = format_highway_address(address)
    if highway and highway != address and highway != cleaned:
        result = try_geocode_query(highway)
        if result:
            print(f"  ✓ [Highway] {address[:60]}...")
            print(f"           -> {highway[:60]}... -> ({result['lat']:.4f}, {result['lng']:.4f})")
            return result

    # Strategy 5: Try landmark-based geocoding
    landmark = extract_landmark(address)
    if landmark and landmark != address:
        result = try_geocode_query(landmark)
        if result:
            print(f"  ✓ [Landmark] {address[:60]}...")
            print(f"            -> {landmark[:60]}... -> ({result['lat']:.4f}, {result['lng']:.4f})")
            return result

    # All strategies failed
    print(f"  ✗ Failed all strategies: {address[:70]}...")
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

    # Track success metrics
    try:
        import subprocess
        print("\n6. Updating success metrics...")
        result = subprocess.run(
            [sys.executable, "scripts/track_geocoding_success.py"],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            # Print just the summary from the tracker
            if "SUMMARY" in result.stdout:
                summary_section = result.stdout.split("SUMMARY")[1]
                print(summary_section)
        else:
            print(f"   Warning: Could not update metrics: {result.stderr}")
    except Exception as e:
        print(f"   Warning: Could not update metrics: {e}")

if __name__ == "__main__":
    main()
