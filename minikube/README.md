## Deploying Tomcat application

Most simple deployment is running a single pod. Pod is basically an instance of container. Deployment may consist of multiple pods of different types (each of them may have unique job to do).

### Deployment steps
To deploy Tomcat application to k8s cluster we need create deployment:

```shell
kubectl create -f ./deployment.yml
```

Then expose it to the world:

```shell
kubectl expose deployment tomcat-deployment --type=NodePort
```

To check which port our app is served on:

```shell
ADDRESS=$(minikube service tomcat-deployment --url)
curl ${ADDRESS}
```
