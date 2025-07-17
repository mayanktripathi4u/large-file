resource "google_pubsub_topic" "create_task" {
  name = "topic-create-task"
}

resource "google_pubsub_topic" "process_done" {
  name = "topic-process-done"
}