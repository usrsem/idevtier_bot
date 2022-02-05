#!/usr/bin/env bash
echo "Commands: [deploy, logs, bash]"

project_name="idevtier_bot"
repo_name="idevtier/idevtier_bot"

if [ "$1" = "deploy" ]; then
    sudo docker stop "$project_name"
    sudo docker rm "$project_name"
    sudo docker build -t $repo_name .
    sudo docker run -d  --log-opt max-size=10m --log-opt max-file=1 --name "$project_name" $repo_name
    sudo docker logs -f --tail 100 "$project_name"
fi

if [ "$1" = "logs" ]; then
    sudo docker logs -f --tail 100 "$project_name"
fi

if [ "$1" = "bash" ]; then
    sudo docker exec -it "$project_name" bash
fi
