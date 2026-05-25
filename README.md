# 🌤️ WeatherK8s Dashboard

A production-grade weather dashboard deployed on Kubernetes with full monitoring, persistent storage, and CI/CD pipeline.

---

## 📋 Project Overview

A complete microservices-based weather application demonstrating real-world Kubernetes deployment patterns:

- Multi-container orchestration (4 microservices)
- Persistent storage with PostgreSQL
- Redis caching layer
- Liveness & readiness health probes
- ConfigMaps and Secrets management
- Prometheus metrics + Grafana dashboards
- Helm chart packaging
- GitHub Actions CI/CD pipeline

---

## 🏗️ Architecture

```
          ┌─────────────┐
          │ User Browser│
          └──────┬──────┘
                 │
        ┌────────▼────────┐
        │ Ingress/NodePort│
        └────────┬────────┘
                 │
    ┌────────────┼────────────┐
    │            │            │
┌───▼───┐   ┌───▼───┐   ┌────▼────┐
│Frontend│  │Backend│   │PostgreSQL│
│(Nginx) │→ │(Flask)│→  │(History) │
│Port:80 │  │Pt:5000│   │Pt:5432  │
└────────┘  └───┬───┘   └─────────┘
         ┌──────┼──────┐
         │      │      │
     ┌───▼──┐ ┌─▼──┐ ┌─▼──────────┐
     │Redis │ │Ext.│ │ Prometheus  │
     │Cache │ │API │ │ + Grafana   │
     │:6379 │ │    │ │ Monitoring  │
     └──────┘ └────┘ └────────────┘
```

---

## ✨ Features

### Core Application
- **Real-time Weather Search** — Search any city using OpenWeatherMap API
- **Search History** — Persistent history stored in PostgreSQL with timestamps
- **Favorites System** — Save and manage favorite cities
- **Redis Caching** — 10-minute cache for faster API responses
- **Responsive UI** — Modern, mobile-friendly dashboard

### Kubernetes
- Multi-container deployment across 4 microservices
- Persistent Volumes (data survives pod restarts)
- ConfigMaps & Secrets for configuration management
- Liveness and readiness health probes
- Internal DNS-based service discovery
- Helm chart for easy deployment and versioning

### Monitoring & Observability
- Prometheus metrics at `/metrics` endpoint
- Grafana dashboards for real-time visualization
- Custom metrics:
  - `weather_api_requests_total` — Total API calls
  - `weather_api_errors_total` — Error count

### DevOps & CI/CD
- Multi-stage Docker builds
- GitHub Actions pipeline (build → scan → push → deploy)
- Trivy security vulnerability scanning
- Automated Helm image tag updates on new builds

---

## 🛠️ Tech Stack

| Component | Technology | Version |
|-----------|------------|---------|
| Frontend | HTML5, CSS3, JavaScript | — |
| Backend | Python Flask | 3.11 |
| Database | PostgreSQL | 15 |
| Cache | Redis | 7-alpine |
| Container | Docker | — |
| Orchestration | Kubernetes (Minikube) | v1.33.1 |
| Package Manager | Helm | v3.18.3 |
| Monitoring | Prometheus + Grafana | — |
| CI/CD | GitHub Actions | — |
| Security Scan | Trivy | — |

---

## 📁 Project Structure

```
k8s-weather-dashboard/
├── .github/
│   └── workflows/
│       └── ci-cd.yaml             # GitHub Actions pipeline
├── app/
│   ├── backend/
│   │   ├── app.py                 # Flask API with metrics
│   │   ├── requirements.txt
│   │   └── Dockerfile             # Multi-stage build
│   └── frontend/
│       ├── index.html             # Dashboard UI
│       └── Dockerfile             # Nginx static server
├── helm/
│   └── weather-chart/
│       ├── Chart.yaml
│       ├── values.yaml
│       └── templates/
│           ├── backend.yaml       # Backend deployment + service
│           ├── frontend.yaml
│           ├── postgres.yaml      # PostgreSQL with PVC
│           ├── redis.yaml
│           ├── configmap.yaml
│           ├── secret.yaml
│           └── ingress.yaml
├── patch-backend.yaml
├── patch-frontend.yaml
├── patch-postgres.yaml
├── patch-redis.yaml
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites

- Docker Desktop (with Kubernetes enabled)
- Minikube v1.36+
- kubectl v1.34+
- Helm v3.18+
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/praduman127/weather-k8s-dashboard.git
cd weather-k8s-dashboard
```

### 2. Start Minikube

```bash
minikube start --memory=4096 --cpus=2 --driver=docker
minikube addons enable ingress
```

### 3. Load Docker Images

```bash
minikube image load praduman127/weather-backend:local
minikube image load praduman127/weather-frontend:local
minikube image load postgres:15
minikube image load redis:7-alpine
```

### 4. Configure API Key

Get a free API key from [OpenWeatherMap](https://openweathermap.org/api), then:

```bash
# Encode your key
echo -n "your-api-key" | base64

# Paste the output into helm/weather-chart/templates/secret.yaml
```

### 5. Deploy with Helm

```bash
helm install weather ./helm/weather-chart
```

### 6. Access the Application

```bash
# Frontend URL
minikube service frontend-service --url

# Port-forward backend (separate terminal)
kubectl port-forward svc/backend-service 5000:5000
```

---

## 📊 Monitoring Setup

### Grafana

```bash
kubectl port-forward -n monitoring svc/monitoring-grafana 3000:80
```

- URL: `http://localhost:3000`
- Username: `admin`
- Password:

```bash
kubectl get secret -n monitoring monitoring-grafana \
  -o jsonpath="{.data.admin-password}" | base64 -d
```

### Prometheus

```bash
kubectl port-forward -n monitoring svc/monitoring-kube-prometheus-prometheus 9090:9090
```

- URL: `http://localhost:9090`

### Import Kubernetes Dashboard in Grafana

1. Click **+** → **Import**
2. Enter Dashboard ID: `315`
3. Click **Load**
4. Select the Prometheus data source
5. Click **Import**

---

## 🔌 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/metrics` | GET | Prometheus metrics |
| `/api/weather/{city}` | GET | Get weather for a city |
| `/history` | GET | Get search history |
| `/favorites` | GET | List favorite cities |
| `/favorites` | POST | Add city to favorites |
| `/favorites/{city}` | DELETE | Remove city from favorites |

---

## 🧪 Testing

### Run Backend Locally

```bash
cd app/backend
pip install -r requirements.txt
python app.py
```

### Test API Endpoints

```bash
# Health check
curl http://localhost:5000/health

# Get weather
curl http://localhost:5000/api/weather/London

# Prometheus metrics
curl http://localhost:5000/metrics
```

### Verify Kubernetes Deployment

```bash
kubectl get pods
kubectl logs -f deployment/backend
kubectl get svc
```

---

## 🔧 Troubleshooting

**ImagePullBackOff**
```bash
minikube image load <image-name>:<tag>
```

**Port Already in Use**
```bash
kubectl port-forward svc/backend-service 5001:5000
```

**Pods Not Ready**
```bash
kubectl describe pod <pod-name>
kubectl logs <pod-name>
kubectl rollout restart deployment
```

**Database Connection Issues**
```bash
kubectl exec -it deployment/postgres -- psql -U weatheruser -d weatherdb
# Inside psql:
\dt
SELECT * FROM search_history;
```

---

## 🔄 CI/CD Pipeline

The GitHub Actions pipeline automates:

1. **Build** — Docker images for backend and frontend
2. **Push** — Images to Docker Hub
3. **Security Scan** — Trivy vulnerability scanning
4. **Helm Update** — Automated image tag updates in `values.yaml`

### Required GitHub Secrets

| Secret | Description |
|--------|-------------|
| `DOCKER_HUB_USER` | Docker Hub username |
| `DOCKER_HUB_TOKEN` | Docker Hub access token |

---

## 📈 Future Enhancements

- [ ] User authentication (JWT)
- [ ] 5-day weather forecast view
- [ ] Weather alerts and notifications
- [ ] Deploy to cloud (AWS EKS / Azure AKS)
- [ ] End-to-end tests with Cypress
- [ ] Infrastructure as Code with Terraform
- [ ] GitOps with ArgoCD

---

## 📝 Lessons Learned

**Kubernetes** — Deployments, Services, Ingress, Persistent Volumes & Claims, ConfigMaps, Secrets, liveness/readiness probes

**Helm** — Templating with values, chart structure, template functions

**Monitoring** — Prometheus client integration, ServiceMonitor/PodMonitor configuration, Grafana dashboard creation

**CI/CD** — GitHub Actions workflows, Docker build & push automation, security scanning integration

---

## 🙏 Acknowledgments

- [OpenWeatherMap](https://openweathermap.org/) for the free weather API
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Prometheus Community](https://prometheus.io/)
- TechWorld with Nana — Kubernetes tutorial series

---

## 📄 License

MIT License

---

## 👨‍💻 Author

**Praduman**

- GitHub: [@praduman127](https://github.com/praduman127)
- LinkedIn: [linkedin.com/in/praduman-dev-9b6b66367](https://linkedin.com/in/praduman-dev-9b6b66367)

---

⭐ If this project helped you, please give it a star on GitHub!