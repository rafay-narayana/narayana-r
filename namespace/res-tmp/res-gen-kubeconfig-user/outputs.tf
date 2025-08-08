output "kubeconfig" {
  description = "ZTKA kubeconfig of the cluster"
  value       = data.rafay_download_kubeconfig.kubeconfig_cluster.kubeconfig
  sensitive = true
}

output "host" {
  description = "kubeconfig host"
  value = yamldecode(data.rafay_download_kubeconfig.kubeconfig_cluster.kubeconfig).clusters[0].cluster.server 
  sensitive = true
}

output "clientcertificatedata" {
  description = "kubeconfig client certificate data"
  value = yamldecode(data.rafay_download_kubeconfig.kubeconfig_cluster.kubeconfig).users[0].user.client-certificate-data
  sensitive = true
}

output "clientkeydata" {
  description = "kubeconfig client key data"
  value = yamldecode(data.rafay_download_kubeconfig.kubeconfig_cluster.kubeconfig).users[0].user.client-key-data
  sensitive = true
}

output "certificateauthoritydata" {
  description = "kubeconfig certificate authority data"
  value = yamldecode(data.rafay_download_kubeconfig.kubeconfig_cluster.kubeconfig).clusters[0].cluster.certificate-authority-data 
  sensitive = true
}