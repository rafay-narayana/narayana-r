
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

