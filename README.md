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

## Background

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


## Overview

To work with Kubernetes cluster you communicate with Kubernetes API objects (pods, deployments, services, etc.), by defining the desired state of your application. You would typically do it with `kubectl`, however you can use client libraries for language of your choice https://kubernetes.io/docs/reference/using-api/client-libraries/.
Once you've entered desired state of your app, Kubernetes Control Plane makes sure the app is running as defined (it includes automatic tasks such as pulling/starting/stoping containers, scaling number of replicas, etc.). Kubernetes Control Plane consists of multiple processes running on Kubernetes cluster:
*  Kubernetes Master - collection on processes running on single (or multiple) node in cluster. These processes include `kube-apiserver`, `kube-controller-manager` and `kube-scheduler`
*  Each other node runs two processes:
    *  kubelet - "node agent", it works in terms of PodSpecs (YAML or JSON object that describes pod). It takes PodSpecs provided via various mechanisms (monitoring files, HTTP endpoints, HTTP servers) and makes sure that described pods are healthy and running. Kubelet manages containers created only by Kubernetes.
    *  kube-proxy - network proxy which reflects Kubernetes networking services on node


### Kubernetes Objects

Kubernetes abstracts state of the system with use of objects in Kubernetes API. Basic Kubernetes Objects are:
*  Pod
*  Service
*  Volume
*  Namespace

In addition to basic objects, Kubernetes has couple of higher-level abstraction objects called Controllers - they build upon the basic objects:
*  ReplicaSet
*  Deployment
*  StatefulSet
*  DaemonSet
*  Job

## Kubernetes Components

### Master Components

Master Components provide cluster's control plane. These components make global decisions on cluster, detect and respond to events (e.g. starting new pods when `replicas` field in unsatisfied). Master components can be run on any machine on the cluster, however for simplicity, most installs are done on single node (master). Master node is not running any application's containers (only control plane's). Master components include:
*  kube-apiserver - exposes Kubernetes API, front-end for the control-plane, designed to scale horizontally.
*  etcd - key value backing store for cluster's data.
*  kube-scheduler - watches for pods that don't have assigned node, and assigns them one.
*  kube-controller-manager - runs controllers:
    *  Node Controller - watches pods and notifies if any goes down
    *  Replication Controller - makes sure that `replicas` is satisfied
    *  Endpoint Controller - joins Services and Pods
    *  Service Account & Token Controllers - create default accounts and API tokens for new namespaces

### Node Components

Node Components run on every node, they provide Kubernetes runtime environment and maintain running pods.

*  kubelet - "node agent", it works in terms of PodSpecs (YAML or JSON object that describes pod). It takes PodSpecs provided via various mechanisms (monitoring files, HTTP endpoints, HTTP servers) and makes sure that described pods are healthy and running. Kubelet manages containers created only by Kubernetes.
*  kube-proxy - network proxy which reflects Kubernetes networking services on node
*  Container Runtime - Kubernetes supports

### Kubernetes API

Kubernetes supports multiple API versions, each at a different API path, such as `api/v1` or `apis/extensions/v1beta1`.

#### Versioning
*  Alpha level - contains `alpha` in path, may be buggy, disabled by default, may drop support for features without notice
*  Beta level - contains `beta` in path, well tested, enabled by default, support for features won't drop, however details may change
*  Stable level - version name is `vX` where `type(X) is int`

#### Groups
The API group is specified in a REST path and in the `apiVersion` field of a serialized object. Currently there are several API groups in use:
*  `core` group is at REST path `/api/v1` and uses `apiVersion: v1`
*  named groups at REST paths `apis/<group_name>/<version>` and use `apiVersion: <group_name>/<version>` - `apiVersion: batch/v1`

https://kubernetes.io/docs/reference/

API gropus can be enabled in apiserver with `--runtime-config` flag, e.g. `--runtime-config=batch/v1=false` to disable `batch/v1`, `--runtime-config=batch/v2alpha1` to use `batch/v2alpha1`. Resources within groups can be enabled/disabled as well, e.g. `--runtime-config=extensions/v1beta1/deployments=false,extensions/v1beta1/jobs=false`

## Kubernetes Objects In Depth

Kubernetes objects are persistent entities (once you create it, Kubernetes will work to ensure such object exists), that Kubernetes uses to describe cluster:
*  what apps are running
*  resources available for apps
*  policies that govern apps (restart policies, upgrades etc)

By creating Kubernetes object you're dictating your cluster's desired state.

### Object's Spec and Status

Every object includes two fields, spec and status. Spec is provided by user and describes desired state of the object. Status describes actual status of the object, it is supplied and updated by Kubernetes.

### Describing Object

When you create an object, you must provide it's spec. API request must include that spec as JSON in request body (if you use `kubectl` then stick to YAML).

```yaml
application/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
spec:
  selector:
    matchLabels:
      app: nginx
  replicas: 2
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx
        ports:
        - containerPort: 80
```

You can create this deployment with `kubectl create -f <filename>`

### Required fields

*  `apiVersion` - which Kubernetes API Version to use
*  `kind` - what kind of object will be created
*  `metadata` - includes name and namespace (optional, `default` by default), helps to uniquely identify the object
*  `spec` - different for each Kubernetes object and contains nested fields specific to that object.

### Names

All Kubernetes objects are uniquely identified by name and UID.

* name - client-provided string that refers to an object
* UID - Kubernetes system-generated string to uniquely identify object

### Namespaces

Namespaces are virtual clusters, they enable support for multiple virtual clusters backed by one physical cluster. Namespaces are intended for use in environments with many users. Namespaces provide scope for names, names of resources need to be unique within namespace but not across namespaces.

```shell
kubectl get namespaces
```

Kubernetes starts with three namespaces:
*  default - default namespace for objects without assigned namespace
*  kube-system - namespace for objects created by Kubernetes system
*  kube-public - automatically created, all users can read them (even not authenticated)

```shell
kubectl --namespace=$NAMESPACE run nginx:latest
kubectl --namespace=$NAMESPACE get pods
```

### Labels and Selectors

Labels are key/value pairs that are assigned to objects, they can be used to organize and to select subsets of objects. Labels can be attached at object's creation time and added or modified at any time. Each label key must be unique for given object.

```shell
kubectl label --help
```

#### Syntax

Valid label keys have two segments: optional prefix and a required name (alphanumeric) separated by /. If we specify prefix then it should be in form of DNS subdomain. If prefix is omitted then it's assumed as private to the user. `kubernetes.io/` prefix is reserved for Kubernetes core components. Valid label must be shorter than 64 alphanumeric chars or empty.

#### Selectors

Unlike names, labels are not unique within cluster (there might be many objects with the same set of labels). With use of selector user can spot a set of objects. Kubernetes API supports two types of selectors:
*  equality - `app = nginx, tier != frontend` (`= == !=`)
*  set - `app in (nginx, tomcat), tier in (backend)`             (`in notin <key_identifier>`)
In case of multiple requirements every one must be satisfied. Empty selector will match every object. Example pod spec below selects only nodes with the label `tier = backend`.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx
spec:
  containers:
    - name: nginx-app
      image: nginx:latest
  nodeSelector:
    tier: backend
```

```shell
# Get pods with specific labels (equality)
kubectl get pods -l app=nginx,tier=backend
kubectl get pods -l 'app in (nginx), tier in (backend)'
```

### Field Selectors

Field selectors let select Kubernetes objects based on value of resource fields.

```shell
kubectl get pods --field-selector status.phase=Running
kubectl get pods --field-selector metadata.name=nginx

kubectl get pods --field-selector ""
```

All objects support filtering on `metadata.name` and `metadata.namespace` fields.

```shell
# Chaining selectors
kubectl get pods --field-selector status.phase=Running,metadata.name=nginx

# Filtering multiple kinds of objects

kubectl get pods,deployments --field-selector metadata.namespace=production
```
