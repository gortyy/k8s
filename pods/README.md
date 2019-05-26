# Pods

## Overview

Pod is basic building block (smallest and simplest unit) in Kubernetes object model - it represent process running on cluster. Pod consists of:
*  application container(s)
*  storage resources
*  unique network IP
*  optional configuration for automatic containers management
If you want to scale your application horizontally, then you should run multiple pods with your app. Running multiple pods is usually done with Controller.

## Multiple Containers Management

Pods are able to support multiple containers that form a single service. Containers in pod are automatically run on the same virtual/physical machine. Containers can share resources and communicate via localhost.

### Networking

Each pod is assigned unique IP address. Every container in a pod shares the network namespace, including IP and ports.

### Storage

Pod can specify set of shared storage volumes. Every container in pod can access these volumes - this allows data sharing between containers.

## Working with pods

Single pods are rarely create as they are ephemeral. When pod is created it runs on assigned node until its process is terminated, deleted or node fails (pods are not designed to self-heal). Restarting a container in a pod should not be confused with restarting the pod. The pod itself does not run, but is an environment the containers run in and persists until it is deleted. Kubernetes uses a higher-level abstraction Controllers, that handles the work of managing ephemeral pods (mainly through replication).

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: sample
  labels:
    app: sample
spec:
  containers:
  - name: sample-busybox
    image: busybox
    command: ['sh', '-c', 'echo Hello! && sleep 60']
```

```shell
# Creating pod
kubectl create -f pod-spec.yml
```

### Termination

Because pods represent running processes on nodes it's important to allow graceful shutdown if these processes. When a user requests deletion of a pod, the system records the intended grace period before the pod is allowed to be forcefully killed, and a TERM signal is sent to the main process in each container. Once the grace period has expired, the KILL signal is sent to those processes, and the pod is then deleted from the API server. By default, all deletes are graceful within 30 seconds.

```shell
# Delete pod
kubectl delete pod -f sample

# KILL pod
kubectl delete pod -f sample --grace-period=0 --force
```

## Lifecycle

Pod's `status` field is represented by PodStatus object, which has a phase field:
*  Pending - accepted by Kubernetes but containers are still being created
*  Running - pod has been assigned to node and its processes are starting/running/restarting
*  Succeeded - all processes have ended with success exit code
*  Failed - all processes have terminated
*  Unknown - state of pod cannot be obtained

### Probes

A Probe is a diagnostic performed periodically by the kubelet on a container. The kubelet can optionally perform and react to two kinds of probes on running containers:
*  livenessProbe - whether container is running
*  readinessProbe - whether container is ready to service requests

## Init containers

Pod can have multiple containers running processes within it, but it can also have one or more init containers which are run before the actual containers. Init containers always run to completion and each one must succeed before the next is started.

```yaml
---
apiVersion: v1
kind: Pod
metadata:
  name: myapp-pod
  labels:
    app: myapp
spec:
  containers:
  - name: myapp-container
    image: busybox
    command: ['sh', '-c', 'echo The app is running! && sleep 3600']
  initContainers:
  - name: init-myservice
    image: busybox
    command: ['sh', '-c', 'until nslookup myservice; do echo waiting for myservice; sleep 2; done;']
  - name: init-mydb
    image: busybox
    command: ['sh', '-c', 'until nslookup mydb; do echo waiting for mydb; sleep 2; done;']
---
kind: Service
apiVersion: v1
metadata:
  name: myservice
spec:
  ports:
  - protocol: TCP
    port: 80
    targetPort: 9376
---
kind: Service
apiVersion: v1
metadata:
  name: mydb
spec:
  ports:
  - protocol: TCP
    port: 80
    targetPort: 9377
```

```shell
# Create pod
kubectl create -f init-containers.yml

# Get overall info
kubectl get pod myapp-pod

# Get details
kubectl describe pod myapp-pod

# Create required services
kubectl create -f services.yml

# Get overall info
kubectl get pod myapp-pod

# Get details
kubectl describe pod myapp-pod
```
