#!/bin/bash

# Configuration
DOCKER_COMPOSE_DIR="server"

echo "🚀 Starting IoCloud Titanium Server Docker Compose Services..."

# Step 1: Start MongoDB and Mosquitto services using docker-compose
echo "📦 Starting MongoDB and Mosquitto services..."
cd $DOCKER_COMPOSE_DIR
docker compose up -d
cd ..

# Step 2: Wait a moment for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 5

echo "✅ Docker Compose services are running!"
echo "📊 MongoDB: localhost:27017"
echo "📡 MQTT: localhost:1883"
echo "🌐 MQTT WebSocket: localhost:9001"
echo ""
echo "📋 Running containers:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo "💡 To stop the services, run: cd $DOCKER_COMPOSE_DIR && docker-compose down"
echo "💡 To view logs, run: cd $DOCKER_COMPOSE_DIR && docker-compose logs -f" 
