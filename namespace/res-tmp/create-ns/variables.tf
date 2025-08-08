variable "namespace_name" {
  description = "The name of the Kubernetes namespace"
  type        = string
  default     = "demo-namespace"
}

variable "kubeconfig_path" {
  description = "Path to your kubeconfig file"
  type        = string
  default     = "~/.kube/config"
}
