#!/usr/bin/env python3
"""
Manual test of various query formats
"""

import time
from geocode_addresses import try_geocode_query

# Try various formats for the intersection
queries = [
    "Newburg Rd and Travillion Way, Louisville, KY",
    "Newburg Road and Travillion Way, Louisville, KY",
    "Newburg Rd & Travillion Way, Louisville, KY",
    "Newburg Road & Travillion Way, Louisville, KY",
    "Newburg Rd @ Travillion Way, Louisville, KY",
    "Newburg Road @ Travillion Way, Louisville, KY",
    # Try individual streets
    "Newburg Rd, Louisville, KY",
    "Newburg Road, Louisville, KY",
    "Travillion Way, Louisville, KY",
    # Try without types
    "Newburg and Travillion, Louisville, KY",
]

print("Testing various query formats...")
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
