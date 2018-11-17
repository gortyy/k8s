import argparse
from kubernetes import client, config, utils


config.load_kube_config()


class Creator:
    def __init__(self):
        self.api_client = client.ApiClient()


class CreateFromYaml(Creator):
    def create_object(self, filename):
        return utils.create_from_yaml(self.api_client, filename)

    def create_mysql_service(self):
        response = self.create_object("mysql-service.yml")
        print(response)

    def create_mysql_deployment(self):
        response = self.create_object("mysql-deployment.yml")
        print(response)

    def create_wordpress_service(self):
        response = self.create_object("wordpress-service.yml")
        print(response)

    def create_wordpress_deployment(self):
        response = self.create_object("wordpress-deployment.yml")
        print(response)


class CreateFromCode:
    def __init__(self):
        self.mysql_deployment = self.MySQLDeployment()
        self.mysql_service = self.MySQLService()

        self.wordpress_deployment = self.WordpressDeployment()
        self.wordpress_service = self.WordpressService()

    class MySQLDeployment:
        def __init__(self):
            self.name = "wordpress-mysql"
            self.labels = {"app": "wordpress", "tier": "mysql"}
            self.image = "mysql:5.6"
            self.env = [client.V1EnvVar(name="MYSQL_ROOT_PASSWORD", value="drowssap")]
            self.container_port = 3306
            self.strategy_type = "Recreate"

    class MySQLService:
        def __init__(self):
            self.name = "wordpress-mysql"
            self.labels = {"app": "wordpress", "tier": "mysql"}
            self.type = "ClusterIP"
            self.cluster_ip = None
            self.ports = [client.V1ServicePort(port=3306)]

    class WordpressDeployment:
        def __init__(self):
            self.name = "wordpress"
            self.labels = {"app": "wordpress", "tier": "frontend"}
            self.image = "wordpress:4.8-apache"
            self.env = [
                client.V1EnvVar(name="WORDPRESS_DB_PASSWORD", value="drowssap"),
                client.V1EnvVar(name="WORDPRESS_DB_HOST", value="wordpress-mysql"),
            ]
            self.container_port = 80
            self.strategy_type = "Recreate"

    class WordpressService:
        def __init__(self):
            self.name = "wordpress"
            self.labels = {"app": self.name, "tier": "frontend"}
            self.type = "LoadBalancer"
            self.cluster_ip = None
            self.ports = [client.V1ServicePort(port=80)]

    def create_mysql_service(self):
        self.create_service(self.mysql_service)

    def create_mysql_deployment(self):
        self.create_deployment(self.mysql_deployment)

    def create_wordpress_service(self):
        self.create_service(self.wordpress_service)

    def create_wordpress_deployment(self):
        self.create_deployment(self.wordpress_deployment)

    def create_service(self, service_object):
        metadata = client.V1ObjectMeta(
            name=service_object.name, labels=service_object.labels
        )

        spec = client.V1ServiceSpec(
            ports=service_object.ports,
            selector=service_object.labels,
            cluster_ip=service_object.cluster_ip,
            type=service_object.type,
        )
        service = client.V1Service(
            api_version="v1", kind="Service", metadata=metadata, spec=spec
        )

        api_client = client.CoreV1Api()
        api_client.create_namespaced_service(body=service, namespace="default")

    def create_deployment(self, deployment_object):
        container_port = client.V1ContainerPort(
            container_port=deployment_object.container_port, name=deployment_object.name
        )

        container = client.V1Container(
            image=deployment_object.image,
            name=deployment_object.name,
            env=deployment_object.env,
            ports=[container_port],
        )

        metadata = client.V1ObjectMeta(
            name=deployment_object.name, labels=deployment_object.labels
        )
        template = client.V1PodTemplateSpec(
            metadata=metadata, spec=client.V1PodSpec(containers=[container])
        )

        strategy = client.ExtensionsV1beta1DeploymentStrategy(
            type=deployment_object.strategy_type
        )
        selector = client.V1LabelSelector(match_labels=deployment_object.labels)
        spec = client.ExtensionsV1beta1DeploymentSpec(
            selector=selector, strategy=strategy, template=template
        )

        deployment = client.ExtensionsV1beta1Deployment(
            api_version="apps/v1beta2", kind="Deployment", metadata=metadata, spec=spec
        )

        api_client = client.AppsV1beta2Api()
        api_client.create_namespaced_deployment(body=deployment, namespace="default")


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--type", dest="creator_type")

    return parser.parse_args()


def main():
    config.load_kube_config()
    args = parse_args()

    if args.creator_type == "yaml":
        creator = CreateFromYaml()
    elif args.creator_type == "code":
        creator = CreateFromCode()
    else:
        raise ValueError()

    creator.create_mysql_service()
    creator.create_mysql_deployment()

    creator.create_wordpress_service()
    creator.create_wordpress_deployment()


if __name__ == "__main__":
    main()
