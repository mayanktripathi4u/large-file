output "cluster_name" {
  value = google_container_cluster.primary.name
}

output "gcs_bucket" {
  value = google_storage_bucket.largefile_bucket.name
}

output "pubsub_topics" {
  value = [
    google_pubsub_topic.create_task.name,
    google_pubsub_topic.process_done.name
  ]
}