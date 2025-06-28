data "google_client_config" "default" {}

resource "kubernetes_namespace" "default" {
  metadata {
    name = "default"
  }
}

resource "kubernetes_deployment" "api1" {
  metadata {
    name = "api1"
  }
  spec {
    replicas = 1
    selector {
      match_labels = {
        app = "api1"
      }
    }
    template {
      metadata {
        labels = {
          app = "api1"
        }
      }
      spec {
        container {
          image = "gcr.io/your-project/api1-create-task:latest"
          name  = "api1"
          port {
            container_port = 5000
          }
          env {
            name  = "GCP_PROJECT_ID"
            value = var.project_id
          }
          env {
            name  = "GCP_PUBSUB_TOPIC_CREATE"
            value = "topic-create-task"
          }
        }
      }
    }
  }
}