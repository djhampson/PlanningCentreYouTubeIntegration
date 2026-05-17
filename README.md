# PlanningCentre YouTube Integration

Automatically create YouTube Live Stream events for upcoming Sunday services based on Planning Center data.

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Planning Center API

1. Go to https://api.planningcenteronline.com/oauth/applications
2. Create a new Personal Access Token
3. Copy the App ID and Secret

### 3. Configure YouTube API

1. Go to https://console.cloud.google.com/
2. Create a new project (or use existing)
3. Enable YouTube Data API v3
4. Create OAuth 2.0 credentials
5. Download the client secret JSON file as `client_secret.json`

### 4. Set Up Environment Variables

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your credentials:
   - Planning Center App ID and Secret
   - Planning Center Organization ID
   - Planning Center Service Type ID
   - Update church name and timezone if needed

### 5. Run the Script

```bash
python create_youtube_stream.py
```

**First Run:**
- A browser window will open for YouTube OAuth authentication
- Sign in with your Google account that manages your YouTube channel
- Grant the requested permissions
- The credentials will be saved locally for future runs

**Subsequent Runs:**
- The script will use saved credentials automatically
- No browser authentication needed

## What You'll Get

After running the script successfully, you'll receive:

✅ **YouTube Live Stream** scheduled for your next Sunday service at 4pm
✅ **Formatted Title** like: `Southside Anglican - 11 January 2026 - General - Psalm 77, Hebrews 10:19-25 - Holding Fast Together`
✅ **Description** with sermon details and Bible Gateway links (NIV) for easy reading access
✅ **Watch URL** to share with your congregation
✅ **Stream Key** and server details for OBS or other streaming software
✅ **Configurable Privacy** - Set streams as public, unlisted, or private

## Configuration

See `.env.example` for all available configuration options:

- **PLANNING_CENTER_SERVICE_TYPE_ID**: Choose between Communion Service (1290793) or Contemporary Service (1293240)
- **SERVICE_TIME**: Change from default 16:00 (4pm) if needed
- **TIMEZONE**: Adjust for your location (default: Australia/Sydney)
- **CHURCH_NAME**: Customize the church name in titles
- **YOUTUBE_PRIVACY_STATUS**: Set stream visibility - `public`, `unlisted`, or `private` (default: public)

## How It Works

1. **Queries Planning Center** - Fetches the next Sunday service plan
2. **Extracts Details** - Sermon title, series, and Bible readings from service items
3. **Formats Title** - Creates YouTube title: `<Church> - <Date> - <Series> - <Reading> - <Title>`
4. **Creates Stream** - Uses YouTube Data API to:
   - Create a scheduled live broadcast
   - Create a stream endpoint
   - Bind them together
   - Configure settings (DVR, auto-start, recording, etc.)

## Output Example

```
Planning Center to YouTube Live Stream Creator
================================================================================

1. Fetching next Sunday service from Planning Center...
   ✓ Found plan: Holding Fast Together (ID: 85232838)

2. Fetching service items...
   ✓ Found 22 items

3. Extracting sermon details...
   Sermon Title: Holding Fast Together
   Sermon Series: General
   Bible Reading: Psalm 77, Hebrews 10:19-25
   Service Date: Sunday, 11 January 2026

4. Formatting YouTube stream title...
   ✓ Title: Southside Anglican - 11 January 2026 - General - Psalm 77, Hebrews 10:19-25 - Holding Fast Together

5. Creating YouTube Live Stream...
   ✓ Broadcast created
   ✓ Stream created
   ✓ Broadcast bound to stream

SUCCESS! YouTube Live Stream Created
✓ Watch URL: https://www.youtube.com/watch?v=...
✓ Stream Key and server details provided
```

## Troubleshooting

**No upcoming Sunday found:**
- Check that your PLANNING_CENTER_SERVICE_TYPE_ID is correct
- Verify there are plans scheduled in Planning Center

**YouTube authentication fails:**
- Ensure you've added your email as a test user in OAuth consent screen
- Check that YouTube Data API v3 is enabled in your Google Cloud project

**Missing Bible readings:**
- Script looks for items titled "Readings" or containing "reading"
- Ensure readings are in the item description, not just the title

## Documentation

See [CLAUDE.MD](CLAUDE.MD) for detailed technical documentation.
