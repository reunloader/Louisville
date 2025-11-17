#!/usr/bin/env python3
"""
Test geocoding improvements on a small sample of failed addresses.
"""

import yaml
import time
from pathlib import Path
from geocode_addresses import geocode_address

# Sample of failed addresses representing different failure types
test_sample = [
    "100 Indian Legends Dr. Responding units were assigned to manage the scene and clear the roadway., Louisville, KY",
    "100 North 45th Street, Louisville, KY",  # Missing space
    "100 Colonial Oaks Ct near South 1st Street, Louisville, KY",  # Extra location info
    "100 River Rd at Joe's Crab Shack, Louisville, KY",  # At location
    "100 I 64 East, Louisville, KY",  # Highway
    "Zorn Avenue and Country Club Road, Louisville, KY",  # Intersection
]

print("=" * 70)
print("Testing Geocoding Improvements on Sample Failures")
print("=" * 70)
print(f"\nTesting {len(test_sample)} addresses...")
print("⏳ This will take ~{} seconds (rate limiting)...\n".format(len(test_sample)))

successes = 0
failures = 0

for i, addr in enumerate(test_sample, 1):
    print(f"\n[{i}/{len(test_sample)}] {addr[:65]}...")

    result = geocode_address(addr)

    if result:
        successes += 1
    else:
        failures += 1

    # Rate limit
    if i < len(test_sample):
        time.sleep(1.5)  # Slightly longer to avoid 403s

print("\n" + "=" * 70)
print(f"Results: {successes} succeeded, {failures} failed")
print(f"Success rate: {100*successes/len(test_sample):.0f}%")
print("=" * 70)
