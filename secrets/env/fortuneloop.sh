#!/bin/bash

trap "exit" SIGINT

mkdir /var/htdocs

while true; do
    /usr/games/fortune > /var/htdocs/index.html
    sleep $INTERVAL
done
