# k8s-fastapi-starter
 
A minimal FastAPI service containerized with Docker and deployed to Kubernetes. It is intentionally small, but it is the seed of a larger project: the end-to-end ML pipeline (Portfolio Project #1 = Docker + MLflow + FastAPI + Kubernetes). Today it just returns a version string; the structure is built to be extended into real model serving.
 
## What it demonstrates
 
- Containerizing a Python (FastAPI) app with a cache-aware Dockerfile.
- The Kubernetes object chain: Deployment manages a ReplicaSet, which manages Pods, each wrapping a container.
- Connecting a Service to Pods via label selectors.
- Scaling to multiple replicas.
- Zero-downtime rolling updates and rollbacks.
## Project structure
 
```
k8s-fastapi-starter/
├── app/
│   └── main.py          # FastAPI app: GET / (message + version), GET /health
├── requirements.txt
├── Dockerfile           # requirements copied before code (keeps the pip layer cached)
├── k8s/
│   ├── deployment.yaml  # Deployment: replicas, selector, pod template
│   └── service.yaml     # ClusterIP Service selecting the app pods
└── README.md
```
 
## Prerequisites
 
- Docker
- minikube (Docker driver) + kubectl
## Run it locally (minikube)
 
```bash
# 1. Build the image
docker build -t fastapi-app:v1 .
 
# 2. Make it visible inside the cluster (minikube Docker driver won't see host images otherwise)
minikube image load fastapi-app:v1
 
# 3. Deploy
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
 
# 4. Inspect the object chain
kubectl get deployment,replicaset,pods
 
# 5. Access it (ClusterIP is internal, so port-forward to reach it locally)
kubectl port-forward service/fastapi-service 8080:80
# then, in another terminal:
curl localhost:8080        # {"message":"hello from k8s","version":"v1"}
```
 
## Scale
 
```bash
kubectl scale deployment fastapi-app --replicas=3
kubectl get pods           # three pods, all behind the one Service
```
 
## Rolling update and rollback
 
```bash
# build + load a new version
docker build -t fastapi-app:v2 .
minikube image load fastapi-app:v2
 
# roll it out (watch the old ReplicaSet scale down as the new one scales up)
kubectl set image deployment/fastapi-app fastapi=fastapi-app:v2
kubectl rollout status deployment/fastapi-app
kubectl get replicaset     # old RS at 0, new RS at the desired count
 
# roll back if needed
kubectl rollout undo deployment/fastapi-app
```
 
Note on GitOps hygiene: prefer editing `k8s/deployment.yaml` (bump the image tag) and re-running `kubectl apply` over imperative commands like `kubectl set image`. Mixing the two makes the live state drift from the YAML in this repo, and Kubernetes will warn about the `last-applied-configuration` annotation on rollback. Keep the repo as the single source of truth.
 
## Kubernetes concepts in play
 
- Deployment -> ReplicaSet -> Pod: you manage the Deployment; it creates a ReplicaSet per version; the ReplicaSet keeps the desired number of Pods alive (self-healing).
- Label selector: the Service and the Deployment find their Pods by matching `selector` against Pod `labels`, not by naming pods directly.
- Rolling update: a new ReplicaSet scales up while the old scales down; the old is retained (scaled to 0) to enable rollback.
## Next steps (toward Portfolio Project #1)
 
- [ ] Replace `GET /` with a `POST /predict` endpoint that loads and serves a real model (start with the iris classifier from the earlier Docker exercise).
- [ ] Add `readinessProbe` and `livenessProbe` pointing at `/health` so Kubernetes only routes traffic to ready pods and restarts unhealthy ones.
- [ ] Externalize config with a ConfigMap and credentials with a Secret; mount them into the pod.
- [ ] Add resource `requests`/`limits` to the container spec.
- [ ] Introduce MLflow for model tracking/registry; pull the served model from the registry.
- [ ] Add a CI/CD workflow (build image, run tests, apply manifests).
- [ ] Package the manifests as a Helm chart for dev/staging/prod.
- [ ] Deploy to GKE (ties to the GCP Professional ML Engineer path).