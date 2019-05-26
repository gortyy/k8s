# Updating applications declaratively with Deployment

## Updating apps running in pods

Let's say that our app is currently running on image tagged as `v1`. Then we develop upon our first image and push tag `v2` to our hub. The next thing we'd like to do is to update our pods with new version. However pods cannot be updated, to use newer version we need to delete all existing pods running `v1`, edit template and declare that we want to use `v2` and then create new pods.

Actually we have two ways of updating our application:
* delete existing pods and start new ones,
* start new ones, once they are up delete the old ones. You can do this by deleting all old pods or gradually deleting old ones and adding new.

Both approaches have some up- and downsides. First want could cause a temporary outage of service provided by your app. The second one requires that your app can run few versions at once, without any collision.

### Deleting pods and replacing them with new ones

ReplicationController/ReplicaSet allows you to replace existing pods with newer pods - RC template can be updated any time. When RC creates new pods it uses last version of its template.

### Spinning up new pods and then deleting the old ones

If you don't want to see any downtime, and your app supports running multiple versions at once, then you can first creates new pod and then delete old ones.
Pods are usually fronted by a Service. Once new pods are fully operational you can switch service's endpoint (it's label) and make it point to the new pods.


### Performing a rolling update

Instead of creating new pods and then deleting all the old ones, you can perform rolling update - replace old pods with new steps by step. It could be done by slowly scaling down old RC and scaling up new RC. In this case service would have to point to both new and old services.


## Automatic rolling update with RC

Instead of manually scaling up/down your RCs you can ask `kubectl` to do it for you.

```yaml
apiVersion: v1
kind: ReplicationController
metadata:
  name: http-v1
spec:
  replicas: 4
  template:
    metadata:
      name: http
      labels:
        app: http
    spec:
      containers:
      - image: dsmiech/python_http:v1
        name: python-http
---
apiVersion: v1
kind: Service
metadata:
  name: http
spec:
  type: NodePort
  selector:
    app: http
  ports:
  - port: 8080
    targetPort: 8080
```

```shell
kubectl create -f python-http-rc.yml

url=$(minikube service http --url)

while :; do
    curl $url
    sleep 1
done

kubectl rolling-update http-v1 http-v2 --image=dsmiech/python_http:v2 --v 6

kubectl describe rc http-v2
```

`kubectl` created new RC by copying manifest of `http-v1` RC and changing its image to the one specified in command. Rolling-update process updates labels of both RCs.
`rolling-update` command is nice example of automatic version update, but this method is now deprecated. Here are the reasons why:
* it is modifying existing objects (pods labels and label selectors of RCs)
* kubectl (API client) is the one that's doing all the requests (master should handle this)

In our case the update went smoothly, but what happens if our client looses connection to api server?

## Using deployments to update apps declaratively

A deployment is higher level resource meant for deploying applications and updating them declaratively, instead of doing it through a RC, which are both considered lower-level abstractions.

When you're using deployment to create pods, they are created by deployment's RC, not by deployment directly.

Using deployment instead of lower-level constructs makes updating an app much easier - you just declare desired state through single k8s resource and letting k8s do the rest of job.

## Creating deployment

```yaml
apiVersion: apps/v1beta1
kind: Deployment
metadata:
  name: http
spec:
  replicas: 4
  template:
    metadata:
      name: http
      labels:
        app: http
    spec:
      containers:
        - image: dsmiech/python_http:v1
          name: python-http
```

```shell
kubectl delete rc --all

kubectl create -f python-http-deployment-v1.yml --record
minikube service http --url

kubectl rollout status deployment http
```

## Updating deployment

```shell
kubectl edit deployment http
# or
kubectl set image deployment http python-http=dsmiech/python_http:v2
```

How this new state should be achieved is governed by the deployment strategy configured on deployment itself. The default strategy is `RollingUpdate`, and the alternative is `Recreate`.

Similar to RCs, all your new pods are now managed by the new RS. Unlike before, the old ReplicaSet is still there, whereas the old Replication-Controller was deleted at the end of the rolling-update process.

## Rolling back a deployment

```shell
kubectl edit deployment http
# or
kubectl set image deployment http python-http=dsmiech/python_http:v3

kubectl rollout status deployment http

kubectl rollout undo deployment http
kubectl rollout history deployment http
kubectl rollout undo deployment http --to-revision=1
```

## Pausing the rollout process

After rolling out bugged version of the app, you might not want to rollout another version across all pods the way it was done previously. We'll run new v4 next to the existing v2 pods and see how it behaves with only fraction of your users.

```shell
kubectl set image deployment http python-http=dsmiech/python_http:v4
kubectl rollout pause deployment http
# after some period
kubectl rollout resume deployment http
```

## Blocking rollouts of bad versions

`minReadySeconds` property in deployment's spec is used to prevent deploying malfunctioning versions of apps.

```yaml
apiVersion: apps/v1beta1
kind: Deployment
metadata:
  name: http
spec:
  replicas: 4
  minReadySeconds: 10
  strategy:
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
    type: RollingUpdate
  template:
    metadata:
      name: http
      labels:
        app: http
    spec:
      containers:
        - image: dsmiech/python_http:v3
          name: python-http
          readinessProbe:
            periodSeconds: 1
            httpGet:
              path: /
              port: 8080
```

```shell
kubectl apply -f python-http-deployment-v2.yml

kubectl rollout status deployment http
kubectl get pods

kubectl describe deploy http
```

If you only define the readiness probe without setting minReadySeconds properly, new pods are considered available immediately when the first invocation of the readiness probe succeeds. If the readiness probe starts failing shortly after, the bad version is rolled out across all pods. Therefore, you should set minReadySeconds appropriately.
