# Design Decisions

## Cluster provisioning
- Tooling: kubeadm (or kubespray) chosen because: <why>
- K8s version: <exact version>

## Jenkins placement (Node3 only)
- Approach: node label + nodeSelector OR affinity
- Rationale: deterministic scheduling, isolation

## Observability stack
- Helm charts used for: prometheus-stack / grafana
- Dashboard strategy: kubernetes + application dashboards

## Logging stack
- fluent-bit reads stdout and ships to Elasticsearch
- Kibana exposed via ingress with authentication

## Application logging performance issue (stdout)
Proposed design:
- Async file logging
- Daily rotation
- Size limit 1GB per file
- Shipping strategy: sidecar tailing files OR node-level agent reading files
(Details to be filled in Step2.4 note)

## GitOps (bonus)
- Deferred for initial implementation
- Potential tooling: Argo CD / Flux
- Would manage: app + platform manifests + canary strategy