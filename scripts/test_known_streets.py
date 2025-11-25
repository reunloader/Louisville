#!/usr/bin/env python3
"""
Test with known major streets in Louisville
"""

import time
from geocode_addresses import try_geocode_query, geocode_address

# Try known major streets/intersections in Louisville
queries = [
    # Individual known streets
    "Broadway, Louisville, KY",
    "4th Street, Louisville, KY",
    "Bardstown Road, Louisville, KY",
    # Known intersections
    "Broadway and 4th Street, Louisville, KY",
    "Bardstown Road and Eastern Parkway, Louisville, KY",
]

print("Testing with known major streets in Louisville...")
print("=" * 70)

for query in queries:
    print(f"\nQuery: {query}")
    result = try_geocode_query(query)
    if result:
        print(f"  ✓ SUCCESS: ({result['lat']:.6f}, {result['lng']:.6f})")
    else:
        print(f"  ✗ Failed")
    time.sleep(1.2)

print("\n" + "=" * 70)
print("\nNow testing with full geocode_address function:")
print("=" * 70)

test_addr = "Broadway and 4th Street, Louisville, KY"
print(f"\nTesting: {test_addr}")
result = geocode_address(test_addr)
if result:
    print(f"Final result: {result}")
else:
    print("Failed")
