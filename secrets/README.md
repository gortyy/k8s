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

When you mount ConfigMap volume to directory, then the mounted directory will contain only files from the mounted filesystem - original files in that dir won't be accessible as long as the volume is mounted.
If you want to have an access to already existing files, mount each ConfigMap entry as a file.

```yaml
spec:
  containers:
  - image: some/image
    volumeMounts:
    - name: myvolume
      mountPath: /etc/someconfig.conf
      subPath: myconfig.conf
```

By default, the permissions on all files in a configMap volume are set to 644. You can change this by setting the `defaultMode` property in the volume spec.

```yaml
volumes:
- name: config
configMap:
name: fortune-config
defaultMode: "6600"
```

When you update a ConfigMap, the files in all the volumes referencing it are updated. It’s then up to the process to detect that they’ve been changed and reload them. All the files are updated atomically, which means all updates occur at once. Kubernetes achieves this by using symbolic links.

```shell
kubectl exec fortune-https -c web-server ls -- -l /etc/nginx/conf.d
kubectl exec fortune-https -c web-server ls -- -l /etc/nginx/conf.d/..data
```

If you’ve mounted a single file in the container instead of the whole volume, the file will not be updated.

### Example

```shell
kubectl create configmap fortune-config --from-file=configmap-files
kubectl get configmap fortune-config -o yaml
kubectl port-forward fortune 8080:80 &
curl -H "Accept-Encoding: gzip" -I localhost:8080
kubectl exec fortune -c web-server ls /etc/nginx/conf.d

kubectl edit configmap fortune-config
kubectl exec fortune -c web-server
kubectl exec fortune -c web-server -- nginx -s reload

kubectl exec -it fortune -c web-server -- ls -lA /etc/nginx/conf.d
```


## Secrets

All the information passed to containers so far is regular, non-sensitive configuration data that doesn’t need to be kept secure.

To store and distribute secret information, Kubernetes provides a separate object called a Secret. Secrets are much like ConfigMaps — they’re also maps that hold key-value pairs. They can be used the same way as a ConfigMap. You can
* Pass Secret entries to the container as environment variables
* Expose Secret entries as files in a volume

Kubernetes keeps Secrets safe by making sure each Secret is only distributed to the nodes that run the pods that need access to the Secret. Also, on the nodes themselves, Secrets are always stored in memory and never written to physical storage, which would require wiping the disks after deleting the Secrets from them.

```shell
kubectl get secrets
kubectl describe secrets
```

By default, the default-token Secret is mounted into every container, but you can disable that in each pod by setting the automountServiceAccountToken field in the pod spec to false or by setting it to false on the service account the pod is using.

```shell
kubectl exec mypod ls /var/run/secrets/kubernetes.io/serviceaccount/
```

### Creating Secret

Edit `fortune-config` and enter ssl config.

```conf
ssl_certificate certs/https.cert;
ssl_certificate_key certs/https.key;
ssl_protocols TLSv1 TLSv1.1 TLSv1.2;
ssl_ciphers HIGH:!aNULL:!MD5;
```

```shell
openssl genrsa -out https.key 2048
openssl req -new -x509 -key https.key -out https.cert -days 3650 -subj /CN=www.testexample.com

echo bar > foo

kubectl create secret generic fortune-https --from-file=https.key --from-file=https.cert --from-file=foo
kubectl get secret fortune-https -o yaml

kubectl port-forward fortune-https 8443:443 &
curl https://localhost:8443 -k
curl https://localhost:8443 -k -v
kubectl exec fortune-https -c web-server -- mount | grep certs
```

When you expose the Secret to a container through a secret volume, the value of the Secret entry is decoded and written to the file in its actual form (regardless if it’s plain text or binary). The same is also true when exposing the Secret entry through an environment variable. In both cases, the app doesn’t need to decode it, but can read the file’s contents or look up the environment variable value and use it directly.

Like configMap volumes, secret volumes also support specifying file permissions for the files exposed in the volume through the defaultMode property.

### Pull Secrets

Up to now all container images have been stored on public image registries, which don’t require any special credentials to pull images from them.

To run a pod, which uses an image from the private repository, you need to
* Create a Secret holding the credentials for the Docker registry.
* Reference that Secret in the imagePullSecrets field of the pod manifest.

```shell
kubectl create secret docker-registry mydockerhubsecret \
    --docker-username=myusername \
    --docker-password=mypassword \
    --docker-email=my.email@provider.com
```

To have Kubernetes use the Secret when pulling images from your private Docker Hub repository, all you need to do is specify the Secret’s name in the pod spec.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: private-pod
spec:
  imagePullSecrets:
  - name: mydockerhubsecret
  containers:
  - image: username/private:tag
    name: main
```
