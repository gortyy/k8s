# Kubernetes Knowledge Base

## Minikube installation

```shell
brew cask install minikube
brew install kubernetes-cli
```

## Starting minikube

```shell
minikube start
```

Containers:
*  their function is to keep software separated into its own clean view of an operating system
*  virtual machines & direct installations were their predecessors
*  vendored by Docker/rkt and others (however Docker is dominating the market)

Containers orchestration:
*  defines relationships between containers, from scaling to connecting to the outer world
*  before container orchestration became a thing people used homegrown scripts or manual configuration between containers
*  vendored by Kubernetes/Docker Swarm/AWS ECS/Mesos

Containers orchestration is still evolving. In this setting Kubernets is the most advanced technology. Most of the cloud services offer native support for Kubernetes (even Docker Swarm announced support for k8s-like orchestration configuration).

Kubernetes story:
*  originated from Google's "Borg" in mid 2014
*  versin 1.0 released in 2015
*  Google worked together with Linux Foundation to form Cloud Native Computing Foundation (CNCF) to offer Kubernetes as open source product
*  Kubernetes is frequently abbreviated to k8s

Kubernetes advantages:
*  built in Google based on their experience with Borg, tested on high-loads
*  vast community
*  it offers auto-scaling and is cloud-agnostic
*  it runs on Linux


https://cloud.google.com/kubernetes-engine/
https://aws.amazon.com/eks/
https://azure.microsoft.com/en-us/services/kubernetes-service/
