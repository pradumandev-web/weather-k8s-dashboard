# 🌦️ K8s Weather Dashboard

> A production-style Kubernetes project featuring a weather dashboard with Redis caching, PostgreSQL persistence, Helm packaging, NGINX Ingress, Prometheus/Grafana monitoring, and GitHub Actions CI/CD.

---

## 🏗️ Architecture

```
GitHub Push → GitHub Actions CI/CD
                ↓ builds & pushes Docker images
            Docker Hub
                ↓ Helm deploys to
        Minikube Cluster
            ├── Frontend  (nginx, port 80)
            ├── Backend   (Flask, port 5000)
            ├── Redis     (cache, 5 min TTL)
            ├── PostgreSQL (search history + favourites)
            └── Ingress   (weather.local → frontend/backend)
```

---

## 📦 Tech Stack

| Layer | Technology |
|---|---|
| Frontend | HTML + CSS + JavaScript |
| Backend | Python Flask |
| Database | PostgreSQL 15 |
| Cache | Redis 7 |
| Container | Docker |
| Orchestration | Kubernetes (Minikube) |
| Packaging | Helm |
| Routing | NGINX Ingress |
| Monitoring | Prometheus + Grafana |
| CI/CD | GitHub Actions + Trivy |

---

## 🚀 Quick Start

### Prerequisites
```bash
# Install these tools first:
# 1. Docker Desktop
# 2. Minikube
# 3. kubectl
# 4. Helm
```

### Step 1 — Start Minikube
```bash
minikube start --memory=4096 --cpus=2
minikube addons enable ingress
```

### Step 2 — Add your secrets
Edit `helm/weather-chart/templates/secret.yaml` and replace the base64 values:
```bash
echo -n "your-postgres-password" | base64
echo -n "your-openweathermap-api-key" | base64
```

### Step 3 — Update values.yaml
Edit `helm/weather-chart/values.yaml`:
```yaml
backend:
  image: yourdockerhubid/weather-backend
frontend:
  image: yourdockerhubid/weather-frontend
```

### Step 4 — Build & Push Docker Images
```bash
docker build -t yourdockerhubid/weather-backend:latest ./app/backend
docker build -t yourdockerhubid/weather-frontend:latest ./app/frontend
docker push yourdockerhubid/weather-backend:latest
docker push yourdockerhubid/weather-frontend:latest
```

### Step 5 — Deploy with Helm
```bash
helm install weather ./helm/weather-chart
```

### Step 6 — Add DNS entry
```bash
echo "$(minikube ip) weather.local" | sudo tee -a /etc/hosts
```

### Step 7 — Open in browser
```
http://weather.local
```

---

## 📊 Monitoring Setup

### Install Prometheus + Grafana via Helm
```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm install monitoring prometheus-community/kube-prometheus-stack

# Access Grafana (default: admin/prom-operator)
kubectl port-forward svc/monitoring-grafana 3000:80
```
Open http://localhost:3000

---

## 🔧 Useful Commands

```bash
# Check all running resources
kubectl get all

# Check pod logs
kubectl logs -l app=backend -f
kubectl logs -l app=postgres -f

# Upgrade after changes
helm upgrade weather ./helm/weather-chart

# Uninstall
helm uninstall weather

# SSH into Minikube
minikube ssh

# Check Ingress
kubectl get ingress
kubectl describe ingress weather-ingress
```

---

## 🔐 GitHub Actions Setup

Add these secrets in your GitHub repo (Settings → Secrets):

| Secret | Value |
|---|---|
| `DOCKER_HUB_USER` | Your Docker Hub username |
| `DOCKER_HUB_TOKEN` | Docker Hub access token |

---

## 📁 Project Structure

```
k8s-weather-dashboard/
├── app/
│   ├── backend/
│   │   ├── app.py              # Flask API
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   └── frontend/
│       ├── index.html          # Weather UI
│       └── Dockerfile
├── helm/
│   └── weather-chart/
│       ├── Chart.yaml
│       ├── values.yaml         ← Master config
│       └── templates/
│           ├── configmap.yaml
│           ├── secret.yaml
│           ├── backend.yaml
│           ├── frontend.yaml
│           ├── postgres.yaml   # Includes PVC
│           ├── redis.yaml
│           └── ingress.yaml
├── .github/
│   └── workflows/
│       └── ci-cd.yaml
└── README.md
```

---

## ✨ Features

- 🌐 **Live weather data** from OpenWeatherMap API
- ⚡ **Redis caching** — shows whether data came from cache or API
- 🗄️ **PostgreSQL** — persistent search history + favourite cities
- 🔐 **Secrets management** — API keys and passwords via K8s Secrets
- ⚙️ **ConfigMap** — all config centralised, no hardcoding
- 📦 **Helm** — one command deploy/upgrade
- 🌍 **NGINX Ingress** — domain-based routing
- 📊 **Prometheus + Grafana** — pod monitoring dashboards
- 🔄 **GitHub Actions** — automated build, Trivy security scan, deploy