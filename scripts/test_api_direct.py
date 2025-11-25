#!/usr/bin/env python3
"""
Direct API test with full error details
"""

import json
import urllib.request
import urllib.parse

USER_AGENT = "Derby City Watch Event Map"

def test_query_verbose(query):
    """Test a query with verbose output."""
    print(f"\nTesting: {query}")
    print("-" * 60)

    url = f"https://nominatim.openstreetmap.org/search?format=json&q={urllib.parse.quote(query)}&limit=1"
    print(f"URL: {url}")

    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': USER_AGENT,
            'Accept': 'application/json'
        })
        print("Sending request...")

        with urllib.request.urlopen(req, timeout=10) as response:
            print(f"Response status: {response.status}")
            print(f"Response headers: {dict(response.headers)}")

            data = json.loads(response.read().decode())
            print(f"Response data: {json.dumps(data, indent=2)}")

            if data and len(data) > 0:
                lat = float(data[0]['lat'])
                lng = float(data[0]['lon'])
                print(f"✓ SUCCESS: ({lat:.6f}, {lng:.6f})")
                return True
            else:
                print("✗ No results returned")
                return False

    except urllib.error.HTTPError as e:
        print(f"✗ HTTP Error: {e.code} - {e.reason}")
        print(f"   Response body: {e.read().decode()}")
        return False
    except urllib.error.URLError as e:
        print(f"✗ URL Error: {e.reason}")
        return False
    except Exception as e:
        print(f"✗ Exception: {type(e).__name__}: {e}")
        return False

# Test with a simple known address
test_query_verbose("Broadway, Louisville, KY")

import time
time.sleep(2)

# Test with intersection
test_query_verbose("Broadway & 4th Street, Louisville, KY")
