#!/usr/bin/env bash


docker-compose -f ubuntu-docker-compose.yml kill
docker rm -f $(docker ps -aq --filter status=exited)

docker-compose -f ubuntu-docker-compose.yml up -d

