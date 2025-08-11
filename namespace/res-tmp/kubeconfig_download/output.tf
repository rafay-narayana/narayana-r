output "kubeconfig_cluster" {
  description = "kubeconfig_cluster"
  value       = data.rafay_download_kubeconfig.kubeconfig_cluster.kubeconfig
}
