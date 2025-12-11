#!/bin/bash
set -e

echo "🚀 Setting up Monitoring Stack (Prometheus + Loki + Grafana)..."

# Add Helm Repos
echo "📦 Adding Helm Repos..."
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update

# Create Namespace
echo "📂 Creating 'monitoring' namespace..."
kubectl create namespace monitoring --dry-run=client -o yaml | kubectl apply -f -

# Install Prometheus
echo "📉 Installing Prometheus..."
helm upgrade --install prometheus prometheus-community/prometheus \
  --namespace monitoring \
  -f monitoring/prometheus-values.yaml

# Install Loki
echo "📝 Installing Loki..."
helm upgrade --install loki grafana/loki-stack \
  --namespace monitoring \
  -f monitoring/loki-values.yaml

# Install Grafana
echo "📊 Installing Grafana..."
helm upgrade --install grafana grafana/grafana \
  --namespace monitoring \
  -f monitoring/grafana-values.yaml

echo "✅ Monitoring stack deployed!"
echo "➡️  Access Grafana:"
echo "   kubectl get svc -n monitoring grafana"
echo "   Password: admin"
