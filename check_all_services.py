#!/usr/bin/env python3
"""
Check all service types for upcoming plans
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

PLANNING_CENTER_APP_ID = os.getenv('PLANNING_CENTER_APP_ID')
PLANNING_CENTER_SECRET = os.getenv('PLANNING_CENTER_SECRET')
base_url = "https://api.planningcenteronline.com/services/v2"
auth = (PLANNING_CENTER_APP_ID, PLANNING_CENTER_SECRET)

# Service types to check
service_types = [
    (1290793, "Communion Service"),
    (1293240, "Contemporary Service"),
    (1392508, "Special Events"),
    (1474343, "Prayer Meeting"),
    (1703821, "Young Adults")
]

print("=" * 80)
print("Checking all service types for upcoming plans...")
print("=" * 80)

for st_id, st_name in service_types:
    print(f"\n{st_name} (ID: {st_id})")
    print("-" * 80)

    plans_url = f"{base_url}/service_types/{st_id}/plans"
    params = {
        'filter': 'future',
        'order': 'sort_date',
        'per_page': 3
    }

    try:
        response = requests.get(plans_url, auth=auth, params=params)
        response.raise_for_status()

        data = response.json()
        plans = data.get('data', [])

        if plans:
            print(f"✓ Found {len(plans)} upcoming plan(s):\n")
            for plan in plans:
                plan_id = plan['id']
                plan_title = plan['attributes'].get('title', 'Untitled')
                plan_date = plan['attributes'].get('sort_date', 'No date')
                series_title = plan['attributes'].get('series_title', 'No series')
                print(f"  Plan ID: {plan_id}")
                print(f"  Title: {plan_title}")
                print(f"  Date: {plan_date}")
                print(f"  Series: {series_title}")
                print()
        else:
            print("  No upcoming plans found\n")

    except Exception as e:
        print(f"  Error: {e}\n")

print("=" * 80)
