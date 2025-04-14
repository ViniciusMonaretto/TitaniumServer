#!/bin/bash

# Name of your Docker container
CONTAINER_NAME="my-python-angular-container"

echo "🛑 Stopping container..."
docker stop $CONTAINER_NAME 2>/dev/null

echo "🧹 Removing container..."
docker rm $CONTAINER_NAME 2>/dev/null

echo "✅ Container '$CONTAINER_NAME' stopped and removed."
