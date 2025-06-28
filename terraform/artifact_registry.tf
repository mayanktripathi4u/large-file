resource "google_artifact_registry_repository" "docker_repo" {
  provider = google-beta

  location     = var.region
  repository_id = "docker-repo"
  description  = "Docker image registry"
  format       = "DOCKER"
}
