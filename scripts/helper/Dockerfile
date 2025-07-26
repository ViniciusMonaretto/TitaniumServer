# 🐢 Base image: Use official Node.js v23 image for building the Angular project
FROM node:23

# 📁 Set working directory inside the container
WORKDIR /app

# 🚀 Install Angular CLI globally to enable Angular commands like `ng build`
RUN npm install -g @angular/cli

# 📦 Copy the full project into the container's working directory
COPY . /app

# 📁 Ensure we're in the root directory of the app before running the build
WORKDIR /app

# 🛠️ Default command: execute the frontend build script when the container runs
CMD ["sh", "build_frontend.sh"]
