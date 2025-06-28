from flask import Flask, request, jsonify
from faker import Faker
from PIL import Image
import os, io
import numpy as np 
import redis, json
from google.cloud import storage, pubsub_v1

app = Flask(__name__)

fake = Faker()

redis_client = redis.Redis(host='redis', port=6379, decode_responses=True)

# Initialize Google Cloud Pub/Sub client
publisher = pubsub_v1.PublisherClient()
gcp_project_id = os.environ.get('GCP_PROJECT_ID', 'None')
gcp_pubsub_topic = os.environ.get('GCP_PUBSUB_TOPIC_PROCESS', 'None')
topic_path = publisher.topic_path(gcp_project_id, gcp_pubsub_topic)


@app.route('/process', methods=['POST'])
def process_task():
    task_id = request.json.get('task_id')
    request_id = request.json.get('request_id')
    image = Image.new('RGB', (100, 100), color = 'blue')
    image_bytes = io.BytesIO()
    image.save(image_bytes, format='PNG')
    image_bytes.seek(0)

    # Save the image to a GCS bucket
    client = storage.Client()
    bucket = client.bucket(os.environ['GCS_BUCKET_NAME'])
    # blob = bucket.blob(f'tasks/{task_id}/image.png')
    # blob.upload_from_file(image_bytes, content_type='image/png')

    blob = bucket.blob(f'tasks/{task_id}/image_{fake.uuid4()}.png')
    blob.upload_from_file(image_bytes, content_type='image/png')


    return jsonify({
        'task_id': task_id,
        'request_id': request_id,
        'status': 'Task processed successfully'
    }), 200


def generate_image_with_target_size(target_size_mb = 12, format='PNG'):
    """
    Generate a random image with the specified target size.
    """
    # image = Image.new('RGB', target_size_mb, color = 'blue')
    # image_bytes = io.BytesIO()
    # image.save(image_bytes, format='PNG')
    # image_bytes.seek(0)
    # return image_bytes

    target_bytes = target_size_mb * 1024 * 1024  # Convert MB to bytes
    width = height = 1024  # Start with a 1024x1024 image
    step = 256

    while True:
        array = np.random.randint(0, 256, (height, width, 3), dtype=np.uint8)
        image = Image.fromarray(array)
        image_bytes = io.BytesIO()
        image.save(image_bytes, format=format)
        size = image_bytes.tell()  # Get the size of the image in bytes
        if size >= target_bytes:
            print(f"Geenrated Image Size: {size / (1024 * 1024):.2f} MB")
            image.save(f"random_task_id_{target_size_mb}MB_image.{format.lower()}", format=format)
            break
        width += step
        height += step

    return image_bytes

## Based on Push Subscription from Pub/Sub Topic: <defined in gcp_pubsub_topic>
@app.route('/process-task', methods=['POST'])
def process_task():
    envelope = request.get_json()
    msg = json.loads(envelope['message']['data'])

    task_id = msg['task_id']
    request_id = msg['request_id']

    content = 'X' * 11 * 1024 * 1024
    filename = f"{task_id}.txt"
    storage_client = storage.Client()
    bucket_name = os.environ.get('GCS_BUCKET_NAME', 'None')
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(filename)
    blob.upload_from_string(content)

    redis_client.set(task_id, json.dumps({"request_id": request_id, "status": "uploaded", "filename": filename}))
    publisher.publish(topic_path, data=json.dumps({"task_id": task_id, "request_id": request_id, "filename": filename}).encode("utf-8"))
    return '', 200


# if __name__ == '__main__':
#     port = int(os.environ.get('PORT', 5000))
#     app.run(host='0.0.0.0', port=port, debug=True)