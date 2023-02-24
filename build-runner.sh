git pull
# docker volume create certmoncerts
docker container rm -f certmon
docker build -t certmon:1.0 .
docker run -d --restart always --name certmon -p 5000:5000  \
    -v certmoncerts:/etc/certmon/instance certmon:1.0

docker rmi -f $(docker images --filter "dangling=true" -q --no-trunc)

#4d7cab49eec3
#docker run -d --name grafana -p 3000:3000 4d7cab49eec3