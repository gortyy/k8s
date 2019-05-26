# Deployments

You describe a desired state in a Deployment object, and the Deployment controller changes the actual state to the desired state at a controlled rate.

### Deploying Tomcat application

Most simple deployment is running a single pod. Pod is basically an instance of container. Deployment may consist of multiple pods of different types (each of them may have unique job to do).

### Deployment steps
To deploy Tomcat application to Kubernetes cluster we need to create deployment:

```yaml
apiVersion: apps/v1beta2
kind: Deployment
metadata:
  name: tomcat-deployment
spec:
  selector:
    matchLabels:
      app: tomcat
  replicas: 2
  template:
    metadata:
      labels:
        app: tomcat
    spec:
      containers:
      - name: tomcat
        image: tomcat:8
        ports:
        - containerPort: 8080
```

```shell
kubectl create -f ./deployment.yml
```

*  A deployment named `tomcat-deployment` is created - indicated by `metadata.name` field.
*  Deployment creates two repliced pods - idicated by `spec.replicas`.
*  The selector field defines how the deployment finds which pod to manage. In this case it's matching label used in pod template `app=tomcat`.
*  The `template` field contains:
    * pod label `app: tomcat`
    * `template.spec` tells to run single container

```shell
kubectl get deployments tomcat-deployment
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

### Updating Tomcat deployment

Changing Docker image:
```shell
DEPLOYMENT="deployment.v1beta2.apps/tomcat-deployment"
kubectl set image "${DEPLOYMENT}" tomcat=tomcat:8.5

# OR

kubectl edit "${DEPLOYMENT}"

# Check rollout results
kubectl rollout status "${DEPLOYMENT}"
```

### Scaling Tomcat deployment

You can scale a deployment using following command:
```shell
kubectl scale "${DEPLOYMENT}" --replicas=3
```

### Pausing Tomcat deployment

You can pause a Deployment before triggering one or more updates and then resume it. This will allow you to apply multiple fixes in between pausing and resuming without triggering unnecessary rollouts.

```shell
kubectl rollout pause "${DEPLOYMENT}"
#
# Do some updates as above (edit or set)
#

# Check if rollout started
kubectl rollout history "${DEPLOYMENT}"

# Resume deployment
kubectl rollout resume "${DEPLOYMENT}"
