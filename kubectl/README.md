## Kubectl

Kubectl is the main gateway of contact with local or remote k8s clusters. That's the main tool used when working with k8s.

### Basic commands

```shell
# list all pods in default namespace
kubectl get pods

# describe given pod
kubectl describe pod <pod-name>

# expose port of service running in k8s cluster
kubectl expose deployment tomcat-deployment --type=NodePort

# show output of service running in k8s pod
kubectl attach <pod-name> -c <container-name>

# run interactive shell inside k8s pod
kubectl exec --it <pod-name> bash

# assign label to k8s object
kubectl label pod <pod-name> key=value

# run single pod
kubectl run <pod-name> --image=<image-name>
```
