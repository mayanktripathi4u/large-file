resource "google_storage_bucket" "largefile_bucket" {
  name     = var.gcs_bucket_name
  location = var.region
  force_destroy = true
  uniform_bucket_level_access = true
}
