## Step 4 - Question 1: Scaling App X Under Heavy Load

### Problem
We have a limited cluster with two applications:
- **App X**: Real-time application, cannot be interrupted
- **App Y**: Batch job manager, can be killed and restarted

### Solution

#### 1. PriorityClass
We define two PriorityClass objects to differentiate between applications:
- `high-priority-realtime` (value: 1000000) → App X
- `low-priority-batch` (value: 1000) → App Y

When the cluster is under heavy load and App X needs more resources, 
Kubernetes preempts (evicts) App Y pods to free up resources for App X.
This works well because App Y manages batch jobs that can be safely 
interrupted and restarted later.

#### 2. HPA (Horizontal Pod Autoscaler)
App X uses HPA with CPU-based scaling:
- Minimum replicas: 2
- Maximum replicas: 10
- Scale up when CPU > 60%

#### Sample Manifest
See: `k8s/base/step4/q1-manifest.yaml`

## Step 4 - Question 2: Canary Deployments

### Tool: Argo Rollouts

Argo Rollouts is a Kubernetes controller that provides advanced deployment 
strategies including canary releases with fine-grained traffic control.

### How It Works

1. New version is deployed as a canary alongside the stable version
2. Traffic is gradually shifted: 10% → 30% → 50% → 100%
3. Metrics are monitored at each step (via Prometheus integration)
4. If error rate exceeds threshold → automatic rollback
5. If metrics are healthy → continue rollout

### Pipeline Management (Jenkinsfile.deploy)

```groovy
stage('Canary Deploy') {
    steps {
        // Deploy canary with 10% traffic
        sh "ansible-playbook ansible/deploy-manifests.yaml -e 'canary=true weight=10'"
    }
}
stage('Canary Analysis') {
    steps {
        // Wait and check metrics
        sh "sleep 300"
        sh "ansible-playbook ansible/check-metrics.yaml"
    }
}
stage('Full Rollout') {
    steps {
        sh "ansible-playbook ansible/deploy-manifests.yaml -e 'canary=false'"
    }
}
```

### Why Argo Rollouts?
- Native Kubernetes integration
- Prometheus metric analysis built-in
- Automatic rollback on failure
- Traffic split via Nginx Ingress annotations


## Step 4 - Question 3: Scheduled Scaling

### 3a: Scaling Before/After Specific Times

#### Solution: KEDA with Cron Scaler

KEDA (Kubernetes Event Driven Autoscaling) supports cron-based scaling, 
which allows us to scale applications before traffic spikes occur.

```yaml
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: app-x-scheduled-scaling
  namespace: app
spec:
  scaleTargetRef:
    name: app-x
  minReplicaCount: 2
  maxReplicaCount: 20
  triggers:
  - type: cron
    metadata:
      timezone: Europe/Istanbul
      start: "0 8 * * *"    # Scale up at 08:00
      end: "0 22 * * *"     # Scale down at 22:00
      desiredReplicas: "10"
```

This ensures App X scales out before high traffic periods and scales 
in afterwards, preventing users from experiencing high response times.

### 3b: Increasing Node Count Before Specific Times

#### Cloud Provider Solutions

**AWS:** Use Scheduled Scaling for Auto Scaling Groups (ASGs)
- Set desired/minimum capacity to increase at specific times
- Nodes are ready before traffic hits

**GCP:** Use Cloud Scheduler to trigger GKE node pool resize
- `gcloud container clusters resize` at scheduled times

**Azure:** AKS Scheduled Scaling via Azure Automation
- Modify node count of scaleset on schedule

#### On-Premise / Vagrant Environment
For non-cloud environments, a Jenkins job or Ansible playbook can be 
scheduled via CronJob to:
1. SSH into the host machine
2. Run `vagrant up node-X` to provision a new node
3. Run kubeadm join to add node to cluster

This can be triggered 15-30 minutes before expected traffic peaks.

#### Why Scale Nodes Before Pods?
New nodes take 2-5 minutes to join the cluster and become ready. 
If we only scale pods, they may stay Pending while waiting for node capacity.
By scaling nodes first (e.g., 15 minutes before peak), 
pods can be scheduled immediately when traffic arrives.
