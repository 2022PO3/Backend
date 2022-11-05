#!/bin/bash

cd ~/Backend
echo 'Stopping all running containers'
docker stop $(docker ps -aq)
echo "Checkout master and pull changes"
git checkout master && git pull
echo "Login to Docker"
docker login
echo "Pull Docker image from DockerHub"
docker pull python1002/django:backend
echo "Restart Docker images"
docker compose up -d=true
echo "All done"