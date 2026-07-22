# Kubernetes Deployment Guide

## Overview

This directory contains Kubernetes manifests for deploying AEGIS LENS databases (PostgreSQL, TimescaleDB, Neo4j, Redis) to a Kubernetes cluster.

## Prerequisites

- Kubernetes cluster (minikube, kind, or cloud provider)
- kubectl configured to access your cluster
- kustomize (optional, can be installed via deploy.sh)

## Quick Start

1. **Copy environment template:**
   ```bash
   cp .env.example .env
   ```

2. **Edit .env with your passwords:**
   ```bash
   nano .env
   ```

3. **Deploy to Kubernetes:**
   ```bash
   ./deploy.sh
   ```

## Manual Deployment

If you prefer manual deployment:

1. **Create namespace:**
   ```bash
   kubectl apply -f base/namespace.yaml
   ```

2. **Create ConfigMaps:**
   ```bash
   kubectl apply -f base/configmaps/
   ```

3. **Create Secrets (replace with actual values):**
   ```bash
   export POSTGRES_PASSWORD=your_password
   export TIMESCALE_PASSWORD=your_password
   export NEO4J_PASSWORD=your_password
   export REDIS_PASSWORD=your_password
   
   envsubst < base/secrets/postgres-secret.yaml | kubectl apply -f -
   envsubst < base/secrets/timescale-secret.yaml | kubectl apply -f -
   envsubst < base/secrets/neo4j-secret.yaml | kubectl apply -f -
   envsubst < base/secrets/redis-secret.yaml | kubectl apply -f -
   ```

4. **Deploy databases:**
   ```bash
   kubectl apply -k base/
   ```

## Components

### PostgreSQL
- **Deployment:** 1 replica
- **Storage:** 10Gi PVC
- **Port:** 5432
- **Resources:** 256Mi-1Gi memory, 250m-1000m CPU

### TimescaleDB
- **Deployment:** 1 replica
- **Storage:** 20Gi PVC
- **Port:** 5432
- **Resources:** 512Mi-2Gi memory, 500m-2000m CPU

### Neo4j
- **Deployment:** 1 replica
- **Storage:** 10Gi PVC
- **Ports:** 7474 (HTTP), 7687 (Bolt)
- **Resources:** 512Mi-2Gi memory, 250m-1000m CPU

### Redis
- **Deployment:** 1 replica
- **Storage:** 5Gi PVC
- **Port:** 6379
- **Resources:** 128Mi-512Mi memory, 100m-500m CPU

## Verification

Check deployment status:
```bash
kubectl get pods -n aegis-lens
kubectl get services -n aegis-lens
kubectl get pvc -n aegis-lens
```

View logs:
```bash
kubectl logs -n aegis-lens deployment/postgres
kubectl logs -n aegis-lens deployment/timescaledb
kubectl logs -n aegis-lens deployment/neo4j
kubectl logs -n aegis-lens deployment/redis
```

## Scaling

To scale deployments:
```bash
kubectl scale deployment postgres --replicas=2 -n aegis-lens
kubectl scale deployment timescaledb --replicas=2 -n aegis-lens
```

Note: Scaling stateful databases requires additional configuration for high availability.

## Cleanup

To remove all resources:
```bash
kubectl delete -k base/
kubectl delete namespace aegis-lens
```

## Troubleshooting

### Pods not starting
```bash
kubectl describe pod <pod-name> -n aegis-lens
kubectl logs <pod-name> -n aegis-lens
```

### PVC issues
```bash
kubectl get pvc -n aegis-lens
kubectl describe pvc <pvc-name> -n aegis-lens
```

### Service connectivity
```bash
kubectl exec -it -n aegis-lens <pod-name> -- sh
# Test service connectivity from within pod
```

## Production Considerations

1. **Storage Class:** Configure appropriate storage class for your cloud provider
2. **Resource Limits:** Adjust based on actual workload requirements
3. **High Availability:** Configure replicas and read replicas for production
4. **Backup:** Implement backup strategies for all databases
5. **Monitoring:** Add Prometheus exporters for monitoring
6. **Security:** Use network policies and RBAC for access control
