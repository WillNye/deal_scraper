#!/usr/bin/env bash


docker-compose -f mac-docker-compose.yml kill
docker rm -f $(docker ps -aq --filter status=exited)

docker-compose -f mac-docker-compose.yml up -d

