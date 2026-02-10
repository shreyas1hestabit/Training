#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Step 1: Stop any running prod containers
echo "Stopping old prod containers..."
docker compose --profile prod down

# Step 2: Build and start containers in detached mode
echo "Building and starting prod stack..."
docker compose --profile prod up -d --build

# Step 3: Show status
echo "Prod stack is running!"
docker ps
