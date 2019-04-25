#!/bin/bash

trap "exit" SIGINT

INTERVAL=$1

mkdir /var/htdocs

while true; do
    /usr/games/fortune > /var/htdocs/index.html
    sleep $INTERVAL
done
