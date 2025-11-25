#!/usr/bin/env python3
"""
Retry geocoding for intersection addresses that previously failed.
Only retries addresses that appear to be intersections (contain 'and' or '&').
"""

import sys
import yaml
import time
from pathlib import Path

# Import our improved geocoding functions
from geocode_addresses import geocode_address, load_geocode_cache, save_geocode_cache

DATA_FILE = "_data/geocoded_addresses.yml"
RATE_LIMIT_DELAY = 1.0

def main():
    print("=" * 70)
    print("Retry Failed Intersection Geocoding")
    print("=" * 70)

    # Load current cache
    print("\n1. Loading existing cache...")
    cache = load_geocode_cache()
    total_addresses = len(cache)

    # Find failed intersection addresses
    failed_intersections = [
        addr for addr, coords in cache.items()
        if coords is None and (' and ' in addr.lower() or ' & ' in addr)
    ]

    print(f"   Total addresses: {total_addresses}")
    print(f"   Total failed addresses: {sum(1 for c in cache.values() if c is None)}")
    print(f"   Failed intersections: {len(failed_intersections)}")

    if not failed_intersections:
        print("   No failed intersections to retry!")
        return

    # Show estimate
    print(f"\n⚠️  This will make up to {len(failed_intersections)} API requests.")
    print(f"   Estimated time: ~{len(failed_intersections)//60} minutes")
    print(f"   (With new strategies: &, @, reversed, no-types, midpoint)")

    response = input("\n   Continue? (yes/no): ")

    if response.lower() not in ['yes', 'y']:
        print("   Cancelled.")
        return

    # Retry failed intersections
    print(f"\n2. Retrying {len(failed_intersections)} failed intersections...")
    successes = 0
    still_failed = 0

    for i, address in enumerate(failed_intersections, 1):
        print(f"\n[{i}/{len(failed_intersections)}]", end=" ")

        coords = geocode_address(address)

        if coords:
            cache[address] = coords
            successes += 1
        else:
            still_failed += 1

        # Rate limiting
        if i < len(failed_intersections):
            time.sleep(RATE_LIMIT_DELAY)

        # Save progress every 20 addresses
        if i % 20 == 0:
            print(f"\n   💾 Saving progress... ({successes} recovered so far)")
            save_geocode_cache(cache)

    # Final save
    print(f"\n3. Saving final results...")
    save_geocode_cache(cache)

    # Summary
    print("\n" + "=" * 70)
    print("Summary:")
    print(f"  Intersections retried: {len(failed_intersections)}")
    print(f"  Successfully geocoded: {successes} ({100*successes/len(failed_intersections):.1f}%)")
    print(f"  Still failed: {still_failed} ({100*still_failed/len(failed_intersections):.1f}%)")

    # Calculate new overall stats
    total_failed = sum(1 for c in cache.values() if c is None)
    total_success = total_addresses - total_failed
    print(f"  Overall success rate: {100*total_success/total_addresses:.2f}%")
    print("=" * 70)

    if successes > 0:
        print(f"\n✅ Improved by recovering {successes} intersection addresses!")
        print(f"   Intersection failure count reduced from 501 to {501 - successes}")

if __name__ == "__main__":
    main()
