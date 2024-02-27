#!/bin/bash

# Check if the file path is provided as an argument
if [ $# -ne 1 ]; then
    echo "Usage: $0 <video_file>"
    exit 1
fi

# Path to the video file provided as argument
VIDEO_FILE="$1"

# Check if the video file exists
if [ ! -f "$VIDEO_FILE" ]; then
    echo "Error: File '$VIDEO_FILE' not found."
    exit 1
fi

# Command to play video in VLC in full screen on loop without showing the title
vlc --fullscreen --loop --no-video-title-show "$VIDEO_FILE"
