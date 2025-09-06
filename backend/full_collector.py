from network_collector import GCPNetworkCollector
from metrics_collector import GCPMetricsCollector
from shared.data_models import DataProcessor
import json
import os
from datetime import datetime

def collect_all_data():
    """Collect both network resources and metrics"""
    project_id = os.environ.get('GOOGLE_CLOUD_PROJECT')
    if not project_id:
        import subprocess
        try:
            result = subprocess.run(['gcloud', 'config', 'get-value', 'project'], 
                                  capture_output=True, text=True)
            project_id = result.stdout.strip()
        except:
            print("Could not determine project ID")
            return None
    
    print(f"Collecting complete network data for project: {project_id}")
    print("="*70)
    
    # Collect network resources
    network_collector = GCPNetworkCollector(project_id)
    network_data = network_collector.collect_all_data()
    
    print("\n" + "="*70)
    
    # Try to collect metrics (may fail, that's okay)
    try:
        metrics_collector = GCPMetricsCollector(project_id)
        metrics_data = metrics_collector.collect_all_instance_metrics()
        network_data['metrics'] = metrics_data
    except Exception as e:
        print(f"Metrics collection failed (this is normal): {e}")
        network_data['metrics'] = {}
    
    # Process data and generate insights
    processor = DataProcessor(network_data)
    summary = processor.get_network_summary()
    security_insights = processor.get_security_insights()
    cost_insights = processor.get_cost_insights()
    
    # Add insights to data
    network_data['summary'] = {
        'total_networks': summary.total_networks,
        'total_subnets': summary.total_subnets,
        'total_instances': summary.total_instances,
        'total_firewall_rules': summary.total_firewall_rules
    }
    network_data['insights'] = {
        'security': security_insights,
        'cost': cost_insights
    }
    
    # Save complete data
    output_file = 'complete_network_data.json'
    with open(output_file, 'w') as f:
        json.dump(network_data, f, indent=2, default=str)
    
    print("\n" + "="*70)
    print("COLLECTION COMPLETE!")
    print(f"Data saved to: {output_file}")
    print("\nSummary:")
    print(f"  📊 Networks: {summary.total_networks}")
    print(f"  🌐 Subnets: {summary.total_subnets}")
    print(f"  💻 Instances: {summary.total_instances}")
    print(f"  🔥 Firewall Rules: {summary.total_firewall_rules}")
    
    if security_insights:
        print(f"\n🔒 Security Insights:")
        for insight in security_insights:
            print(f"  {insight}")
    
    if cost_insights:
        print(f"\n💰 Cost Insights:")
        for insight in cost_insights:
            print(f"  {insight}")
    
    return network_data

if __name__ == "__main__":
    collect_all_data()