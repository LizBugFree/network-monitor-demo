# Cloud Network Monitoring Dashboard

## Project Overview

A cloud-native network monitoring tool that provides real-time visibility into Google Cloud Platform network infrastructure. Built by a networking engineer for networking engineers, this tool addresses the gap between traditional network monitoring and cloud-native environments by providing intuitive dashboards and automated alerting for cloud network performance.

## Business Problem

**Challenge**: Traditional network monitoring tools don't provide adequate visibility into cloud networking components like VPCs, subnets, NAT gateways, and inter-AZ traffic patterns. Cloud engineers often lack the networking expertise to identify performance bottlenecks, while network engineers struggle with cloud-specific monitoring tools.

**Solution**: A purpose-built monitoring dashboard that bridges this gap by presenting cloud network data in familiar networking terminology with actionable insights.

## Key Features

### 1. Network Topology Visualization
- **Real-time VPC network mapping**
- **Subnet relationships and firewall rules**
- **Cloud NAT and Cloud Router status**
- **Load balancer and firewall rule relationships**

### 2. Performance Monitoring
- **Inter-region and inter-zone latency tracking**
- **Cloud NAT utilization and costs**
- **Load balancer performance metrics**
- **Egress traffic costs by resource**

### 3. Intelligent Alerting
- **Firewall rule changes detection**
- **Route changes in Cloud Router**
- **VPC peering modifications**
- **Unusual traffic pattern alerts**

### 4. Cost Analytics
- **Egress traffic cost breakdown**
- **Cloud NAT cost optimization suggestions**
- **Unused external IP identification**
- **Cross-zone traffic cost analysis**

## Technical Implementation

### Backend Architecture
- **Language**: Python (google-cloud libraries, pandas, flask)
- **Compute**: Cloud Functions for serverless data collection
- **Storage**: Firestore for time-series metrics, Cloud Storage for static assets
- **Orchestration**: Cloud Scheduler for scheduled data collection
- **APIs**: Cloud Endpoints or Cloud Run for REST APIs

### Frontend
- **Framework**: React with Chart.js for visualizations
- **Hosting**: Cloud Storage with Cloud CDN
- **Authentication**: Firebase Auth (optional for demo)

### Infrastructure as Code
- **Tool**: Terraform for complete infrastructure deployment
- **Modules**: Reusable components for different regions

## Repository Structure
```
network-monitor/
├── README.md
├── docs/
│   ├── architecture.md
│   ├── api-documentation.md
│   └── deployment-guide.md
├── terraform/
│   ├── main.tf
│   ├── lambda.tf
│   ├── api-gateway.tf
│   ├── dynamodb.tf
│   └── variables.tf
├── backend/
│   ├── cloud_functions/
│   │   ├── network_collector.py
│   │   ├── metric_processor.py
│   │   └── alert_handler.py
│   ├── shared/
│   │   ├── gcp_utils.py
│   │   └── data_models.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── utils/
│   ├── public/
│   └── package.json
└── scripts/
    ├── deploy.sh
    ├── test-connectivity.py
    └── sample-data-generator.py
```

## Core Metrics Collected

### Network Infrastructure
- VPC network count and configurations
- Subnet utilization (available IP ranges)
- Cloud Router routes and BGP sessions
- Cloud NAT gateway status and utilization
- Load balancer health and performance

### Performance Data
- Cloud Monitoring network metrics (sent/received bytes/packets)
- Inter-zone and inter-region data transfer volumes
- Load balancer response times and error rates
- Cloud NAT active connections and bandwidth

### Security & Compliance
- Firewall rule changes and modifications
- VPC Flow Logs analysis (top talkers, protocols)
- Unused firewall rules and external IPs
- IAM changes related to network resources

### Cost Optimization
- Egress traffic costs by service and region
- Cloud NAT vs instance-based NAT cost comparison
- Unused external IP addresses
- Over-provisioned load balancers

## Dashboard Views

### 1. Network Overview
- Total VPCs, subnets, and resources
- Network health score
- Recent changes timeline
- Cost trend over time

### 2. Topology Map
- Interactive network diagram
- Resource relationships
- Traffic flow visualization
- Drill-down capabilities

### 3. Performance Analytics
- Latency heatmaps by AZ
- Throughput trends
- Error rate monitoring
- Capacity utilization

### 4. Cost Management
- Monthly data transfer costs
- Cost per AZ and service
- Optimization recommendations
- Budget tracking and forecasting

## Technologies Demonstrated

### Cloud Services (GCP)
- Cloud Functions (Serverless computing)
- Firestore (NoSQL database)
- Cloud Endpoints/Cloud Run (REST APIs)
- Cloud Monitoring (Monitoring and logging)
- Cloud Storage (Static hosting)
- Cloud Scheduler (Cron jobs)
- IAM (Security and permissions)

### Development Skills
- Python backend development
- REST API design and implementation
- React frontend with data visualization
- Infrastructure as Code with Terraform
- Automated testing and deployment

### Networking Knowledge Applied
- Understanding of GCP networking services
- Network performance analysis
- Cost optimization strategies
- Security best practices
- Troubleshooting methodologies

## Sample Insights Generated

### Performance Optimization
- "Cloud NAT in us-central1-a is processing 80% more traffic than others - consider redistributing workloads"
- "Cross-zone traffic increased 40% this week - review application architecture"

### Cost Optimization  
- "3 unused external IPs are costing $10.95/month"
- "Moving workload to same zone could save $150/month in egress charges"

### Security & Compliance
- "Firewall rule 'allow-ssh-from-anywhere' allows 0.0.0.0/0 on port 22 - security risk"
- "Cloud Router 'main-router' routes were modified 2 hours ago - review changes"

## Getting Started

### Prerequisites
- Google Cloud Platform account with billing enabled
- Terraform installed locally
- Python 3.9+ and Node.js 16+
- Google Cloud CLI configured

### Quick Start
```bash
# Clone repository
git clone https://github.com/[username]/network-monitor
cd network-monitor

# Deploy infrastructure
cd terraform
terraform init
terraform plan
terraform apply

# Deploy application code
cd ../scripts
./deploy.sh

# Access dashboard
echo "Dashboard URL: $(terraform output dashboard_url)"
```