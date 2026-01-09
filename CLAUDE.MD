# PlanningCentre YouTube Integration

## Project Overview

This project provides a Python script that automatically creates YouTube Live Stream events based on upcoming Sunday services from Planning Center.

## Workflow

The script performs the following steps:

1. **Query Planning Center** - Find the next Sunday Service for Southside Anglican Church
2. **Query Service Items** - Retrieve all planned items for that service
3. **Extract Service Details** - Determine:
   - Sermon Title
   - Sermon Series
   - Bible Reading
4. **Create YouTube Live Stream** - Schedule a YouTube Live Stream for 4pm on that Sunday

## YouTube Stream Title Format

```
Southside Anglican - <Service Date> - <Sermon Series> - <Bible Reading> - <Sermon Title>
```

### Example
```
Southside Anglican - 12 January 2026 - New Beginnings - Romans 12:1-2 - Living Sacrifices
```

## API References

### Planning Center API
- Documentation: https://developer.planning.center/docs/#/overview/
- Authentication: OAuth 2.0 or Personal Access Token
- Endpoints needed:
  - Service Types
  - Plans
  - Plan Items

### YouTube Data API v3
- Documentation: https://developers.google.com/youtube/v3
- Authentication: OAuth 2.0
- Endpoints needed:
  - `liveBroadcasts.insert` - Create scheduled live stream
  - `liveStreams.insert` - Create stream settings

## Implementation Status

✅ **COMPLETE** - All functionality implemented and tested

## Requirements

- Python 3.8+
- Planning Center API credentials (Personal Access Token)
- YouTube Data API v3 OAuth 2.0 credentials
- Required Python packages:
  - `requests` - Planning Center API calls
  - `python-dotenv` - Environment variable management
  - `python-dateutil` - Date parsing and handling
  - `google-auth` - Google authentication
  - `google-auth-oauthlib` - OAuth flow handling
  - `google-auth-httplib2` - HTTP library for Google APIs
  - `google-api-python-client` - YouTube Data API client

## Configuration Files

### `.env`
Environment variables for credentials and settings:
- `PLANNING_CENTER_APP_ID` - Personal Access Token App ID
- `PLANNING_CENTER_SECRET` - Personal Access Token Secret
- `PLANNING_CENTER_ORG_ID` - Organization ID (419566)
- `PLANNING_CENTER_SERVICE_TYPE_ID` - Service Type ID (1293240 for Contemporary Service)
- `CHURCH_NAME` - Church name for titles (Southside Anglican)
- `SERVICE_TIME` - Service time in 24h format (16:00)
- `TIMEZONE` - Timezone (Australia/Sydney)
- `YOUTUBE_CLIENT_SECRETS_FILE` - Path to OAuth credentials (client_secret.json)

### `client_secret.json`
YouTube OAuth 2.0 credentials (Desktop app type)

### `token.pickle`
Saved YouTube authentication token (auto-generated on first run)

## Technical Implementation

### Planning Center Integration

**Class: `PlanningCenterClient`**

Methods:
- `get_next_sunday_service(service_type_id)` - Queries future plans and finds the next Sunday
  - Uses filter='future' and order='sort_date'
  - Checks weekday() == 6 for Sunday
- `get_plan_items(service_type_id, plan_id)` - Retrieves all items for a plan
- `extract_service_details(plan, items)` - Extracts sermon details
  - Sermon title from plan attributes
  - Series from plan attributes
  - Bible readings from items with "reading" in title

### YouTube Integration

**Function: `get_youtube_service()`**
- Handles OAuth 2.0 authentication
- Checks for saved credentials in token.pickle
- Refreshes expired tokens automatically
- Launches browser for initial authentication
- Returns authenticated YouTube API service

**Function: `create_youtube_stream(title, scheduled_start_time, description)`**
- Creates live broadcast with `liveBroadcasts().insert()`
  - Sets privacy to public
  - Configures auto-start, auto-stop, DVR, recording
  - Sets scheduled start time
- Creates stream endpoint with `liveStreams().insert()`
  - RTMP ingestion type
  - Variable resolution and framerate
- Binds broadcast to stream with `liveBroadcasts().bind()`
- Returns watch URL, stream key, and ingestion address

### Data Flow

```
Planning Center API
    ↓
[Get Next Sunday Service]
    ↓
[Get Service Items]
    ↓
[Extract Sermon Details]
    ↓
[Format YouTube Title]
    ↓
YouTube Data API
    ↓
[Create Broadcast + Stream]
    ↓
[Return Watch URL]
```

## Files in Project

- `create_youtube_stream.py` - Main script
- `test_planning_center.py` - Test Planning Center API connection
- `check_all_services.py` - Check all service types for plans
- `check_plan_items.py` - Inspect specific plan items
- `requirements.txt` - Python dependencies
- `.env` - Configuration (not committed)
- `client_secret.json` - YouTube OAuth credentials (not committed)
- `token.pickle` - Saved auth token (not committed)
- `.gitignore` - Ignore sensitive files
- `.env.example` - Template for configuration
- `README.md` - User documentation
- `CLAUDE.MD` - Technical documentation (this file)

## Error Handling

- HTTP errors from APIs are caught and displayed with status codes
- Missing credentials cause early exit with helpful messages
- YouTube API errors show detailed error information
- No Sunday service found exits gracefully
- Token refresh happens automatically

## Development Notes

- Branch: `claude/fetch-sunday-service-script-MSN65`
- All sensitive credentials are gitignored
- OAuth token is persisted to avoid re-authentication
- Script handles both Communion Service (1290793) and Contemporary Service (1293240)
- Timezone handling ensures correct scheduling
- Bible readings parsed from item descriptions
