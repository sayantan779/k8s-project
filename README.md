***

# Hello World Python – Prometheus & Grafana on Kubernetes

Simple Flask “Hello World” application instrumented with Prometheus metrics, containerized with Docker, and deployed to Kubernetes with Prometheus Operator (kube‑prometheus‑stack) and Grafana.

## Project structure

```text
hello/
├── Dockerfile                # Builds app image with Flask + prometheus_client
├── hello.py                  # Flask app exposing / and /metrics
├── helloDeploy.yaml          # Kubernetes Deployment (pod annotations for scraping)
├── helloService.yaml         # Service exposing port 5000 (named port http)
├── hello-servicemonitor.yaml # ServiceMonitor for kube-prometheus-stack
```

## Prerequisites

- Docker (or any OCI‑compatible image build tool)  
- Kubernetes cluster (kind, minikube, k3d, etc.) with `kubectl` configured  
- Prometheus Operator installed via `kube-prometheus-stack` Helm chart in a `monitoring` namespace with release name `prometheus-stack`

Example Helm install:

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
kubectl create namespace monitoring
helm install prometheus-stack prometheus-community/kube-prometheus-stack -n monitoring
```

## Build and push the Docker image

Update `IMAGE` to your own registry repository:

```bash
cd hello

IMAGE=<your-registry>/hello-world:latest

docker build -t $IMAGE .
docker push $IMAGE
```

Update the `image:` field in `helloDeploy.yaml` to match `IMAGE` if needed.

## Deploy the app and monitoring manifests

```bash
kubectl apply -f helloDeploy.yaml          # Deployment
kubectl apply -f helloService.yaml         # Service
kubectl apply -f hello-servicemonitor.yaml # ServiceMonitor
```

- Deployment runs two replicas labeled `app: hello-app` and annotated for Prometheus scraping on `/metrics` at port `5000`.  
- Service selects `app: hello-app`, exposes port `5000` as a named port `http`, and can be reached via NodePort or port‑forward.  
- ServiceMonitor in namespace `monitoring` selects the Service with label `app: hello-app` and scrapes `/metrics` every 15 seconds using port `http`.

Check resources:

```bash
kubectl get pods -l app=hello-app
kubectl get svc hello-python-service
kubectl get servicemonitor -n monitoring hello-servicemonitor
```

## Generate traffic and verify metrics

Port‑forward the service and hit the application:

```bash
kubectl port-forward svc/hello-python-service 5000:5000
curl http://localhost:5000/
curl http://localhost:5000/metrics | head
```

The `/metrics` endpoint exposes both default Python client metrics and custom metrics such as `helloworld_requests_total` and `helloworld_request_latency_seconds`.

## View in Prometheus and Grafana

- **Prometheus UI**  
  - Port‑forward Prometheus from the `monitoring` namespace.  
  - Open the Prometheus UI and check “Status → Targets” for a job referencing `hello-servicemonitor`; its state should be `UP`.

- **Grafana**  
  - Port‑forward Grafana from the `monitoring` namespace.  
  - Log in using the admin credentials stored in the Grafana secret.  
  - Use the configured Prometheus data source and create a dashboard or use Explore with queries such as:
    - `helloworld_requests_total`
    - `rate(helloworld_request_latency_seconds_bucket[5m])`

This demonstrates end‑to‑end instrumentation of a Python service on Kubernetes with Prometheus and Grafana observability.
