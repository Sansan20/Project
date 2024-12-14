#!/bin/bash

docker-compose build
docker-compose up parser
docker-compose up pizza_app
docker-compose up

