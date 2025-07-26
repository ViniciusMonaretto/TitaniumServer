#!/bin/bash

# 🔧 Configuration variables
IMAGE_NAME="angular-builder"
CONTAINER_NAME="angular-builder-container"

# 🛠️ Build the Docker image using the specified Dockerfile and show detailed progress
echo "🔨 Building Docker image..."
docker build \
  -f ./scripts/helper/Dockerfile \
  --progress=plain \
  -t $IMAGE_NAME .

# 🧹 Remove any existing container with the same name to avoid conflicts
if [ "$(docker ps -aq -f name=$CONTAINER_NAME)" ]; then
    echo "🧹 Removing old container..."
    docker rm -f $CONTAINER_NAME
fi

# 🚀 Run the container, mounting the current directory to /app inside the container
echo "🚀 Running container to build frontend..."
docker run --rm --name $CONTAINER_NAME \
  -v "$PWD":/app \
  $IMAGE_NAME
