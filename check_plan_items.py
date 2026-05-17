#!/usr/bin/env python3
"""
Check plan items for the next Sunday service
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

PLANNING_CENTER_APP_ID = os.getenv('PLANNING_CENTER_APP_ID')
PLANNING_CENTER_SECRET = os.getenv('PLANNING_CENTER_SECRET')
base_url = "https://api.planningcenteronline.com/services/v2"
auth = (PLANNING_CENTER_APP_ID, PLANNING_CENTER_SECRET)

# Check the next Contemporary Service plan
service_type_id = 1293240
plan_id = 85232838  # Holding Fast Together - Jan 11, 2026

print("=" * 80)
print(f"Checking Plan Items for Plan ID: {plan_id}")
print("=" * 80)

# Get plan details
plan_url = f"{base_url}/service_types/{service_type_id}/plans/{plan_id}"
try:
    response = requests.get(plan_url, auth=auth)
    response.raise_for_status()
    plan_data = response.json()['data']

    print(f"\nPlan Details:")
    print(f"  Title: {plan_data['attributes'].get('title', 'N/A')}")
    print(f"  Date: {plan_data['attributes'].get('sort_date', 'N/A')}")
    print(f"  Series: {plan_data['attributes'].get('series_title', 'N/A')}")
    print(f"  Notes: {plan_data['attributes'].get('public_notes', 'N/A')}")

except Exception as e:
    print(f"Error fetching plan: {e}")

# Get plan items
items_url = f"{base_url}/service_types/{service_type_id}/plans/{plan_id}/items"
print(f"\n" + "-" * 80)
print("Plan Items:")
print("-" * 80)

try:
    response = requests.get(items_url, auth=auth)
    response.raise_for_status()

    data = response.json()
    items = data.get('data', [])

    if items:
        print(f"\nFound {len(items)} items:\n")
        for idx, item in enumerate(items, 1):
            item_id = item['id']
            item_title = item['attributes'].get('title', 'Untitled')
            item_description = item['attributes'].get('description', '')
            item_type = item['type']
            sequence = item['attributes'].get('sequence', 0)

            print(f"{idx}. {item_title}")
            print(f"   ID: {item_id}")
            print(f"   Type: {item_type}")
            print(f"   Sequence: {sequence}")
            if item_description:
                print(f"   Description: {item_description}")
            print()
    else:
        print("  No items found\n")

except Exception as e:
    print(f"Error: {e}\n")

print("=" * 80)

# Try to get notes for the plan
print("\nChecking for Plan Notes...")
print("-" * 80)
notes_url = f"{base_url}/service_types/{service_type_id}/plans/{plan_id}/notes"
try:
    response = requests.get(notes_url, auth=auth)
    response.raise_for_status()

    data = response.json()
    notes = data.get('data', [])

    if notes:
        print(f"\nFound {len(notes)} note(s):\n")
        for note in notes:
            category = note['attributes'].get('category_name', 'Uncategorized')
            content = note['attributes'].get('content', '')
            print(f"  Category: {category}")
            print(f"  Content: {content}")
            print()
    else:
        print("  No notes found\n")

except Exception as e:
    print(f"Error: {e}\n")

print("=" * 80)
