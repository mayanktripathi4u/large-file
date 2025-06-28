from flask import Flask, request, jsonify
import requests, json, uuid, os, time, redis
from google.cloud import pubsub_v1

app = Flask(__name__)

redis_client = redis.Redis(host='redis', port=6379, decode_responses=True)

# Initialize Google Cloud Pub/Sub client
publisher = pubsub_v1.PublisherClient()
gcp_project_id = os.environ.get('GCP_PROJECT_ID', 'None')
gcp_pubsub_topic = os.environ.get('GCP_PUBSUB_TOPIC_CREATE', 'None')
topic_path = publisher.topic_path(gcp_project_id, gcp_pubsub_topic)


@app.route('/start/<string:request_id>', methods=['GET'])
def start_task(request_id):
    # Generate a task ID to simulate task creation. Its purpose is to uniquely identify the task.
    # So using timestamp or UUID is a good practice.
    task_id = str(uuid.uuid4())

    # Trigger API-2 (Process Task API) to start processing the task.
    requests.post('http://process_task_api:5000/process', json={
        'task_id': task_id,
        'request_id': request_id
    } )
    return jsonify({'task_id': task_id, 'status': 'Task started successfully'}), 200


@app.route('/create-task', methods=['GET'])
def create_task():
    request_id = request.args.get("request_id")
    task_id = str(uuid.uuid4())

    redis_client.set(task_id, json.dumps({"request_id": request_id, "status": "created"}))
    message = json.dumps({"task_id": task_id, "request_id": request_id})
    publisher.publish(topic_path, data=message.encode("utf-8"))

    return jsonify({"task_id": task_id, 'status': 'Task started successfully'}), 200


# if __name__ == '__main__':
#     port = int(os.environ.get('PORT', 5000))
#     app.run(host='0.0.0.0', port=port, debug=True)
