#!/usr/bin/env bash

HOME_DIR=$(pwd)
CLEAR_ALL=false

if [ "$1" = "--clear-all" ]; then
    CLEAR_ALL=true
fi

PS_DATABASE=$(docker ps -a | grep database)
PS_API_SERVER=$(docker ps -a | grep api-server)

if [[ ! -z ${PS_API_SERVER} ]]; then
    cd $HOME_DIR/server
    docker-compose stop api-server
    docker-compose rm -f api-server
    if $CLEAR_ALL; then
        docker rmi -f server_api-server
        docker rmi -f python:3
    fi
    cd $HOME_DIR
fi

if [[ ! -z ${PS_DATABASE} ]]; then
    cd $HOME_DIR/postgres96
    if $CLEAR_ALL; then
        ./stop-database.sh --all
    else
        ./stop-database.sh
    fi
    cd $HOME_DIR
fi

cd $HOME_DIR/postgres96
 ./start-database.sh --load-cmaq

cd $HOME_DIR/server
docker-compose build
docker-compose up -d

echo "CMAQ Exposure API running at: http://localhost:5000/v1/ui/#/default"

exit 0;