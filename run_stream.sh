#!/bin/bash
#cd "/Users/southsideanglican/Library/CloudStorage/Dropbox/LocalDev/PlanningCentreYouTubeIntegration/PlanningCentreYouTubeIntegration"
source venv/bin/activate

OUTPUT=$(python3 create_youtube_stream.py 2>&1)
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    WATCH_URL=$(echo "$OUTPUT" | grep "Watch URL:" | sed 's/.*Watch URL: //')
    terminal-notifier -title "YouTube Stream" -message "Stream scheduled! Click to open." -open "$WATCH_URL" -sound "Glass"
elif echo "$OUTPUT" | grep -q "Duplicate stream already exists"; then
    WATCH_URL=$(echo "$OUTPUT" | grep -o 'https://www.youtube.com/watch?v=[^ ]*' | head -1)
    terminal-notifier -title "YouTube Stream" -message "A stream already exists for this Sunday. Click to open." -open "$WATCH_URL" -sound "Basso"
else
    osascript -e "display alert \"YouTube Stream Failed\" message \"An unexpected error occurred. Check the logs for details.\" as critical"
fi
