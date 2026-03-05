# Kubernetes Manifests

## Base
k8s/base/app contains:
- Deployment (4+ replicas)
- Service
- Ingress (nginx)
- ConfigMap/Secret
- HPA

## Scheduling
Pods should be evenly distributed across Node2 and Node3.
Approach: podAntiAffinity + topologyKey = kubernetes.io/hostname

## Platform
k8s/base/platform will host:
- Jenkins (must be scheduled only on Node3)
- Monitoring (Prometheus/Grafana)
- Logging (Elasticsearch/Kibana/fluent-bit)