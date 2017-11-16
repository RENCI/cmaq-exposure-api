#!/usr/bin/env bash

docker-compose stop database
docker-compose rm -f database
if [[ "${1}" == '--all' ]]; then
    docker rmi -f postgres96_database
    docker rmi -f centos:7
fi

exit 0;
