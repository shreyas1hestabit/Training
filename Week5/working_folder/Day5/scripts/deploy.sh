# #!/bin/bash

# # Exit immediately if a command exits with a non-zero status
# set -e

# # Step 1: Stop any running prod containers
# echo "Stopping old prod containers..."
# docker compose --profile prod down

# # Step 2: Build and start containers in detached mode
# echo "Building and starting prod stack..."
# docker compose --profile prod up -d --build
# docker compose -f docker-compose.yml --profile prod down
# docker compose -f docker-compose.yml --profile prod up -d --build

# # Step 3: Show status
# echo "Prod stack is running!"
# docker ps

#!/bin/bash
set -e

echo " Starting Production Deployment..."

# Step 1: Shut down existing services to ensure a clean slate
# We combine both files to make sure Docker knows about all defined volumes/networks
docker compose -f docker-compose.yml -f docker-compose.prod.yml --profile prod down

# Step 2: Build and start
# This merges the two files, applies the 'prod' profile, and builds fresh images
echo " Building and starting containers..."
docker compose -f docker-compose.yml -f docker-compose.prod.yml --profile prod up -d --build

# Step 3: Cleanup
echo " Removing dangling images to save space..."
docker image prune -f

# Step 4: Verification
echo " Deployment Complete! Current Status:"
docker ps