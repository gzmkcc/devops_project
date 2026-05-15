from flask import Flask, request, jsonify
import json

app = Flask(__name__)

@app.route('/validate', methods=['POST'])
def validate():
    admission_review = request.get_json()
    
    # Extract the deployment object
    deployment = admission_review['request']['object']
    
    # Check all containers for resource requests
    containers = deployment['spec']['template']['spec']['containers']
    
    for container in containers:
        resources = container.get('resources', {})
        requests = resources.get('requests', {})
        
        if 'cpu' not in requests or 'memory' not in requests:
            return jsonify({
                "apiVersion": "admission.k8s.io/v1",
                "kind": "AdmissionReview",
                "response": {
                    "uid": admission_review['request']['uid'],
                    "allowed": False,
                    "status": {
                        "message": f"Container '{container['name']}' must have CPU and memory requests defined"
                    }
                }
            })
    
    return jsonify({
        "apiVersion": "admission.k8s.io/v1",
        "kind": "AdmissionReview",
        "response": {
            "uid": admission_review['request']['uid'],
            "allowed": True
        }
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8443, 
            ssl_context=('/certs/tls.crt', '/certs/tls.key'))