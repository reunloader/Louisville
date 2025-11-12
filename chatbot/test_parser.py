#!/usr/bin/env python3
"""
Quick test script to verify scanner parser works correctly.
"""

from scanner_parser import ScannerParser
import os

print("Testing Derby City Watch Scanner Parser")
print("=" * 50)

# Initialize parser
posts_dir = "../_posts"
print(f"\nLoading posts from: {posts_dir}")

parser = ScannerParser(posts_dir)

print(f"✓ Loaded {len(parser.incidents)} incidents")

# Test 1: Show recent incidents
print("\n" + "=" * 50)
print("Test 1: Recent Incidents")
print("=" * 50)

recent = parser.get_recent_incidents(limit=3)
for i, incident in enumerate(recent, 1):
    print(f"\n{i}. {incident['title']}")
    print(f"   Date: {incident['date']}")
    print(f"   Status: {incident['status']}")
    print(f"   Categories: {', '.join(incident['categories'])}")
    print(f"   Incidents found: {len(incident['incidents'])}")

# Test 2: Location search
print("\n" + "=" * 50)
print("Test 2: Location Search - 'Bardstown'")
print("=" * 50)

bardstown_results = parser.search_by_location("Bardstown", limit=5)
print(f"\nFound {len(bardstown_results)} incidents mentioning 'Bardstown'")

for i, result in enumerate(bardstown_results[:3], 1):
    print(f"\n{i}. {result['date']}")
    for inc in result['incidents']:
        if 'bardstown' in inc['location'].lower():
            print(f"   {inc['emoji']} {inc['title']} - {inc['location']}")

# Test 3: Traffic search
print("\n" + "=" * 50)
print("Test 3: Category Search - 'traffic'")
print("=" * 50)

traffic = parser.get_recent_incidents(category='traffic', limit=5)
print(f"\nFound {len(traffic)} traffic-related incidents")

for i, result in enumerate(traffic[:3], 1):
    print(f"\n{i}. {result['date']}")
    print(f"   Status: {result['status']}")

# Test 4: AI data format
print("\n" + "=" * 50)
print("Test 4: AI Context Data Format")
print("=" * 50)

ai_data = parser.get_all_data_for_ai()
print(f"\nGenerated {len(ai_data)} characters of context data")
print(f"First 500 characters:\n")
print(ai_data[:500] + "...")

print("\n" + "=" * 50)
print("✓ All tests completed successfully!")
print("=" * 50)
