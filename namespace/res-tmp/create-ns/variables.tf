variable "namespace_name" {
  description = "The name of the Kubernetes namespace"
  type        = string
  default     = "demo-namespace"
}

variable "kubeconfig_content" {
  description = "Full kubeconfig file content"
  type        = string
}
