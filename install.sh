#!/bin/bash

echo "Cloning pico-lib..."
if [ -d "pico-lib" ]; then
    echo "Removing existing pico-lib directory..."
    rm -rf pico-lib
fi
git clone https://gitlab.metropolia.fi/lansk/pico-lib.git
if [ $? -ne 0 ]; then
    echo "Failed to clone pico-lib"
    exit 1
fi

# Copy required files from pico-lib to lib
mkdir -p lib/umqtt
cp pico-lib/*.py lib/
cp pico-lib/*.mpy lib/
cp pico-lib/umqtt/*.mpy lib/umqtt/

echo "Starting installation to Pico..."
# Start web server in current directory (project root)
python -m http.server &
WEB_SERVER_PID=$!

# Wait a moment for the server to start
sleep 2

# Find the Pico device
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    DEVICE=$(ls /dev/cu.usbmodem* 2>/dev/null | head -n 1)
else
    # Linux
    DEVICE=$(ls /dev/ttyACM* 2>/dev/null | head -n 1)
fi

if [ -z "$DEVICE" ]; then
    echo "No Pico device found"
    kill $WEB_SERVER_PID
    rm -rf pico-lib
    exit 1
fi

echo "Device: $DEVICE"

# Install all files according to package.json structure
python -m mpremote connect $DEVICE mip install --target / http://localhost:8000/

# Stop the web server
kill $WEB_SERVER_PID

# Clean up
echo "Cleaning up..."
rm -rf pico-lib