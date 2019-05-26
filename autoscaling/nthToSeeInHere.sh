minikube start

minikube addons enable metrics-server

kubectl run hello --image=nginxdemos/hello --port=80 --requests="cpu=100m,memory=256Mi"

kubectl get pods

kubectl expose deployment hello --name=hello-svc --port=80 --target-port=80 --type=LoadBalancer

kubectl get service hello-svc

minikube service hello-svc --url

kubectl autoscale deployment hello --min=1 --max=6 --cpu-percent=5

kubectl get hpa hello

ab -c 100 -n 1000 $(minikube service hello-svc --url)/

kubectl describe hpa hello
