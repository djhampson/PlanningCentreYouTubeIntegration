#!/usr/bin/env python3
"""
Create YouTube Live Stream from Planning Center service data

This script:
1. Queries Planning Center for the next Sunday service
2. Extracts sermon title, series, and Bible readings
3. Creates a scheduled YouTube Live Stream for 4pm on that Sunday
"""

import os
import sys
import requests
from datetime import datetime
from dotenv import load_dotenv
from dateutil import parser as date_parser

# Load environment variables
load_dotenv()

# Planning Center Configuration
PLANNING_CENTER_APP_ID = os.getenv('PLANNING_CENTER_APP_ID')
PLANNING_CENTER_SECRET = os.getenv('PLANNING_CENTER_SECRET')
SERVICE_TYPE_ID = os.getenv('PLANNING_CENTER_SERVICE_TYPE_ID')

# Service Configuration
CHURCH_NAME = os.getenv('CHURCH_NAME', 'Southside Anglican')
SERVICE_TIME = os.getenv('SERVICE_TIME', '16:00')
TIMEZONE = os.getenv('TIMEZONE', 'Australia/Sydney')

# API Base URL
BASE_URL = "https://api.planningcenteronline.com/services/v2"


class PlanningCenterClient:
    """Client for interacting with Planning Center API"""

    def __init__(self, app_id, secret):
        self.auth = (app_id, secret)
        self.base_url = BASE_URL

    def get_next_sunday_service(self, service_type_id):
        """Get the next Sunday service plan"""
        url = f"{self.base_url}/service_types/{service_type_id}/plans"
        params = {
            'filter': 'future',
            'order': 'sort_date',
            'per_page': 10
        }

        response = requests.get(url, auth=self.auth, params=params)
        response.raise_for_status()

        plans = response.json().get('data', [])

        # Find the next Sunday
        for plan in plans:
            plan_date_str = plan['attributes'].get('sort_date')
            if plan_date_str:
                plan_date = date_parser.parse(plan_date_str)
                # Check if it's a Sunday (weekday() returns 6 for Sunday)
                if plan_date.weekday() == 6:
                    return plan

        return None

    def get_plan_items(self, service_type_id, plan_id):
        """Get all items for a specific plan"""
        url = f"{self.base_url}/service_types/{service_type_id}/plans/{plan_id}/items"

        response = requests.get(url, auth=self.auth)
        response.raise_for_status()

        return response.json().get('data', [])

    def extract_service_details(self, plan, items):
        """
        Extract sermon title, series, and Bible readings from plan and items

        Returns:
            dict with keys: sermon_title, sermon_series, bible_reading, service_date
        """
        # Get basic plan details
        sermon_title = plan['attributes'].get('title', 'Untitled')
        sermon_series = plan['attributes'].get('series_title', 'General')
        service_date_str = plan['attributes'].get('sort_date')
        service_date = date_parser.parse(service_date_str) if service_date_str else None

        # Look for Bible readings in items
        bible_reading = None
        for item in items:
            item_title = item['attributes'].get('title', '').lower()
            item_description = item['attributes'].get('description', '')

            # Check if this item contains readings
            if 'reading' in item_title or item_title == 'readings':
                if item_description:
                    # Clean up the readings format
                    readings = item_description.strip().replace('\n', ', ')
                    bible_reading = readings
                    break

        # If no specific readings found, use a default
        if not bible_reading:
            bible_reading = "TBA"

        return {
            'sermon_title': sermon_title,
            'sermon_series': sermon_series,
            'bible_reading': bible_reading,
            'service_date': service_date
        }


def format_youtube_title(service_date, sermon_series, bible_reading, sermon_title):
    """
    Format the YouTube stream title

    Format: Southside Anglican - <Service Date> - <Sermon Series> - <Bible Reading> - <Sermon Title>
    """
    date_str = service_date.strftime('%d %B %Y')  # e.g., "11 January 2026"

    title = f"{CHURCH_NAME} - {date_str} - {sermon_series} - {bible_reading} - {sermon_title}"

    return title


def create_youtube_stream(title, scheduled_start_time):
    """
    Create a YouTube Live Stream (placeholder - requires YouTube API setup)

    Args:
        title: The stream title
        scheduled_start_time: datetime object for when to schedule the stream
    """
    print("\n" + "=" * 80)
    print("YouTube Live Stream Creation")
    print("=" * 80)
    print(f"\nTitle: {title}")
    print(f"Scheduled Start: {scheduled_start_time}")
    print("\nNote: YouTube API integration not yet implemented.")
    print("To complete this, you need to:")
    print("1. Set up YouTube Data API v3 credentials")
    print("2. Download OAuth client secret JSON")
    print("3. Implement OAuth flow and API calls")
    print("=" * 80)

    # TODO: Implement YouTube API integration
    # This would use google-api-python-client to:
    # 1. Authenticate with OAuth 2.0
    # 2. Call liveBroadcasts.insert to create the broadcast
    # 3. Call liveStreams.insert to create the stream
    # 4. Bind the broadcast to the stream

    return None


def main():
    """Main function to orchestrate the process"""
    print("=" * 80)
    print("Planning Center to YouTube Live Stream Creator")
    print("=" * 80)

    # Validate configuration
    if not PLANNING_CENTER_APP_ID or not PLANNING_CENTER_SECRET:
        print("\nError: Missing Planning Center credentials in .env file")
        sys.exit(1)

    if not SERVICE_TYPE_ID:
        print("\nError: Missing PLANNING_CENTER_SERVICE_TYPE_ID in .env file")
        sys.exit(1)

    # Initialize Planning Center client
    pc_client = PlanningCenterClient(PLANNING_CENTER_APP_ID, PLANNING_CENTER_SECRET)

    try:
        # Step 1: Get next Sunday service
        print("\n1. Fetching next Sunday service from Planning Center...")
        plan = pc_client.get_next_sunday_service(SERVICE_TYPE_ID)

        if not plan:
            print("   ✗ No upcoming Sunday service found")
            sys.exit(1)

        plan_id = plan['id']
        print(f"   ✓ Found plan: {plan['attributes'].get('title')} (ID: {plan_id})")

        # Step 2: Get plan items
        print("\n2. Fetching service items...")
        items = pc_client.get_plan_items(SERVICE_TYPE_ID, plan_id)
        print(f"   ✓ Found {len(items)} items")

        # Step 3: Extract sermon details
        print("\n3. Extracting sermon details...")
        details = pc_client.extract_service_details(plan, items)

        print(f"   Sermon Title: {details['sermon_title']}")
        print(f"   Sermon Series: {details['sermon_series']}")
        print(f"   Bible Reading: {details['bible_reading']}")
        print(f"   Service Date: {details['service_date'].strftime('%A, %d %B %Y')}")

        # Step 4: Format YouTube title
        print("\n4. Formatting YouTube stream title...")
        youtube_title = format_youtube_title(
            details['service_date'],
            details['sermon_series'],
            details['bible_reading'],
            details['sermon_title']
        )
        print(f"   ✓ Title: {youtube_title}")

        # Step 5: Create YouTube stream
        print("\n5. Creating YouTube Live Stream...")
        # Combine service date with service time
        scheduled_time = details['service_date'].replace(
            hour=int(SERVICE_TIME.split(':')[0]),
            minute=int(SERVICE_TIME.split(':')[1])
        )

        create_youtube_stream(youtube_title, scheduled_time)

        print("\n" + "=" * 80)
        print("Process completed!")
        print("=" * 80)

    except requests.exceptions.HTTPError as e:
        print(f"\n✗ HTTP Error: {e}")
        print(f"  Status Code: {e.response.status_code}")
        print(f"  Response: {e.response.text}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
