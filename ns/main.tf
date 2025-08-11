
data "rafay_download_kubeconfig" "kubeconfig_cluster" {
  cluster = var.host_cluster_name
}

resource "local_file" "kubeconfig" {
  lifecycle {
    ignore_changes = all
  }
  depends_on = [data.rafay_download_kubeconfig.kubeconfig_cluster]
  content    = data.rafay_download_kubeconfig.kubeconfig_cluster.kubeconfig
  filename   = "/tmp/test/host-kubeconfig.yaml"
}

resource "null_resource" "host_kubeconfig_ready" {
  depends_on = [local_file.kubeconfig]
  provisioner "local-exec" {
    command = "while [ ! -f /tmp/test/host-kubeconfig.yaml ]; do sleep 1; done"
  }
}

# Create namespace
resource "kubernetes_namespace" "ns" {
  metadata {
    name = var.namespace_name
  }
}

resource "kubernetes_deployment" "nginx" {
 count = var.status == "yes" ? 1 : 0
 depends_on = [null_resource.host_kubeconfig_ready, kubernetes_namespace.ns]
 metadata {
  name   = "nginx-deployment"
  namespace = var.namespace_name
  labels = {
   app = "nginx"
  }
 }
 spec {
  replicas = 1
  selector {
   match_labels = {
    app = "nginx"
   }
  }
  template {
   metadata {
    labels = {
     app = "nginx"
    }
   }
   spec {
    container {
     name = "nginx"
     image = "nginx:latest"
     port {
      container_port = 80
     }
    }
   }
  }
 }
}
resource "kubernetes_service" "nginx" {
 count = var.status == "yes" ? 1 : 0
 depends_on = [kubernetes_deployment.nginx]
 metadata {
  name   = "nginx-service"
  namespace = var.namespace_name
 }
 spec {
  selector = {
   app = "nginx"
  }
  port {
   port    = 80
   target_port = 80
  }
  type = "ClusterIP"
 }
}
