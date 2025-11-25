#!/usr/bin/env python3
"""
Quick test for intersection geocoding
"""

import sys
from geocode_addresses import geocode_address
import time

test_intersections = [
    "Newburg Rd and Travillion Way, Louisville, KY",
    "Zorn Avenue and Country Club Road, Louisville, KY",
    "Bardstown Road and Eastern Parkway, Louisville, KY",
]

print("Testing intersection geocoding...")
print("=" * 70)

for addr in test_intersections:
    print(f"\nTesting: {addr}")
    result = geocode_address(addr)
    if result:
        print(f"  ✓ Success: {result}")
    else:
        print(f"  ✗ Failed")
    time.sleep(1.5)  # Rate limit

print("\n" + "=" * 70)
