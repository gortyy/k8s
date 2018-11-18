package main

import (
	"flag"
	"fmt"
	"path/filepath"

	appsv1 "k8s.io/api/apps/v1"
	apiv1 "k8s.io/api/core/v1"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/client-go/kubernetes"
	"k8s.io/client-go/tools/clientcmd"
	"k8s.io/client-go/util/homedir"
)

type KubernetesObject interface {
	GetName() string
	Create()
}

type Service struct {
	KubernetesObject
	Name   string
	Labels map[string]string
	Port   int32
	Type   apiv1.ServiceType
}

func (s Service) GetName() string {
	return s.Name
}

func (s Service) Create() {
	servicesClient := clientset.CoreV1().Services(apiv1.NamespaceDefault)

	manifest := &apiv1.Service{
		ObjectMeta: metav1.ObjectMeta{
			Name:   s.Name,
			Labels: s.Labels,
		},
		Spec: apiv1.ServiceSpec{
			Ports: []apiv1.ServicePort{
				{
					Port: s.Port,
				},
			},
			Selector: s.Labels,
			Type:     s.Type,
		},
	}

	_, err := servicesClient.Create(manifest)
	if err != nil {
		panic(err)
	}
	fmt.Printf("Created service %q.\n", s.GetName())
}

type Deployment struct {
	KubernetesObject
	Name     string
	Labels   map[string]string
	Strategy appsv1.DeploymentStrategy
	Image    string
	Env      []apiv1.EnvVar
	Ports    []apiv1.ContainerPort
}

func (d Deployment) GetName() string {
	return d.Name
}

func (d Deployment) Create() {
	deploymentsClient := clientset.AppsV1().Deployments(apiv1.NamespaceDefault)

	manifest := &appsv1.Deployment{
		ObjectMeta: metav1.ObjectMeta{
			Name:   d.Name,
			Labels: d.Labels,
		},
		Spec: appsv1.DeploymentSpec{
			Selector: &metav1.LabelSelector{
				MatchLabels: d.Labels,
			},
			Strategy: d.Strategy,
			Template: apiv1.PodTemplateSpec{
				ObjectMeta: metav1.ObjectMeta{
					Labels: d.Labels,
				},
				Spec: apiv1.PodSpec{
					Containers: []apiv1.Container{
						{
							Image: d.Image,
							Name:  d.Name,
							Env:   d.Env,
							Ports: d.Ports,
						},
					},
				},
			},
		},
	}

	_, err := deploymentsClient.Create(manifest)
	if err != nil {
		panic(err)
	}
	fmt.Printf("Created deployment %q.\n", d.GetName())
}

var (
	clientset = loadKubeConfig()
)

func loadKubeConfig() *kubernetes.Clientset {
	var kubeconfig *string
	if home := homedir.HomeDir(); home != "" {
		kubeconfig = flag.String("kubeconfig", filepath.Join(home, ".kube", "config"), "(optional) absolute path to kubeconfig file")
	} else {
		kubeconfig = flag.String("kubeconfig", "", "absolute path to kubeconfig file")
	}
	flag.Parse()

	config, err := clientcmd.BuildConfigFromFlags("", *kubeconfig)
	if err != nil {
		panic(err)
	}

	clientset, err := kubernetes.NewForConfig(config)
	if err != nil {
		panic(err)
	}

	return clientset
}

func main() {
	mysqlService := Service{
		Name: "wordpress-mysql",
		Labels: map[string]string{
			"app":  "wordpress",
			"tier": "mysql",
		},
		Port: 3306,
		Type: "ClusterIP",
	}

	wordpressService := Service{
		Name: "wordpress",
		Labels: map[string]string{
			"app":  "wordpress",
			"tier": "frontend",
		},
		Port: 80,
		Type: "LoadBalancer",
	}

	mysqlService.Create()
	wordpressService.Create()

	mysqlDeployment := Deployment{
		Name: "wordpress-mysql",
		Labels: map[string]string{
			"app":  "wordpress",
			"tier": "mysql",
		},
		Strategy: appsv1.DeploymentStrategy{
			Type: "Recreate",
		},
		Image: "mysql:5.6",
		Env: []apiv1.EnvVar{
			{
				Name:  "MYSQL_ROOT_PASSWORD",
				Value: "drowssap",
			},
		},
		Ports: []apiv1.ContainerPort{
			{
				Name:          "mysql",
				ContainerPort: 3306,
			},
		},
	}

	wordpressDeployment := Deployment{
		Name: "wordpress",
		Labels: map[string]string{
			"app":  "wordpress",
			"tier": "frontend",
		},
		Strategy: appsv1.DeploymentStrategy{
			Type: "Recreate",
		},
		Image: "wordpress:4.8-apache",
		Env: []apiv1.EnvVar{
			{
				Name:  "WORDPRESS_DB_HOST",
				Value: "wordpress-mysql",
			},
			{
				Name:  "WORDPRESS_DB_PASSWORD",
				Value: "drowssap",
			},
		},
		Ports: []apiv1.ContainerPort{
			{
				Name:          "wordpress",
				ContainerPort: 80,
			},
		},
	}

	mysqlDeployment.Create()
	wordpressDeployment.Create()
}
