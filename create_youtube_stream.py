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
import pickle
from datetime import datetime, timezone
from dotenv import load_dotenv
from dateutil import parser as date_parser
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

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

# YouTube Configuration
YOUTUBE_CLIENT_SECRETS_FILE = os.getenv('YOUTUBE_CLIENT_SECRETS_FILE', 'client_secret.json')
YOUTUBE_TOKEN_FILE = 'token.pickle'
YOUTUBE_SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
YOUTUBE_PRIVACY_STATUS = os.getenv('YOUTUBE_PRIVACY_STATUS', 'public').lower()

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


def generate_bible_gateway_links(bible_reading):
    """
    Generate Bible Gateway links for Bible readings

    Args:
        bible_reading: String containing Bible readings (e.g., "Psalm 77, Hebrews 10:19-25")

    Returns:
        List of tuples: [(passage_name, url), ...]
    """
    import urllib.parse

    if not bible_reading or bible_reading == "TBA":
        return []

    # Split by comma to handle multiple readings
    readings = [r.strip() for r in bible_reading.split(',')]

    links = []
    for reading in readings:
        if reading:
            # URL encode the passage
            encoded_passage = urllib.parse.quote(reading)
            # Create Bible Gateway URL with NIV translation
            url = f"https://www.biblegateway.com/passage/?search={encoded_passage}&version=NIV"
            links.append((reading, url))

    return links


def get_youtube_service():
    """
    Authenticate and return YouTube API service

    Returns:
        YouTube API service object
    """
    creds = None

    # Check if we have saved credentials
    if os.path.exists(YOUTUBE_TOKEN_FILE):
        with open(YOUTUBE_TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)

    # If no valid credentials, authenticate
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("   Refreshing YouTube credentials...")
            creds.refresh(Request())
        else:
            print("   Starting YouTube OAuth flow...")
            print("   A browser window will open for authentication.")
            flow = InstalledAppFlow.from_client_secrets_file(
                YOUTUBE_CLIENT_SECRETS_FILE, YOUTUBE_SCOPES)
            creds = flow.run_local_server(port=0)

        # Save credentials for future use
        with open(YOUTUBE_TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)
        print("   ✓ YouTube credentials saved")

    return build('youtube', 'v3', credentials=creds)


def create_youtube_stream(title, scheduled_start_time, description=""):
    """
    Create a YouTube Live Stream

    Args:
        title: The stream title
        scheduled_start_time: datetime object for when to schedule the stream
        description: Optional description for the stream

    Returns:
        dict with broadcast_id and stream_url
    """
    print("\n" + "=" * 80)
    print("YouTube Live Stream Creation")
    print("=" * 80)
    print(f"\nTitle: {title}")
    print(f"Scheduled Start: {scheduled_start_time}")

    try:
        # Get YouTube API service
        youtube = get_youtube_service()

        # Convert datetime to ISO 8601 format with timezone
        if scheduled_start_time.tzinfo is None:
            scheduled_start_time = scheduled_start_time.replace(tzinfo=timezone.utc)
        scheduled_start_iso = scheduled_start_time.isoformat()

        # Step 1: Create the broadcast
        print("\n   Creating broadcast...")

        # Validate privacy status
        valid_privacy_statuses = ['public', 'unlisted', 'private']
        privacy_status = YOUTUBE_PRIVACY_STATUS if YOUTUBE_PRIVACY_STATUS in valid_privacy_statuses else 'public'

        broadcast_body = {
            'snippet': {
                'title': title,
                'description': description,
                'scheduledStartTime': scheduled_start_iso,
            },
            'status': {
                'privacyStatus': privacy_status,
                'selfDeclaredMadeForKids': False,
            },
            'contentDetails': {
                'enableAutoStart': True,
                'enableAutoStop': True,
                'enableDvr': True,
                'enableEmbed': True,
                'recordFromStart': True,
            }
        }

        broadcast_response = youtube.liveBroadcasts().insert(
            part='snippet,status,contentDetails',
            body=broadcast_body
        ).execute()

        broadcast_id = broadcast_response['id']
        print(f"   ✓ Broadcast created (ID: {broadcast_id})")

        # Step 2: Create the stream
        print("   Creating stream...")
        stream_body = {
            'snippet': {
                'title': f"Stream for {title}",
            },
            'cdn': {
                'frameRate': 'variable',
                'ingestionType': 'rtmp',
                'resolution': 'variable',
            },
            'contentDetails': {
                'isReusable': False,
            }
        }

        stream_response = youtube.liveStreams().insert(
            part='snippet,cdn,contentDetails',
            body=stream_body
        ).execute()

        stream_id = stream_response['id']
        stream_key = stream_response['cdn']['ingestionInfo']['streamName']
        ingestion_address = stream_response['cdn']['ingestionInfo']['ingestionAddress']

        print(f"   ✓ Stream created (ID: {stream_id})")

        # Step 3: Bind broadcast to stream
        print("   Binding broadcast to stream...")
        youtube.liveBroadcasts().bind(
            part='id,contentDetails',
            id=broadcast_id,
            streamId=stream_id
        ).execute()

        print("   ✓ Broadcast bound to stream")

        # Get the watch URL
        watch_url = f"https://www.youtube.com/watch?v={broadcast_id}"

        print("\n" + "=" * 80)
        print("SUCCESS! YouTube Live Stream Created")
        print("=" * 80)
        print(f"\n✓ Watch URL: {watch_url}")
        print(f"✓ Broadcast ID: {broadcast_id}")
        print(f"✓ Stream ID: {stream_id}")
        print(f"\nStreaming Information:")
        print(f"  Server URL: {ingestion_address}")
        print(f"  Stream Key: {stream_key}")
        print("=" * 80)

        return {
            'broadcast_id': broadcast_id,
            'stream_id': stream_id,
            'watch_url': watch_url,
            'stream_key': stream_key,
            'ingestion_address': ingestion_address
        }

    except HttpError as e:
        print(f"\n✗ YouTube API Error: {e}")
        import json
        error_details = json.loads(e.content)
        print(f"  Details: {error_details}")
        return None
    except Exception as e:
        print(f"\n✗ Error creating YouTube stream: {e}")
        import traceback
        traceback.print_exc()
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

        # Create description
        description_parts = [
            f"Join us for our Sunday service at {CHURCH_NAME}.",
            "",
            f"Sermon: {details['sermon_title']}",
            f"Series: {details['sermon_series']}",
            f"Bible Reading: {details['bible_reading']}",
        ]

        # Add Bible Gateway links
        bible_links = generate_bible_gateway_links(details['bible_reading'])
        if bible_links:
            description_parts.append("")
            description_parts.append("Read along:")
            for passage, url in bible_links:
                description_parts.append(f"  {passage}: {url}")

        description_parts.append("")
        description_parts.append(f"Service Date: {details['service_date'].strftime('%A, %d %B %Y at %I:%M %p')}")

        description = "\n".join(description_parts)

        result = create_youtube_stream(youtube_title, scheduled_time, description)

        if not result:
            print("\n✗ Failed to create YouTube Live Stream")
            sys.exit(1)

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
