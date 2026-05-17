#!/usr/bin/env python3
"""
Test script to verify Planning Center API connection and find Organization/Service Type IDs
"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

PLANNING_CENTER_APP_ID = os.getenv('PLANNING_CENTER_APP_ID')
PLANNING_CENTER_SECRET = os.getenv('PLANNING_CENTER_SECRET')

def test_api_connection():
    """Test basic API connection and retrieve organization info"""

    print("=" * 80)
    print("Testing Planning Center API Connection")
    print("=" * 80)

    # Base URL for Planning Center Services API
    base_url = "https://api.planningcenteronline.com/services/v2"

    # Set up authentication
    auth = (PLANNING_CENTER_APP_ID, PLANNING_CENTER_SECRET)

    try:
        # Test 1: Get organization info
        print("\n1. Fetching organization information...")
        response = requests.get(base_url, auth=auth)
        response.raise_for_status()

        print(f"   ✓ API connection successful!")
        print(f"   Status Code: {response.status_code}")

        # Test 2: Get service types
        print("\n2. Fetching service types...")
        service_types_url = f"{base_url}/service_types"
        response = requests.get(service_types_url, auth=auth)
        response.raise_for_status()

        data = response.json()
        service_types = data.get('data', [])

        if service_types:
            print(f"   ✓ Found {len(service_types)} service type(s):")
            print()
            for st in service_types:
                st_id = st['id']
                st_name = st['attributes']['name']
                print(f"   ID: {st_id}")
                print(f"   Name: {st_name}")
                print(f"   ---")
        else:
            print("   ⚠ No service types found")

        # Test 3: Get recent plans
        if service_types:
            print("\n3. Fetching recent plans for first service type...")
            first_service_type_id = service_types[0]['id']
            plans_url = f"{base_url}/service_types/{first_service_type_id}/plans"
            params = {
                'filter': 'future',
                'order': 'sort_date',
                'per_page': 5
            }
            response = requests.get(plans_url, auth=auth, params=params)
            response.raise_for_status()

            data = response.json()
            plans = data.get('data', [])

            if plans:
                print(f"   ✓ Found {len(plans)} upcoming plan(s):")
                print()
                for plan in plans:
                    plan_id = plan['id']
                    plan_title = plan['attributes'].get('title', 'Untitled')
                    plan_date = plan['attributes'].get('sort_date', 'No date')
                    series_title = plan['attributes'].get('series_title', 'No series')
                    print(f"   ID: {plan_id}")
                    print(f"   Title: {plan_title}")
                    print(f"   Date: {plan_date}")
                    print(f"   Series: {series_title}")
                    print(f"   ---")
            else:
                print("   ⚠ No upcoming plans found")

        print("\n" + "=" * 80)
        print("Configuration Summary")
        print("=" * 80)

        if service_types:
            print(f"\n✓ Add this to your .env file:")
            print(f"  PLANNING_CENTER_SERVICE_TYPE_ID={service_types[0]['id']}")
            print(f"\nNote: You can choose a different service type ID from the list above if needed.")

        print("\n✓ API credentials are working correctly!")
        print("=" * 80)

    except requests.exceptions.HTTPError as e:
        print(f"\n✗ HTTP Error: {e}")
        print(f"  Status Code: {e.response.status_code}")
        print(f"  Response: {e.response.text}")
    except Exception as e:
        print(f"\n✗ Error: {e}")

if __name__ == "__main__":
    if not PLANNING_CENTER_APP_ID or not PLANNING_CENTER_SECRET:
        print("Error: Missing Planning Center credentials in .env file")
        exit(1)

    test_api_connection()
