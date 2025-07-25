#!/bin/bash

# Configuration
IMAGE_NAME="titanium-server"
CONTAINER_NAME="titanium-server-container"
PORT=8888
DOCKER_COMPOSE_DIR="server"

echo "🚀 Starting IoCloud Titanium Server..."

# Step 1: Start MongoDB and Mosquitto services using docker-compose
echo "📦 Starting MongoDB and Mosquitto services..."
cd $DOCKER_COMPOSE_DIR
docker-compose up -d
cd ..

# Step 2: Wait a moment for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 5

# Step 3: Build the Docker image
echo "🔨 Building Docker image..."
docker build -t $IMAGE_NAME .

# Step 4: Stop and remove any existing container with the same name
if [ "$(docker ps -aq -f name=$CONTAINER_NAME)" ]; then
    echo "🧹 Removing old container..."
    docker rm -f $CONTAINER_NAME
fi

# Step 5: Run the container with proper network configuration
echo "🚀 Running Titanium Server container..."
docker run -d --name $CONTAINER_NAME -p $PORT:$PORT --network server_default $IMAGE_NAME

# Step 6: Wait for the application to start
echo "⏳ Waiting for application to start..."
sleep 3

echo "✅ IoCloud Titanium Server is running!"
echo "🌐 Web Interface: http://localhost:$PORT"
echo "📊 MongoDB: localhost:27017"
echo "📡 MQTT: localhost:1883"
echo ""
echo "📋 Running containers:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
