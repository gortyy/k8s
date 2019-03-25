# Volumes

In certain situations you want your containers persist data throughout pod's lifecycle. You may not want to persist the
whole filesystem but preserve only directories that hold application's data.

Kubernetes solves this problem with use of storage volumes. They aren't top level resource like pods - volumes are
defined within pod - they share the same lifecycle as their parent pod. Because of following pod's lifecycle, volume's
contents will persist throught containers restarts. Also if the pod contains multiple containers, the volume can be used
by all of them at once.

## Introduction

Volumes are pod's components - therefore they're defined in pod's specification. They aren't Kubernetes standalone
object and they cannot be created/deleted on their own. Volume is available to every container within pod, but it must
be mounted before actaul usage.

## Available volume types

Kubernetes offers a wide variety of volumes, some of them are generic and some are strictly related to the underlying
technologies.

* *emptyDir* - simple empty directory used for storing ephemeral data
* *hostPath* - used for mounting directories from the worker node's filesystem into pod
* *gitRepo*
* *nfs*
* *awsElasticBlockStore* and other cloud provider-specific storages
* *configMap*, *secret* - special types of volumes used to expose certain Kubernetes resources and cluster information
to the pod, they're not used for storing data, but for exposing Kubernetes metadata to apps running in the pod
* *presistentVolumeClaim* - a way to use already provisioned persistent storage


## Sharing data between containers

### emptyDir

An *emptyDir* volume is especially useful for sharing files between containers running in the same pod.

```yaml
apiVersion: v1
kind: Pod
metadata:
    name: fortune
spec:
    containers:
    - image: dsmiech/fortune
      name: html-generator
      volumeMounts:
      - name: html
        mountPath: /var/htdocs
    - image: nginx:alpine
      name: web-server
      volumeMounts:
      - name: html
        mountPath: /usr/share/nginx/html
        readOnly: true
      ports:
      - containerPort: 80
    volumes:
    - name: html
      emptyDir: {}
```

```shell
$ kubectl create -f fortune-pod.yml
$ kubectl get po fortune

$ kubectl exec -c html-generator fortune curl -- -s http://localhost
```

The *emptyDir* that we used in our pod was created on the actual hard-drive of the worker node hosting this pod, so its performance
depends on type of nodes disk. However you can tell Kubernetes to create *emptyDir* on a *tmps* filesystem.

```yaml
volumes:
- name: html
  emptyDir:
    medium: Memory
```

Other volumes build upon *emptyDir*, they create it and then populate it with data.

### gitRepo

*gitRepo* is basically an emptyDir volume that is populated with git repository. Its done when pod is starting up, but before its containares are created. Important thing to note is that after creation, *gitRepo* isn't doing anything to keep up with changes on the remote.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: gitrepo-pod
spec:
  containers:
  - image: dsmiech/nginx
    name: web-server
    volumeMounts:
    - name: html
      mountPath: /usr/share/nginx/html
      readOnly: true
    ports:
    - containerPort: 80
      protocol: TCP
  volumes:
  - name: html
    gitRepo:
      repository: https://github.com/gortyy/k8s.git
      revision: master
      directory: .
```

## Accessing files on the worker node's filesystem

Most pods should be aware of the host node that they're running on, so they shouldn't access any files on that node. But certain system-level pods do need to either read the node's fiels or use the node's filesystem to access the node's devices through the filesystem. Kubernetes enables this with *hostPath*.

*hostPath* is the first of persistent storage, because both *gitRepo* and *emptyDir* contents are deleted when pod dies.

```shell
$ kubectl describe pod --namespace kube-system aws-node-12345
```

Remember to use *hostPath* volumes only if you need to read or write system files on the node. Never use them to persist data across pods.

## Using persistent storage

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: mongodb
spec:
  volumes:
  - name: mongodb-data
    awsElasticBlockStore:
      volumeID: vol-0c7f568c01d4f06c5
      fsType: ext4
  containers:
  - image: mongo
    name: mongodb
    volumeMounts:
    - name: mongodb-data
      mountPath: /data/db
    ports:
    - containerPort: 27017
      protocol: TCP
```

```shell
$ kubectl create -f mongodb-pod-ebs.yml
$ kubectl exec -it mongodb mong

> use mystore

> db.foo.insert({name:'foo'})
> db.foo.find()

$ kubectl delete pod mongodb
$ kubectl create -f mongodb-pod-ebs.yml

$ kubectl exec -it mongodb mong

> use mystore

> db.foo.find()
```


## Decoupling pods from the underlying storage technology

Ideally, a developer deploying apps on Kubernetes shouldn't worry about underlying storage technology, the same way he doesn't worry about physical servers backing cluster.

## PersistentVolumes and PersistentVolumeClaims

To enable apps to request storage in Kubernetes cluster without haveing to deal with infrastructure specifics, two new resources were introduced - *PersistentVolumes* and *PersistentVolumeClaims*.

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: mongodb-pv
spec:
  capacity:
    storage: 1Gi
  accessModes:
  - ReadWriteOnce
  - ReadOnlyMany
  persistentVolumeReclaimPolicy: Retain
  awsElasticBlockStore:
    volumeID: vol-0c7f568c01d4f06c5
    fsType: ext4
```

*PersistentVolumes* don't belong to any namespace. They're cluster-level resources like nodes.

### Claiming PersistentVolume

Claiming a PersistentVolume is a completely separate process from creating a pod, beacuase you want the same *PersistentVolumeClaim* to stay available even if the pod is rescheduled.

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: mongodb-pvc
spec:
  resources:
    requests:
      storage: 1Gi
  accessModes:
  - ReadWriteOnce
  storageClassName: ""
```

*PersistentVolumeClaim* can be created only in a specific namespace.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: mongodb
spec:
  containers:
  - image: mongo
    name: mongodb
    volumeMounts:
    - name: mongodb-data
      mountPath: /data/db
    ports:
    - containerPort: 27017
      protocol: TCP
  volumes:
  - name: mongodb-data
    persistentVolumeClaim:
      claimName: mongodb-pvc
```

Using this indirect method of obtaining storage from the instrastructure is much simple for the application developer.


### Recycling PersistentVolumes

```shell
$ kubectl delete pod mongodb
$ kubectl delete pvc mongodb-pvc

# What will happen if we create PVC once again? Will it be bound to PersistentVolume?

$ kubectl create -f mongodb-pvc.yml
$ kubectl get pvc

$ kubectl get pv
```

Because you used PersistentVolume before and it may contain some data and it shouldnt be bound to a completely new claim without cleaning it first. This behavior was set by flag `persistentVolumeReclaimPolicy: Retain`.

Two other possible reclaim policies exist:
* `Recycle` - clear contents of volume
* `Delete` - delete underlying storage
