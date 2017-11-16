#!/usr/bin/env bash

docker-compose build
docker-compose up -d
echo "Database is running - use your local IP address for connection"

exit 0;
