#!/bin/sh

# 📁 Navigate to the Angular project directory
cd ./web/webApp

# 🏗️ Start the build process
echo "Build angular app"

# 📦 Install frontend dependencies
echo "📦 Installing dependencies..."
npm install

# 🛠️ Run Angular production build
ng build

# 📁 Move back to the server directory
cd ../../server

# 🧹 Remove previous build artifacts if they exist
rm -rf ./webApp

# 📂 Create a fresh directory for the built frontend
mkdir ./webApp

# 📥 Copy the newly built frontend assets into the server’s webApp directory
cp -r ../web/webApp/dist/web-app/* ./webApp
