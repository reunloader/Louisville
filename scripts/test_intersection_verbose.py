#!/usr/bin/env python3
"""
Verbose test for intersection geocoding
"""

import sys
import time
import re
from geocode_addresses import try_geocode_query

# Test just the intersection strategies manually
address = "Newburg Rd and Travillion Way, Louisville, KY"
print(f"Testing: {address}\n")

# Remove ", Louisville, KY" suffix to work with address part
suffix = ", Louisville, KY"
addr_part = address[:-len(suffix)] if address.endswith(suffix) else address

# Normalize to use "and" for processing
addr_part = addr_part.replace(" & ", " and ").replace(" And ", " and ")

# Extract the two street names
parts = re.split(r'\s+and\s+', addr_part, flags=re.IGNORECASE)
if len(parts) == 2:
    street1 = parts[0].strip()
    street2 = parts[1].strip()
    print(f"Street 1: {street1}")
    print(f"Street 2: {street2}\n")

    # Strategy 1: Try with "&" symbol
    query = f"{street1} & {street2}, Louisville, KY"
    print(f"Strategy 1: {query}")
    result = try_geocode_query(query)
    print(f"Result: {result}\n")
    time.sleep(1.5)

    if not result:
        # Strategy 2: Try with "@" symbol
        query = f"{street1} @ {street2}, Louisville, KY"
        print(f"Strategy 2: {query}")
        result = try_geocode_query(query)
        print(f"Result: {result}\n")
        time.sleep(1.5)

    if not result:
        # Strategy 3: Try geocoding each street separately
        query1 = f"{street1}, Louisville, KY"
        print(f"Strategy 3a: {query1}")
        result1 = try_geocode_query(query1)
        print(f"Result: {result1}\n")
        time.sleep(1.5)

        if result1:
            query2 = f"{street2}, Louisville, KY"
            print(f"Strategy 3b: {query2}")
            result2 = try_geocode_query(query2)
            print(f"Result: {result2}\n")

            if result2:
                mid_lat = (result1['lat'] + result2['lat']) / 2
                mid_lng = (result1['lng'] + result2['lng']) / 2
                print(f"Midpoint: ({mid_lat:.6f}, {mid_lng:.6f})")
