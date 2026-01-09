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

On first run, you'll be prompted to authorize the YouTube API access through your browser.

## Configuration

See `.env.example` for all available configuration options.

## How It Works

1. Queries Planning Center for the next Sunday service
2. Extracts sermon title, series, and Bible reading from service items
3. Creates a YouTube Live Stream scheduled for 4pm on that Sunday
4. Formats the title as: `Southside Anglican - <Date> - <Series> - <Reading> - <Title>`

## Documentation

See [CLAUDE.MD](CLAUDE.MD) for detailed technical documentation.
