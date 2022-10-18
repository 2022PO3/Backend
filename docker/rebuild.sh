#!bin/bash
echo "Stopping all containers"
sudo docker stop $(sudo docker ps -aq)
echo "Rebuild Docker images"
sudo docker compose build
echo "Restart Docker images"
sudo docker compose up -d=true
echo "All done"