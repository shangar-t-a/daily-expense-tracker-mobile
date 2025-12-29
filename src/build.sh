#!/usr/bin/env bash
set -e

echo "Python version:"
python3 --version

echo "Cleaning Buildozer artifacts..."
buildozer android clean || true
rm -rf .buildozer
rm -rf ~/.buildozer/android/platform/build-arm64-v8a
rm -rf ~/.buildozer/android/platform/python-for-android

echo "Building APK..."
buildozer -v android debug
