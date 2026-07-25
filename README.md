# PredictOps: Self-Healing Infrastructure Platform on Kubernetes

An AI-driven AIOps platform that monitors live infrastructure metrics and automatically scales a Kubernetes deployment using Azure OpenAI as a reasoning engine — built end-to-end on a self-managed Kubernetes cluster on Azure.

## Overview

Most self-healing systems react to failures after they happen. PredictOps takes a different approach: it continuously reads live metrics from Prometheus, sends them to an LLM (Azure OpenAI) for risk assessment, and automatically scales the application in response to predicted load — closing the loop between observability and action.

## Tech Stack

| Layer | Tools |
|---|---|
| Infrastructure (IaC) | Terraform, Azure (Ubuntu VMs) |
| Container Orchestration | Kubernetes (self-managed via kubeadm) |
| Containerization | Docker |
| CI/CD | GitHub Actions |
| Monitoring | Prometheus |
| AI / Decision Engine | Azure OpenAI (GPT-4.1-mini) |
| App | Python (Flask) |
| Access Control | Kubernetes RBAC, Secrets |

## Key Features

- Infrastructure as Code: Entire Azure infrastructure (VMs, networking, NSG) provisioned via Terraform.
- Self-managed Kubernetes cluster: Built manually with kubeadm rather than a managed service (AKS), for deeper infra control and understanding.
- Live monitoring: Prometheus scrapes a custom /metrics endpoint every 15 seconds.
- AI-driven decision-making: A predictor service queries Azure OpenAI with live metrics and gets a real-time SCALE/OK decision.
- Automated remediation: On a "SCALE" decision, the predictor calls the Kubernetes API directly (via a scoped ServiceAccount + RBAC Role) to scale the deployment — no human in the loop.
- CI/CD pipeline: GitHub Actions builds and validates both app and predictor images on every push, then deploys to the cluster via SSH.
- Secure by design: Azure OpenAI credentials are injected via Kubernetes Secrets, never hardcoded; SSH access is IP-restricted at the NSG level.

## Repository Structure

- app.py - Demo Flask service with /metrics endpoint
- Dockerfile - App container image
- predict.py - AI predictor: reads Prometheus, queries Azure OpenAI, scales deployment
- Dockerfile.predictor - Predictor container image
- requirements.txt - Python dependencies
- deployment.yaml - App Deployment + Service (Kubernetes)
- predictor-deployment.yaml - Predictor Deployment (Kubernetes)
- predictor-rbac.yaml - ServiceAccount + Role + RoleBinding for the predictor
- prometheus-config.yaml - Prometheus scrape configuration
- prometheus-deployment.yaml - Prometheus Deployment + Service
- .github/workflows/ci-cd.yml - CI/CD pipeline

## How It Works

1. The demo app exposes a /metrics endpoint returning simulated load data.
2. Prometheus scrapes this endpoint every 15 seconds and stores the time series.
3. The AI predictor pod queries Prometheus for the current metric value.
4. It sends that value to Azure OpenAI with a prompt asking for a risk assessment (SCALE or OK).
5. If the model returns SCALE, the predictor calls the Kubernetes API (via its RBAC-scoped ServiceAccount) to scale the deployment up.
6. This loop runs continuously, so the system responds to changing load without manual intervention.

## Setup

### Prerequisites
- Azure CLI, Terraform, kubectl
- An Azure OpenAI resource with a deployed chat model

### Infrastructure
terraform init
terraform apply

### Cluster bootstrap (on the provisioned VM)
sudo kubeadm init --pod-network-cidr=10.244.0.0/16
kubectl apply -f https://raw.githubusercontent.com/projectcalico/calico/v3.28.0/manifests/calico.yaml

### Deploy the stack
kubectl apply -f deployment.yaml
kubectl apply -f prometheus-config.yaml
kubectl apply -f prometheus-deployment.yaml
kubectl apply -f predictor-rbac.yaml
kubectl create secret generic azure-openai-secret --from-literal=AZURE_ENDPOINT="your-endpoint" --from-literal=AZURE_API_KEY="your-key" --from-literal=DEPLOYMENT_NAME="your-deployment-name"
kubectl apply -f predictor-deployment.yaml

### Watch it work
kubectl logs -f -l app=ai-predictor

## Author

Abu Jor Al Gefari (Saikat)
Azure Cloud & DevOps Engineer | AZ-104 & AZ-305 Certified
GitHub: https://github.com/21saikat
LinkedIn: https://linkedin.com/in/ibnesabidsaikat
