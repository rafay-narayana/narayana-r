resource "random_string" "random" {
  length  = 8
  special = false # Avoids special characters
  upper   = false # Lowercase only
}

resource "rafay_ztkarule" "custom_rule" {
  count = var.enable_kubeconfig ? 1 : 0
  metadata {
    name = "custom-ztkarule-cluster-${random_string.random.result}"
  }
  spec {
    artifact {
      type = "Yaml"
      artifact {
        paths {
          name = "file://rule.yaml"
        }
      }
      options {
        force                       = true
        disable_open_api_validation = true
      }
    }
    cluster_selector {
      match_names = [
        var.cluster_name
      ]
    }
    project_selector {
    match_names = [
        var.project
      ]
    }
      
    version = random_string.random.result
  }
}

resource "rafay_ztkapolicy" "custom_policy" {
  depends_on = [rafay_ztkarule.custom_rule]
  count = var.enable_kubeconfig ? 1 : 0
  metadata {
    name = "custom-ztkapolicy-cluster-${random_string.random.result}"
  }
  spec {
    ztka_rule_list {
      name    = rafay_ztkarule.custom_rule.0.id
      version = rafay_ztkarule.custom_rule.0.spec[0].version
    }
    version = random_string.random.result
  }
}

resource "rafay_customrole" "custom_customrole" {
  depends_on = [rafay_ztkapolicy.custom_policy]
  count = var.enable_kubeconfig ? 1 : 0
  metadata {
    name = "custom-customrole-${random_string.random.result}"
  }
  spec {
    ztka_policy_list {
      name    = rafay_ztkapolicy.custom_policy.0.id
      version = rafay_ztkapolicy.custom_policy.0.spec[0].version
    }
    base_role = "PROJECT_ADMIN"
  }
}

resource "rafay_group" "custom_group" {
  depends_on  = [rafay_customrole.custom_customrole]
  count = var.enable_kubeconfig ? 1 : 0
  name        = "custom-group-cluster-${random_string.random.result}"
  description = "custom group for cluster"
}

resource "rafay_groupassociation" "groupassociation" {
  depends_on   = [rafay_group.custom_group]
  count = var.enable_kubeconfig ? 1 : 0
  group        = rafay_group.custom_group.0.name
  project      = var.project
  custom_roles = [rafay_customrole.custom_customrole.0.id]
  add_users    = [var.username]
}

data "external" "env" {
  program = ["sh", "-c", "echo '{\"value\": \"'\"$RCTL_REST_ENDPOINT\"'\"}'"]
}