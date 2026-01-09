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

## Requirements

- Python 3.8+
- Planning Center API credentials
- YouTube Data API credentials
- Required Python packages (TBD):
  - requests / httpx for API calls
  - google-auth / google-api-python-client for YouTube
  - python-dateutil for date handling

## Configuration

The script will need:
- Planning Center API credentials (App ID and Secret)
- YouTube API credentials (OAuth client credentials)
- Church organization details (Planning Center Organization ID)
- Service type identifier in Planning Center

## Development Notes

- All code should be developed on branch: `claude/fetch-sunday-service-script-MSN65`
- Script should handle edge cases (no sermon found, multiple services, etc.)
- Include proper error handling and logging
- Consider timezone handling for service dates
