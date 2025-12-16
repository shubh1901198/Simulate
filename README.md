## 📦 Container Registry – GitHub Container Registry (GHCR)

This project uses **GitHub Container Registry (GHCR)** to store and version Docker images
used for Kubernetes-based simulation jobs.

### Why GHCR?
- Native integration with GitHub Actions
- No external registry credentials required
- Secure, versioned container storage
- Ideal for CI/CD and Kubernetes workflows

### Image Publishing Flow
1. Docker image is built using GitHub Actions
2. Image is pushed to GHCR as a container package
3. Each commit is tagged for traceability
4. Image is deployed to a local KinD Kubernetes cluster

### Example Image Tags
```text
ghcr.io/<org>/trip-simulation:latest
ghcr.io/<org>/trip-simulation:<commit-sha>

## 📦 Container Registry – GitHub Container Registry (GHCR)

This project uses **GitHub Container Registry (GHCR)** to store and version Docker images
used for Kubernetes-based simulation jobs.

### Why GHCR?
- Native integration with GitHub Actions
- No external registry credentials required
- Secure, versioned container storage
- Ideal for CI/CD and Kubernetes workflows

### Image Publishing Flow
1. Docker image is built using GitHub Actions
2. Image is pushed to GHCR as a container package
3. Each commit is tagged for traceability
4. Image is deployed to a local KinD Kubernetes cluster

### Example Image Tags
```text
ghcr.io/<org>/trip-simulation:latest
ghcr.io/<org>/trip-simulation:<commit-sha>


┌──────────────────┐
│   GitHub Repo    │
│ (Source Code)    │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ GitHub Actions   │
│ CI Pipeline      │
│ - Build Docker   │
│ - Push to GHCR   │
└────────┬─────────┘
         │
         ▼
┌────────────────────────────┐
│ GitHub Container Registry  │
│ (GHCR - Docker Package)    │
│ trip-simulation            │
└────────┬───────────────────┘
         │
         ▼
┌──────────────────┐
│ KinD Kubernetes  │
│ - Job Execution  │
│ - Simulation     │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Reports & Logs   │
│ CSV / Logs       │
│ Email + Artifacts│
└──────────────────┘
