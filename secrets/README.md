# ConfigMaps and Secrets


## Configuring containerized applications

* EnvVars

    Popular way of passing configuration options to containers is through environment variables (official MySQL containeris looking for `MYSQL_ROOT_PASSWORD` var).
* Config files

    Using configuration files with containers is a bit trickier, as you would need to put these configs into image or attach a volume. In kubernetes world, it could be handled with `gitRepo` volume.
* ConfigMaps

    Putting configuration data into Kubernetes top-level resource and store it together with other resource manifests in git repo.

## Command-line arguments

### Entrypoint vs Cmd

* ENTRYPOINT - defines executable that gets invoked when container is started
* CMD        - specifies arguments that get passed to ENTYPOINT

```shell
# Execute plain ENTRYPOINT
docker run $IMAGE

# Execute ENTRYPOINT with some arguments
docker run $IMAGE $ARGS
```

### Overriding command and arguments in Kubernetes

```yaml
kind: Pod
spec:
  containers:
  - image: some/thing
    command: [cmd]          # You dont have to enclose strings with qoutes
    args: ["1", "2", "3"]   # But you have to do it with numbers
```

The `command` and `args` fields can't be updated after the pod is created.

So in Kubernetes world:
```
ENTRYPOINT == command   => true
CMD        == args      => true
```

### Specifying env vars in container definition

```yaml
kind: Pod
spec:
  contaienrs:
  - image: some/thing
    env:
    - name: arg1
      value: "1"
```

Remember that in each container Kubernetes automatically puts environment variables for each service in the same namespace.

### Referring to other env vars

```yaml
env:
- name: FIRST
  value: "asd"
- name: SECOND
  value: "$(FIRST)_dsa"
```

## ConfigMaps

Kubernetes allows separating configuration into a separate object - ConfigMap. ConfigMaps are key/value maps with values ranging from short literals to full config files.

An application doesn't need to read the ConfigMap directly or even know that it exists. The contents of the map are instead passed to containers as either environment variables or as files in a volume. And because environment variables can be referenced in command-line arguments, you can pass ConfigMaps entries as command-line arguments.

Having a separate standalone object like this, allows you to keep multiple manifests for ConfigMaps with the same name, each for a different environment (dev, test, stg, prod...).

Because pods reference the ConfigMap by name, you can use a different config in each environment while using the same pod specification across all of them.

### Creating ConfigMap

```shell
kubectl create configmap fortune-config --from-literal=sleep-interval=25
kubectl get configmap fortune-confg -o yaml

kubectl create configmap asd --from-file=config.conf
kubectl create configmap dsa --from-file=/path/to/configs
```

ConfigMap keys must be a valid DNS subdomain.

```yaml
env:
- name: INTERVAL
  valueFrom:
    configMapRefKey:
      name: fortune-config
      key: sleep-interval
```

When you try to reference non-existing configMap in a pod, Kubernetes schedules pod normally and tries to run it containers.

Containers referencing non-existing configMap will fail to start, but others will start normally.

When you create missing configMap those containers come up without the need to recreate entire pod.


When your ConfigMap contains more than just a few entries, its not handy to create env var for each of them.

```yaml
envFrom:
- prefix: CONFIG_ # optional
  configMapRef:
    name: asd
```

### Using ConfigMap volume

ConfigMap volume exposes each entry of the ConfigMap as file.