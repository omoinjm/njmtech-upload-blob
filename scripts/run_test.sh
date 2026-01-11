#!/bin/bash
set -e

TRANSCRIPT_FILE="/tmp/njmtech-yt-transcribe/transcript.txt"
API_TOKEN="WUHQpsClkPo9GdmUxu7jFhPAWQ1SEdiyR"

curl -X POST \
  -H "Authorization: Bearer $API_TOKEN" \
  -F "file=@${TRANSCRIPT_FILE}" \
  http://localhost:8008/api/v1/blob/upload | jq
