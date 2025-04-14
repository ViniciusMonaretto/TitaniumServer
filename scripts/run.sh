#!/bin/bash

# Name for your Docker image
IMAGE_NAME="my-python-angular-app"
CONTAINER_NAME="my-python-angular-container"
PORT=8888

# Step 1: Build the Docker image
echo "🔨 Building Docker image..."
docker build -t $IMAGE_NAME .

# Step 2: Stop and remove any existing container with the same name
if [ "$(docker ps -aq -f name=$CONTAINER_NAME)" ]; then
    echo "🧹 Removing old container..."
    docker rm -f $CONTAINER_NAME
fi

# Step 3: Run the container
echo "🚀 Running container..."
docker run -d --name $CONTAINER_NAME -p $PORT:$PORT $IMAGE_NAME

echo "✅ App is running at: http://localhost:$PORT"