#!/bin/bash

# Path to your video file
VIDEO_FILE="/home/rdk/Downloads/PixelPods/site/v2/static/user_uploads/CanvasDownloader_Taylor_Swift_1708882597471.mp4"

# Command to play video in VLC in full screen on loop
vlc --fullscreen --loop --no-video-title-show "$VIDEO_FILE"
