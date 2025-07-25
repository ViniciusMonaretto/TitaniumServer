#!/bin/bash

# Configuration
CONTAINER_NAME="titanium-server-container"
DOCKER_COMPOSE_DIR="server"

echo "🛑 Stopping IoCloud Titanium Server..."

# Step 1: Stop and remove the main application container
echo "🛑 Stopping Titanium Server container..."
docker stop $CONTAINER_NAME 2>/dev/null
docker rm $CONTAINER_NAME 2>/dev/null

# Step 2: Stop MongoDB and Mosquitto services using docker-compose
echo "🛑 Stopping MongoDB and Mosquitto services..."
cd $DOCKER_COMPOSE_DIR
docker-compose down
cd ..

echo "✅ IoCloud Titanium Server stopped successfully!"
echo ""
echo "📋 Remaining containers:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
