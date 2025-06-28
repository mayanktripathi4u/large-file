from flask import Flask, request, jsonify
import redis, json

app = Flask(__name__)
redis_client = redis.Redis(host='redis', port=6379, decode_responses=True)

@app.route('/get-task-status', methods=['GET'])
def get_task_status():
    task_id = request.args.get("task_id")
    data = redis_client.get(task_id)
    if not data:
        return jsonify({"error": "Invalid task_id"}), 404
    return jsonify(json.loads(data))