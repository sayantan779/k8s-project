from flask import Flask
from prometheus_client import Counter, Histogram, generate_latest
import time

app = Flask(__name__)

# Metrics
REQUEST_COUNT = Counter("helloworld_requests_total", "Total request count")
REQUEST_LATENCY = Histogram("helloworld_request_latency_seconds", "Request latency")

@app.route("/")
def hello():
    start = time.time()
    REQUEST_COUNT.inc()
    response = "Hello World from Python — with Prometheus!"
    REQUEST_LATENCY.observe(time.time() - start)
    return response

@app.route("/metrics")
def metrics():
    return generate_latest(), 200

if __name__ == "__main__":
    # THIS LINE WAS MISSING — it starts the web server
    app.run(host="0.0.0.0", port=5000)
