# Kubernetes Architecture

In Kubernetes, the master (or masters for high availability) control any number of nodes. Master is running API Server, Scheduler and Controller Manager. Nodes are individual machines (physical or virtual) that're running pods and services that are necessary to run them, such as Docker, kubelet and kube-proxy.

*  kubelet is watches and manages services running on individual node (supervisor for that machine), it makes sure that the job assigned by the master is done
*  kube-proxy makes sure that network services exposed by each pod can be accessed as defined in the deployment
