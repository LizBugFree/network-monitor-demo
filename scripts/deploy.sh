# deploy.sh - Deployment script
#!/bin/bash

# Set variables
PROJECT_ID=$(gcloud config get-value project)
REGION="us-central1"
FUNCTIONS_SOURCE_DIR="./cloud_functions"

echo "Deploying Cloud Functions to project: $PROJECT_ID"
echo "Region: $REGION"

# Enable required APIs
echo "Enabling required Google Cloud APIs..."
gcloud services enable compute.googleapis.com
gcloud services enable monitoring.googleapis.com  
gcloud services enable firestore.googleapis.com
gcloud services enable cloudfunctions.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable cloudscheduler.googleapis.com

# Create service account for Cloud Functions
echo "Creating service account..."
gcloud iam service-accounts create network-monitor-functions \
    --description="Service account for network monitoring Cloud Functions" \
    --display-name="Network Monitor Functions"

# Grant necessary permissions
echo "Granting IAM permissions..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:network-monitor-functions@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/compute.viewer"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:network-monitor-functions@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/monitoring.viewer"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:network-monitor-functions@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/datastore.user"

# Deploy network data collector function
echo "Deploying network data collector function..."
gcloud functions deploy network-data-collector \
    --gen2 \
    --runtime=python311 \
    --region=$REGION \
    --source=$FUNCTIONS_SOURCE_DIR \
    --entry-point=network_data_collector \
    --trigger=http \
    --service-account=network-monitor-functions@$PROJECT_ID.iam.gserviceaccount.com \
    --memory=512MB \
    --timeout=540s \
    --set-env-vars=GCP_PROJECT=$PROJECT_ID \
    --allow-unauthenticated

# Deploy network metrics collector function  
echo "Deploying network metrics collector function..."
gcloud functions deploy network-metrics-collector \
    --gen2 \
    --runtime=python311 \
    --region=$REGION \
    --source=$FUNCTIONS_SOURCE_DIR \
    --entry-point=network_metrics_collector \
    --trigger=http \
    --service-account=network-monitor-functions@$PROJECT_ID.iam.gserviceaccount.com \
    --memory=1GB \
    --timeout=540s \
    --set-env-vars=GCP_PROJECT=$PROJECT_ID \
    --allow-unauthenticated

echo "Getting function URLs..."
DATA_COLLECTOR_URL=$(gcloud functions describe network-data-collector --region=$REGION --format="value(serviceConfig.uri)")
METRICS_COLLECTOR_URL=$(gcloud functions describe network-metrics-collector --region=$REGION --format="value(serviceConfig.uri)")

echo "Function URLs:"
echo "Network Data Collector: $DATA_COLLECTOR_URL"
echo "Network Metrics Collector: $METRICS_COLLECTOR_URL"

# Test functions
echo "Testing functions..."
echo "Testing network data collector..."
curl -X POST $DATA_COLLECTOR_URL

echo "Testing network metrics collector..."
curl -X POST $METRICS_COLLECTOR_URL

echo "Deployment completed successfully!"