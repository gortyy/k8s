#!/bin/bash

kubectl create -f mysql-service.yml
kubectl create -f mysql-deployment.yml

kubectl create -f wordpress-service.yml
kubectl create -f wordpress-deployment.yml

minikube service wordpress --url
