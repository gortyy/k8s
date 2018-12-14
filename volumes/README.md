# Volumes

On-disk files in a container are ephemeral, which presents some problems for non-trivial applications when running in containers. First, when a container crashes, kubelet will restart it, but the files will be lost - the container starts with a clean state. Second, when running containers together in a pod it is often necessary to share files between those containers. The Kubernetes Volume abstraction solves both of these problems.

## Overview

Docker has volume concept aswell, but it's less managed than the Kubernetes one. In Docker, volume is a directory that gets mounted to the running container. A Kubernetes volume, on the other hand, has an explicit lifetime - the same as the Pod that encloses it. Consequently, a volume outlives any containers that run within the pod, and data is preserved across container restarts. Of course, when a pod ceases to exist, the volume will cease to exist, too. Perhaps more importantly than this, Kubernetes supports many types of volumes, and a pod can use any number of them simultaneously.

To use a volume, a pod specifies what volumes to provide for the pod (the .spec.volumes field) and where to mount those into containers (the .spec.containers.volumeMounts field).

## ConfigMap Example

https://github.com/appoptics/appoptics-agent-docker#configuration
