# Deployment Guide

## Prerequisites

- Git account on GitHub
- Docker and Docker Compose (for local deployment)
- kubectl and Kubernetes cluster (for K8s deployment)

## GitHub Deployment Instructions

Since GitHub CLI is not installed, follow these steps to deploy:

### Step 1: Create GitHub Repository

1. Go to [GitHub](https://github.com/new)
2. Create a new repository named `knowledge-graph-api`
3. Choose public or private based on your preference
4. **DO NOT** initialize with README (we already have one)
5. Click "Create repository"

### Step 2: Add Remote and Push

```bash
cd /Users/nithinkumarjada/knowledge-graph-api

# Add the remote (replace USERNAME with your GitHub username)
git remote add origin https://github.com/USERNAME/knowledge-graph-api.git

# Rename branch to main (if needed)
git branch -M main

# Push code to GitHub
git push -u origin main
```

### Step 3: Configure GitHub Secrets (for CI/CD)

Go to your repository → Settings → Secrets and variables → Actions

Add these secrets:
- `DOCKER_USERNAME` - Your Docker Hub username
- `DOCKER_PASSWORD` - Your Docker Hub access token

## Local Deployment with Docker Compose

### Quick Start

```bash
cd /Users/nithinkumarjada/knowledge-graph-api

# Start all services
docker-compose up -d

# Check logs
docker-compose logs -f api

# Stop services
docker-compose down
```

The API will be available at `http://localhost:8000`

### Environment Configuration

Edit `docker-compose.yml` to change:
- Neo4j password
- PostgreSQL password
- API debug mode
- Ports

## Production Deployment

### Option 1: Docker Hub

```bash
# Build image
docker build -t yourusername/knowledge-graph-api:1.0.0 .

# Push to Docker Hub
docker push yourusername/knowledge-graph-api:1.0.0
```

### Option 2: Kubernetes

```bash
# Create namespace
kubectl create namespace knowledge-graph

# Create secrets
kubectl create secret generic knowledge-graph-secrets \
  --from-literal=neo4j-user=neo4j \
  --from-literal=neo4j-password=your-password \
  --from-literal=database-url=postgresql://user:pass@host:5432/db \
  --from-literal=secret-key=your-secret-key \
  -n knowledge-graph

# Create config map
kubectl create configmap knowledge-graph-config \
  --from-literal=neo4j-uri=bolt://neo4j-service:7687 \
  -n knowledge-graph

# Deploy
kubectl apply -f k8s/deployment.yaml -n knowledge-graph

# Check deployment
kubectl get pods -n knowledge-graph
kubectl get svc -n knowledge-graph
```

## Testing

```bash
# Run unit tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=app --cov-report=html
```

## Monitoring

### Health Check

```bash
curl http://localhost:8000/health
```

### API Documentation

Open `http://localhost:8000/docs` in your browser (Swagger UI)

### Logs

```bash
# Docker
docker-compose logs -f api

# Kubernetes
kubectl logs -f deployment/knowledge-graph-api -n knowledge-graph
```

## Troubleshooting

### Neo4j Connection Issues

```bash
# Check if Neo4j is running
docker-compose ps

# Rebuild Neo4j
docker-compose down -v
docker-compose up neo4j
```

### PostgreSQL Issues

```bash
# Check database
docker exec knowledge-graph-postgres psql -U postgres -d knowledge_graph_audit -c "\dt"

# Reset database
docker-compose down -v
docker-compose up postgres
```

### API Issues

```bash
# Check logs
docker-compose logs api

# Rebuild
docker-compose build --no-cache api
docker-compose up api
```

## Environment Variables

Create `.env` file in project root:

```env
# Neo4j
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-secure-password

# PostgreSQL
DATABASE_URL=postgresql://postgres:password@localhost:5432/knowledge_graph_audit

# API
SECRET_KEY=your-256-bit-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application
DEBUG=False
APP_NAME=Knowledge Graph Query API
API_VERSION=1.0.0
```

## Scaling Considerations

1. **Database**: Use Neo4j Aura or managed service in production
2. **Message Queue**: Add Celery/RabbitMQ for async tasks
3. **Caching**: Add Redis for query caching
4. **Load Balancer**: Use Nginx or Kubernetes ingress
5. **Monitoring**: Add Prometheus and Grafana

## Security Checklist

- [ ] Change all default passwords
- [ ] Generate new SECRET_KEY
- [ ] Enable HTTPS/TLS
- [ ] Configure CORS appropriately
- [ ] Set up firewall rules
- [ ] Enable database backups
- [ ] Configure audit logging
- [ ] Set up monitoring and alerts
- [ ] Use environment variables for secrets
- [ ] Review and test authentication
