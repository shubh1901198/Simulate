# Simulate — Docker & Kubernetes quick guide

This repository contains two small Python scripts:
- `simulate_trip_a.py` — generates Trip A CSV rows
- `compare_trips.py` — compares Trip A rows with last 10 Trip B rows using thresholds

This README shows quick steps to run with Docker locally, and to run on Kubernetes (as a Job).

Prerequisites
- Docker installed (or Minikube / kind for local Kubernetes)
- kubectl configured for your cluster (minikube, kind, or cloud cluster)

1) Build the Docker image locally

Use this command from the repository root (the Dockerfile is named `dockerfile`):

```bash
docker build -t trip-simulation:local -f dockerfile .
```

2) Run the container locally (one-shot batch)

This project runs as a batch job (it generates CSV and then compares). Run the image directly:

```bash
# simple local run
docker run --rm -v "$PWD":/app -w /app trip-simulation:local
```

Notes:
- The container copies the repo into the image, so data files can be inside the image. Mounting `$PWD` into `/app` lets the container write outputs into your working directory.

3) Push image to a registry (if deploying to remote k8s)

Tag and push to your registry (Docker Hub example):

```bash
docker tag trip-simulation:local your-dockerhub-username/trip-simulation:latest
docker push your-dockerhub-username/trip-simulation:latest
```

Update `k8s/job.yaml` to use the pushed image name.

4) Run on Kubernetes as a Job (recommended for batch jobs)

- If you're using Minikube:

```bash
# Option A: load local image into minikube
minikube image load trip-simulation:local
# then apply the job
kubectl apply -f k8s/job.yaml
kubectl get jobs
kubectl logs job/trip-simulation-job
```

- If you pushed to a remote registry, set `image` in `k8s/job.yaml` to that image and simply:

```bash
kubectl apply -f k8s/job.yaml
kubectl get pods --selector=app=trip-simulation
kubectl logs job/trip-simulation-job
```

5) Alternative: Deployment/Service (not required)

The existing `k8s/deployment.yaml` and `k8s/service.yaml` assume a long-running HTTP process on port 8080. This project is batch-oriented and does not run an HTTP server by default.

If you want a long-running service exposing 8080, update the Python code (e.g., add a small Flask/uvicorn app) and expose that port from the container (add `EXPOSE 8080` to the Dockerfile). Otherwise prefer the Job manifest.

Troubleshooting
- If CSV/threshold files are missing, the scripts will exit with an error. Mount or include these files in the image or set up a volume.
- For Minikube image usage, `minikube image load` is the easiest path. For kind, use `kind load docker-image`.

If you'd like, I can:
- build and run the Docker image locally now, OR
- update the `k8s/deployment.yaml` to a Job or a CronJob automatically, OR
- change the Dockerfile to expose a small HTTP health endpoint so the Deployment/Service makes sense.

Tell me which of the above you'd like me to do next and I'll proceed.

