#  DevOps Engineering Case

This repository contains a production-like Kubernetes infrastructure implementation covering the full DevOps lifecycle — from cluster setup to CI/CD pipelines, monitoring, logging, and security.

---

## Architecture Overview

### Infrastructure
- **Platform:** Vagrant + VMware Fusion on Apple Silicon (arm64)
- **Cluster:** 1 control-plane (k8s-master) + 2 worker nodes (node-1, node-2)
- **Kubernetes:** v1.30.14 with kubeadm
- **CNI:** Flannel

### Application
- Java Spring Boot application (port 9001)
- Multi-stage Docker build
- Endpoint: `/api/foos?val=TEST`
- Image: `gizemk/devops-case-app` on DockerHub

---

## Repository Structure

devops_project/
├── app/                          # Java Spring Boot application (submodule)
├── docker/                       # Dockerfile (multi-stage build)
├── jenkins/                      # CI/CD pipeline definitions
│   ├── Jenkinsfile.build         # CI: build & push image with Kaniko
│   └── Jenkinsfile.deploy        # CD: deploy via Ansible
├── ansible/                      # Ansible playbooks and inventory
│   ├── deploy-manifests.yaml     # Main deployment playbook
│   ├── inventories/prod/hosts    # Inventory for k8s-master
│   └── roles/kubectl_apply/      # kubectl set image role
├── k8s/base/
│   ├── app/                      # Application manifests
│   ├── platform/                 # Platform tool configs (Helm values)
│   └── webhook/                  # Admission webhook
├── infra/vagrant/                # Vagrantfile
└── docs/                         # Documentation and Step 4 answers

---

## Step 1: Application & Docker

The Java Spring Boot application is built using a **multi-stage Dockerfile**:
- **Stage 1 (build):** Maven + Eclipse Temurin 17 — compiles and packages the JAR
- **Stage 2 (runtime):** Eclipse Temurin 17 JRE — runs the application as a non-root user

This approach reduces the final image size significantly and improves security.

---

## Step 2: Kubernetes Cluster

### Cluster Setup
Provisioned with `kubeadm` on Vagrant VMs running Ubuntu 20.04 (arm64).

**Key configuration:**
- `--apiserver-advertise-address=10.50.0.10` (eth1, host-only network)
- Flannel CNI with `--iface=eth1` to use the correct network interface
- kubelet configured with `--node-ip` on each node to avoid VMware's auto-assigned interface

> **Design Decision:** Vagrant creates multiple network interfaces per VM. Without explicitly specifying the interface, kubelet and Flannel default to VMware's NAT interface (eth0), causing kube-proxy iptables rules to be written to the wrong interface and breaking service-to-pod communication.

### Jenkins (node-2 only)
Jenkins is pinned to node-2 using `nodeSelector`:
```yaml
nodeSelector:
  kubernetes.io/hostname: node-2
```
Persistent storage is provided via a `hostPath` PersistentVolume on node-2.

### Prometheus + Grafana
Deployed via `kube-prometheus-stack` Helm chart. Includes:
- Pre-built Kubernetes dashboards
- Custom application dashboard: CPU and memory usage per pod in the `app` namespace

### EFK Stack
- **Elasticsearch:** Single-node, security disabled for simplicity
- **Fluent-bit:** DaemonSet on all nodes, collects container logs from `/var/log/containers/`
- **Kibana:** Log visualization with `kubernetes-*` data view

---

## Step 3: Application Deployment

### Kubernetes Manifests
| Resource | Description |
|---|---|
| Deployment | 4 replicas, liveness/readiness probes, resource limits |
| Service | ClusterIP on port 80 |
| Ingress | Nginx Ingress, accessible at `devops-case.local:30080` |
| HPA | CPU 60% / Memory 70%, min 4 max 10 replicas |
| ConfigMap | Application configuration |
| Secret | Sensitive configuration |

### Pod Distribution
`podAntiAffinity` with `preferredDuringSchedulingIgnoredDuringExecution` ensures pods are distributed evenly across node-1 and node-2.

### CI Pipeline (Jenkinsfile.build)
1. Checkout source code including git submodules
2. Build Docker image with **Kaniko** (no Docker daemon required)
3. Push to DockerHub with build number as tag
4. Trigger CD pipeline automatically

> **Design Decision:** Kaniko was chosen over Docker-in-Docker because the cluster uses containerd, not Docker. Running Docker daemon inside a pod would require privileged access and is considered a security anti-pattern in modern Kubernetes environments.

### CD Pipeline (Jenkinsfile.deploy)
1. Checkout source code
2. Run Ansible playbook via SSH to k8s-master
3. `kubectl set image` updates the deployment with the new image tag
4. Wait for rollout to complete

---

## Step 3 (cont.): Admission Webhook

A custom **ValidatingWebhookConfiguration** rejects any Deployment that does not define CPU and memory resource requests.

- Written in Python (Flask)
- TLS-secured with self-signed certificate
- Only validates namespaces labeled `validate-resources: "true"`

**Test:**
```bash
# This will be rejected:
kubectl apply -f deployment-without-resources.yaml
# Error: Container 'app' must have CPU and memory requests defined
```

---

## Step 4: Written Answers

See [`docs/step4/answers.md`](docs/step4/answers.md)

---

## Design Decisions Summary

| Decision | Rationale |
|---|---|
| Kaniko for image builds | No Docker daemon needed; works natively with containerd |
| Ansible for CD | Idempotent deployments; extensible to multi-host environments |
| Flannel with --iface=eth1 | Vagrant multi-interface issue; explicit interface prevents routing failures |
| Security disabled on Elasticsearch | Development/demo environment; production would use TLS + auth |
| Self-signed certs for webhook | Sufficient for demo; production would use cert-manager |
| NodePort for all UIs | No LoadBalancer available in Vagrant; NodePort provides external access |
