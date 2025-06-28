from flask import Flask, request, jsonify
from google.cloud import storage
import os, redis, json
from datetime import timedelta
import requests

app = Flask(__name__)

redis_client = redis.Redis(host='redis', port=6379, decode_responses=True)

@app.route('/get-url/<string:req_id>/<string:task_id>', methods=['GET'])
def get_url(req_id, task_id):
    client = storage.Client()
    bucket = client.bucket(os.environ['GCS_BUCKET_NAME'])
    blob = bucket.blob(f'tasks/{task_id}/image_*.png')

    if not blob.exists():
        return jsonify({'error': 'Image not found'}), 404
    
    url = blob.generate_signed_url(
        version="v4",
        expiration=3600,  # URL valid for 1 hour
        method="GET"
    )

    return jsonify({
        'request_id': req_id,
        'task_id': task_id,
        'signed_url': url
    }), 200

@app.route('/stream-file', methods=['POST'])
def stream_file():
    envelope = request.get_json()
    msg = json.loads(envelope['message']['data'])

    task_id = msg['task_id']
    request_id = msg['request_id']
    filename = msg['filename']

    storage_client = storage.Client()
    bucket_name = os.environ.get('GCS_BUCKET_NAME', 'None')
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(filename)
    url = blob.generate_signed_url(expiration=timedelta(hours=1))

    metadata = json.loads(redis_client.get(task_id))
    metadata['status'] = 'ready'
    metadata['signed_url'] = url
    redis_client.set(task_id, json.dumps(metadata))

    # # Optional callback
    # callback_url = "https://apigee-callback-url"
    # CALLBACK_URL = os.environ.get('CALLBACK_URL', 'https://apigee-callback-url')
    # try:
    #     requests.post(callback_url, json={"task_id": task_id, "request_id": request_id, "signed_url": url})
    # except Exception as e:
    #     print("Callback failed:", e)

    return '', 200

# if __name__ == '__main__':
#     port = int(os.environ.get('PORT', 5000))
#     app.run(host='0.0.0.0', port=port, debug=True)
