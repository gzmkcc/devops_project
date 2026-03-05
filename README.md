# devops_project
# Dream Games DevOps Engineering Case

This repository contains a production-like DevOps case implementation:
- Java application containerization (multi-stage Docker build)
- 1 master + 2 worker Kubernetes cluster (K8s > 1.25) on Vagrant/VirtualBox
- Platform on K8s: Jenkins (pinned to Node3), Prometheus/Grafana, EFK (Elasticsearch/Kibana/fluent-bit)
- CI pipeline: build & push image to DockerHub
- CD pipeline: deploy manifests via Ansible
- Admission validation webhook: fail deployments missing resource requests

## Topology
- Node1: control-plane
- Node2: worker
- Node3: worker (Jenkins must run only here)

## Quick Links
- docs/architecture.md
- docs/decisions.md
- infra/vagrant/README.md
- k8s/README.md