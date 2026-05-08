#!/bin/bash
set -e

IMAGE_TAG=${1:-latest}
ECR_REGISTRY=${2:?"ECR_REGISTRY is required"}
CONTAINER_NAME="adtech-pipeline"

echo "Deploying image: $ECR_REGISTRY:$IMAGE_TAG"

aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin "$ECR_REGISTRY"

if [ "$(docker ps -aq -f name=$CONTAINER_NAME)" ]; then
    echo "Stopping and removing old container..."
    docker rm -f "$CONTAINER_NAME"
fi

echo "Pulling image..."
docker pull "$ECR_REGISTRY:$IMAGE_TAG"

echo "Starting new container..."
docker run -d --name "$CONTAINER_NAME" -p 8000:8000 "$ECR_REGISTRY:$IMAGE_TAG"

echo "Deployment finished successfully!"
