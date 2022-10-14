cd ~/Backend
echo "Stopping all containers"
sudo docker rm $(sudo docker ps -aq)
echo "Checkout master and pull changes"
git checkout master
git pull
git status
echo "Rebuild Docker images"
sudo docker compose build
echo "Restart Docker images"
sudo docker compose up
echo "All done"
