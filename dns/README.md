# Kubernetes DNS

### Creating MySQL - Wordpress deployment with service discovery

* kubectl

```shell
bash kubectl/main.sh
```

* python

```shell
python python/main.py --type code
# or
python python/main.py --type yaml
```

* go

```shell
cd go
go build -o ./main.out
./main.out -kubeconfig=$HOME/.kube/config
```
