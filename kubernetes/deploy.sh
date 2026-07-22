#!/bin/bash
# Kubernetes deployment script for AEGIS LENS

set -e

echo "Deploying AEGIS LENS to Kubernetes..."

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null
then
    echo "kubectl not found. Please install kubectl first."
    exit 1
fi

# Check if kustomize is installed
if ! command -v kustomize &> /dev/null
then
    echo "kustomize not found. Installing..."
    # Install kustomize
    curl -s "https://raw.githubusercontent.com/kubernetes-sigs/kustomize/master/hack/install_kustomize.sh" | bash
fi

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
else
    echo "Warning: .env file not found. Using default values."
fi

# Apply secrets with environment variables
envsubst < base/secrets/postgres-secret.yaml | kubectl apply -f -
envsubst < base/secrets/timescale-secret.yaml | kubectl apply -f -
envsubst < base/secrets/neo4j-secret.yaml | kubectl apply -f -
envsubst < base/secrets/redis-secret.yaml | kubectl apply -f -

# Apply base configuration
kubectl apply -k base/

echo "Waiting for deployments to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/postgres -n aegis-lens
kubectl wait --for=condition=available --timeout=300s deployment/timescaledb -n aegis-lens
kubectl wait --for=condition=available --timeout=300s deployment/neo4j -n aegis-lens
kubectl wait --for=condition=available --timeout=300s deployment/redis -n aegis-lens

echo "Deployment complete!"
echo "Checking pod status..."
kubectl get pods -n aegis-lens

echo "Checking services..."
kubectl get services -n aegis-lens
