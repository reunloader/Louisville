#!/usr/bin/env python3
"""
Retry geocoding for addresses that previously failed (marked as null).
This helps measure the improvement from our enhanced geocoding strategies.
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
    print("Retry Failed Address Geocoding")
    print("=" * 70)

    # Load current cache
    print("\n1. Loading existing cache...")
    cache = load_geocode_cache()
    total_addresses = len(cache)

    # Find failed addresses (those with null values)
    failed_addresses = [addr for addr, coords in cache.items() if coords is None]
    print(f"   Total addresses: {total_addresses}")
    print(f"   Failed addresses: {len(failed_addresses)}")

    if not failed_addresses:
        print("   No failed addresses to retry!")
        return

    # Ask for confirmation to avoid rate limiting
    print(f"\n⚠️  This will make {len(failed_addresses)} API requests.")
    print(f"   At 1 request/second, this will take ~{len(failed_addresses)//60} minutes.")
    response = input("   Continue? (yes/no): ")

    if response.lower() not in ['yes', 'y']:
        print("   Cancelled.")
        return

    # Retry failed addresses
    print(f"\n2. Retrying {len(failed_addresses)} failed addresses...")
    successes = 0
    still_failed = 0

    for i, address in enumerate(failed_addresses, 1):
        print(f"\n[{i}/{len(failed_addresses)}]", end=" ")

        coords = geocode_address(address)

        if coords:
            cache[address] = coords
            successes += 1
        else:
            still_failed += 1

        # Rate limiting
        if i < len(failed_addresses):
            time.sleep(RATE_LIMIT_DELAY)

        # Save progress every 50 addresses
        if i % 50 == 0:
            print(f"\n   Saving progress... ({successes} recovered so far)")
            save_geocode_cache(cache)

    # Final save
    print(f"\n3. Saving final results...")
    save_geocode_cache(cache)

    # Summary
    print("\n" + "=" * 70)
    print("Summary:")
    print(f"  Addresses retried: {len(failed_addresses)}")
    print(f"  Successfully geocoded: {successes} ({100*successes/len(failed_addresses):.1f}%)")
    print(f"  Still failed: {still_failed} ({100*still_failed/len(failed_addresses):.1f}%)")
    print(f"  Overall success rate: {100*(total_addresses-still_failed)/total_addresses:.1f}%")
    print("=" * 70)

    if successes > 0:
        print(f"\n✓ Improved geocoding by recovering {successes} previously failed addresses!")

if __name__ == "__main__":
    main()
