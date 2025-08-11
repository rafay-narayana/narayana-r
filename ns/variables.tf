variable "namespace_name" {
  description = "The name of the Kubernetes namespace"
  type        = string
  default     = "demo-namespace"
}

variable "host_cluster_name" {
  description = "The name of the cluster"
  type        = string
  validation {
    condition     = length(var.host_cluster_name) > 0
    error_message = "The cluster name must not be empty."
  }
}

variable "status" {
   description = "Allow user to control the nginx deployment"
   type = string
   default = no
}
