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
COPY web/webApp/dist/web-app /app/dist/webApp

# Expose the port the server runs on
EXPOSE 8888
EXPOSE 3000

# Command to run the Tornado server
CMD ["python3", "main.py"]
