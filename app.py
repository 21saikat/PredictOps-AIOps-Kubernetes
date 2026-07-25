from flask import Flask, Response
import random, time

app = Flask(__name__)
request_count = 0

@app.route('/')
def home():
    global request_count
    request_count += 1
    return "PredictOps demo service is running!"

@app.route('/health')
def health():
    return {"status": "ok"}

@app.route('/metrics')
def metrics():
    cpu_sim = random.uniform(10, 90)
    return Response(
        f"app_request_count {request_count}\napp_cpu_simulated {cpu_sim}\n",
        mimetype="text/plain"
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
