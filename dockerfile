# Use an official Python runtime as the base image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the server and requirements
COPY ./server .
COPY ./requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy Angular build files into the container
COPY web/webApp/dist/web-app ./webApp

# Expose the port the server runs on
EXPOSE 8888

# Set environment variables for database and MQTT connections
ENV MONGO_HOST=my-mongo
ENV MONGO_PORT=27017
ENV MONGO_USER=root
ENV MONGO_PASSWORD=example
ENV MQTT_HOST=my-mosquitto
ENV MQTT_PORT=1883

# Command to run the Tornado server
CMD ["python3", "main.py"]
