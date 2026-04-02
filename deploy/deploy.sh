#!/bin/bash
set -e

# Args
IMAGE_TAG=$1
ECR_REGISTRY=$2

echo "Deploying image: $ECR_REGISTRY:$IMAGE_TAG"

# Login no ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $ECR_REGISTRY

# Parar container antigo, se existir
if [ "$(docker ps -aq -f name=ml-pipeline)" ]; then
    echo "Stopping and removing old container..."
    docker rm -f ml-pipeline
fi


echo "Pulling image..."
docker pull $ECR_REGISTRY:$IMAGE_TAG

# Rodar container
echo "Starting new container..."
docker run -d --name ml-pipeline -p 8000:8000 $ECR_REGISTRY:$IMAGE_TAG

echo "✅ Deployment finished successfully!"
