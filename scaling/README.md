# Scaling applications


## Stateful

Stateful applications store client data generated in one session for use in the next one locally. Client session is locked to thread or process running on machine. If that process dies, client's data is lost.

## Stateless

Stateless applications update centralized datastore with the result of single operation so that next session can be handled by any thread or instance of the application.

Kubernetes supports both types of applications, but the good practice is to use stateless whenever its possible.

Kubernetes gives you many options to define how a pod should scale. By far the most used is setting `replicas` option in your deployment definition. Other types of scaling include:
*  defining ReplicaSet
*  bare pods
*  job
*  DaemonSet
