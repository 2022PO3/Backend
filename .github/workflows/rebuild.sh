cd ~/Backend
echo "Stopping all containers"
docker rm $(docker ps -aq)
echo "Checkout master and pull changes"
git checkout master
git pull
git status
echo "Rebuild Docker images"
docker compose build
echo "Restart Docker images"
docker compose up
echo "All done"
