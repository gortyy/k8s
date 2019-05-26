# Horizontal Pod Autoscaler
-------------------------
HPA automatically scales number of pods controlled by replication controllers based on CPU usage (or custom metrics). HPA works only on k8s objects that may be scaled (e.g. it won't work on DaemonSet).

## Implementation
--------------
HPA is both k8s API resource and controller. API resource defines the controller's behaviour. Controller periodically adjust number of replicas inside deployment/replication controller so that mean CPU utilisation is roughly equal to target usage - defined by user

HPA is implemented as control loop whose period is equal to 15 secods - it may be set to different value via controller with `--horizontal-pod-autoscaler-sync-period`.

During each iteration, controller manager is checking resources usage (based on metrics defined in HPA manifest).

HPA is fetching metrics from group of APIs which includes:
* `metrics.k8s.io` (it is served by metrics-server - turned-off by default)
* `custom.metrics.k8s.io`
* `external.metrics.k8s.io`

## Scaling Algorithm
-----------------
HPA work is based on scaling factor which is ratio between target utilisation values and their real values

```
desiredReplicas = ceil[currentReplicas * ( currentMetricValue / desiredMetricValue )]
```

### Discarded Pods
Any pod that is being deleted (in shut-down state) and any failed pods aren't considered during scaling factor calculation.

If some pod's metric doesn't have value it's not taken into consideration at this point, they will be used for final adjustments.

If pod is being initialized it's also not considered in calculations.

### Final Adjustment
If some metric is missing then the mean is calculated in following manner:
* we assume that discarded pods are using 100% of given resource in case of down-scale
* we assume that discarded pods are using 0% of given resource in case of up-scale

This way we can dampen the resulting scaling factor.

### Scaling Decision
If after final adjustment scaling factor's direction is changing or scaling factor is within toleration HPA will not proceed with scaling.

### Multiple metrics
When users defines a set of metrics for HPA then it calculates scaling factors for each of them and chooses highest one - scaling will be done according to that factor.

### Errors
If it happens that some erros occur (unable to fetch metrics) scaling won't work.


## API Resource
----------------
HPA is k8s API resource and it belongs to `autoscaling` group. Current stable version supports autoscaling based on CPU usage - `autoscaling/v1`. Beta version that support scaling based on memory and custom metrics is available at `autoscaling/v2beta2`.

## Kubectl
----------
Other than API Resource we can interact with HPA via `kubectl`. To autoscale ReplicaSet `foo` with min number of pods equal 2 and maximum 5 and 0.8 CPU usage user should invoke:

```
kubectl autoscale rs foo --min=2 --max=5 --cpu-percent=80
```



**Exercise**
------------
* Start minikube and enable `metrics-server` addon
* Run single pod based on `nginxdemos/hello` image, it should have exposed port 80 and request 0.1 CPU core and 256Mi of RAM
* Expose this pod (deployment) with load balancer so that application can be reach from outside (`minikube service <name> --url` might be useful) (check [services](../services/README.md))
* Autoscale this pod (deployment) - set min number of pods to 1 and max to 6 and CPU to 0.05
* Turn on pod-watch and generate some traffic (ab is nice tool here - `ab -c 100 -n 1000 $SERVICE_URL)
* Get some details about HPA events
