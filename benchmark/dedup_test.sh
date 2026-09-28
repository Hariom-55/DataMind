#!/usr/bin/env bash
# dedup_test.sh (v3 — multipart file upload, matches the real /api/datasets endpoint)
# Measures: response time for a FIRST upload (new file, full processing path)
# vs a REPEAT upload of the SAME file content (should hit server-side dedup by content hash).
#
# Usage: ./dedup_test.sh [BASE_URL] [FILE_PATH]

set -euo pipefail
BASE_URL="${1:-http://localhost:8080}"
FILE_PATH="${2:-sample-data.csv}"

if [ ! -f "$FILE_PATH" ]; then
  echo "File not found: $FILE_PATH"
  echo "Pass a real file path, or keep sample-data.csv next to this script."
  exit 1
fi

echo "== First upload (new dataset): $FILE_PATH =="
FIRST_TIME=$(curl -s -o /tmp/dedup_first.json -w "%{time_total}" \
  -X POST "${BASE_URL}/api/datasets" \
  -F "file=@${FILE_PATH}")
echo "First upload time: ${FIRST_TIME}s"
echo "Response: $(cat /tmp/dedup_first.json)"

sleep 1

echo ""
echo "== Repeat upload (same file, should hit dedup path) =="
REPEAT_TIME=$(curl -s -o /tmp/dedup_repeat.json -w "%{time_total}" \
  -X POST "${BASE_URL}/api/datasets" \
  -F "file=@${FILE_PATH}")
echo "Repeat upload time: ${REPEAT_TIME}s"
echo "Response: $(cat /tmp/dedup_repeat.json)"

echo ""
echo "== Result =="
python3 -c "
first = float('${FIRST_TIME}')
repeat = float('${REPEAT_TIME}')
if repeat > 0:
    print(f'Speedup: {first/repeat:.1f}x faster on repeat upload')
print(f'First: {first*1000:.0f}ms | Repeat: {repeat*1000:.0f}ms')
" 2>/dev/null || echo "First: ${FIRST_TIME}s | Repeat: ${REPEAT_TIME}s"

echo ""
echo "Check the two response bodies above manually:"
echo "  - Do they return the SAME dataset id? -> dedup is working"
echo "  - Different ids? -> dedup by content hash is NOT triggering on file upload, worth investigating"
echo ""
echo "Run this 10x and average both columns for a stable resume number."
