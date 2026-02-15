#!/usr/bin/env bash
set -euo pipefail

# Example: convert MP4 to HLS segments for production CDN workflows.
# Usage: ./hls_pack_example.sh input.mp4 output_dir

INPUT="$1"
OUT_DIR="$2"
mkdir -p "$OUT_DIR"

ffmpeg -i "$INPUT" \
  -codec: copy \
  -start_number 0 \
  -hls_time 6 \
  -hls_list_size 0 \
  -f hls "$OUT_DIR/index.m3u8"

echo "HLS generated at $OUT_DIR/index.m3u8"
