# Architecture

## Goals
- Reproducible infra with Vagrant/VirtualBox
- K8s cluster version > 1.25
- CI/CD with Jenkins on Kubernetes
- Observability: Prometheus + Grafana
- Logging: fluent-bit -> Elasticsearch -> Kibana (internet accessible with auth)

## Nodes
- Node1 (master/control-plane)
- Node2 (worker)
- Node3 (worker)
  - Jenkins workloads are scheduled only to Node3 (nodeSelector/affinity + taints/tolerations if needed)

## Workflows
1) CI (Jenkinsfile.build)
   - Build multi-stage image
   - Push to DockerHub
2) CD (Jenkinsfile.deploy)
   - Run Ansible playbook
   - Apply K8s manifests
   - Verify rollout + health checks

## App runtime requirements
- >=4 pods across worker nodes
- balanced behind NGINX ingress
- readiness/liveness probes enabled
- HPA enabled