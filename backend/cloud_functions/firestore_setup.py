import json
from google.cloud import firestore

def initialize_firestore():
    """Initialize Firestore database with proper indexes and collections"""
    
    try:
        db = firestore.Client()
        
        # Create initial collections with sample documents to establish structure
        print("Initializing Firestore collections...")
        
        # Network inventory collection
        network_inventory_ref = db.collection('network-inventory')
        network_inventory_ref.document('_schema').set({
            'description': 'Network resource inventory snapshots',
            'fields': {
                'timestamp': 'ISO datetime string',
                'project_id': 'GCP project ID',
                'networks': 'Array of VPC networks',
                'subnetworks': 'Array of subnets',
                'firewall_rules': 'Array of firewall rules',
                'routers': 'Array of Cloud Routers',
                'nat_gateways': 'Array of Cloud NAT gateways'
            }
        })
        
        # Individual networks collection
        networks_ref = db.collection('networks')
        networks_ref.document('_schema').set({
            'description': 'Individual VPC network records',
            'fields': {
                'name': 'Network name',
                'id': 'Network ID',
                'project_id': 'GCP project ID',
                'timestamp': 'Collection timestamp',
                'auto_create_subnetworks': 'Boolean',
                'routing_mode': 'REGIONAL or GLOBAL'
            }
        })
        
        # Subnetworks collection
        subnetworks_ref = db.collection('subnetworks')
        subnetworks_ref.document('_schema').set({
            'description': 'Individual subnet records',
            'fields': {
                'name': 'Subnet name',
                'id': 'Subnet ID', 
                'region': 'GCP region',
                'network': 'Parent network name',
                'ip_cidr_range': 'CIDR range',
                'available_ips': 'Number of available IPs',
                'timestamp': 'Collection timestamp'
            }
        })
        
        # Firewall rules collection
        firewall_rules_ref = db.collection('firewall-rules')
        firewall_rules_ref.document('_schema').set({
            'description': 'Firewall rule records',
            'fields': {
                'name': 'Rule name',
                'network': 'Network name',
                'direction': 'INGRESS or EGRESS',
                'priority': 'Rule priority (integer)',
                'allowed_ports': 'Array of allowed protocols/ports',
                'source_ranges': 'Array of source IP ranges',
                'timestamp': 'Collection timestamp'
            }
        })
        
        # Network metrics collection
        network_metrics_ref = db.collection('network-metrics')
        network_metrics_ref.document('_schema').set({
            'description': 'Time-series network metrics',
            'fields': {
                'metric_type': 'GCP metric type',
                'resource_type': 'GCP resource type',
                'resource_labels': 'Resource identification labels',
                'metric_labels': 'Metric-specific labels',
                'timestamp': 'Metric timestamp',
                'value': 'Metric value (numeric)',
                'collection_timestamp': 'When metric was collected'
            }
        })
        
        # Metrics summaries collection
        metrics_summaries_ref = db.collection('metrics-summaries')
        metrics_summaries_ref.document('_schema').set({
            'description': 'Aggregated metrics summaries',
            'fields': {
                'timestamp': 'Collection timestamp',
                'project_id': 'GCP project ID',
                'collection_period_minutes': 'Time window for metrics',
                'metrics_count': 'Count of metrics by category'
            }
        })
        
        print("Firestore collections initialized successfully!")
        
        # Note: Indexes need to be created via Firebase Console or gcloud CLI
        print("\nRemember to create these composite indexes:")
        print("1. Collection: network-metrics")
        print("   Fields: project_id (Ascending), metric_type (Ascending), timestamp (Descending)")
        print("2. Collection: networks") 
        print("   Fields: project_id (Ascending), timestamp (Descending)")
        print("3. Collection: subnetworks")
        print("   Fields: project_id (Ascending), region (Ascending), timestamp (Descending)")
        print("\nCreate indexes at: https://console.firebase.google.com/")
        
    except Exception as e:
        print(f"Error initializing Firestore: {str(e)}")
        raise

if __name__ == '__main__':
    initialize_firestore()