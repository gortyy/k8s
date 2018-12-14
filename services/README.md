# Services

Kubernetes pods are ephemeral, if they go down they are substituted by new ones. Each pod gets it's own IP address, but as pods are ephemeral we cannot rely upon it. If some pods provide services to other pods inside the cluster they're using Kubernetes Services.
Kubernetes Service is an abstraction which defines a logical set of pods and policy for accessing them. Pods that are targeted by Service are usually determined by label selector.

## Defining Service

Service is also a Kubernetes Object and it can be defined in similar fashion to Deployment or Pod.

```yaml
kind: Service
apiVersion: v1
metadata:
  name: myservice
spec:
  selector:
    app: myapp
  ports:
  - protocol: TCP
    port: 80
    targetPort: 9376
```

Suppose we have set of pods that expose port `9376` and all have labels `app=myapp`. This spec will create Service named `myservice` which targets any TCP port `9376` on any pod with label `app=myapp`. This service will get assigned IP address aswell. Service can map `port` to any `targetPort` but by default it will map to port with the same value as `port`.
