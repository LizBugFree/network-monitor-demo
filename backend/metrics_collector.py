from google.cloud import monitoring_v3
from google.cloud import compute_v1
from datetime import datetime, timedelta
import json
import os

class GCPMetricsCollector:
    def __init__(self, project_id):
        self.project_id = project_id
        self.monitoring_client = monitoring_v3.MetricServiceClient()
        self.project_name = f"projects/{project_id}"
        
    def get_instance_metrics(self, instance_name, zone, hours_back=1):
        """Get network metrics for a specific instance"""
        print(f"Collecting metrics for instance: {instance_name}")
        
        # Time range - last hour
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours_back)
        
        metrics_data = {}
        
        # List of network metrics we want to collect
        metric_types = [
            'compute.googleapis.com/instance/network/received_bytes_count',
            'compute.googleapis.com/instance/network/sent_bytes_count',
            'compute.googleapis.com/instance/network/received_packets_count',
            'compute.googleapis.com/instance/network/sent_packets_count',
        ]
        
        for metric_type in metric_types:
            try:
                # Create time interval
                interval = monitoring_v3.TimeInterval({
                    "end_time": end_time,
                    "start_time": start_time,
                })
                
                # Create the request
                request = monitoring_v3.ListTimeSeriesRequest({
                    "name": self.project_name,
                    "filter": f'metric.type="{metric_type}" AND resource.labels.instance_name="{instance_name}" AND resource.labels.zone="{zone}"',
                    "interval": interval,
                    "view": monitoring_v3.ListTimeSeriesRequest.TimeSeriesView.FULL,
                })
                
                # Make the request with timeout
                results = self.monitoring_client.list_time_series(request=request, timeout=10)
                
                # Process results
                values = []
                for result in results:
                    for point in result.points:
                        values.append({
                            'timestamp': point.interval.end_time.isoformat(),
                            'value': point.value.double_value or point.value.int64_value
                        })
                
                metrics_data[metric_type] = values
                print(f"  Found {len(values)} data points for {metric_type.split('/')[-1]}")
                
            except Exception as e:
                print(f"  Warning: Could not get {metric_type}: {e}")
                metrics_data[metric_type] = []
        
        return metrics_data
    
    def collect_all_instance_metrics(self):
        """Collect metrics for all instances"""
        print("Collecting metrics for all instances...")
        
        # First, get list of all instances
        compute_client = compute_v1.InstancesClient()
        request = compute_v1.AggregatedListInstancesRequest(project=self.project_id)
        instance_list = compute_client.aggregated_list(request=request)
        
        all_metrics = {}
        
        for zone, response in instance_list:
            if hasattr(response, 'instances') and response.instances:
                for instance in response.instances:
                    if instance.status == 'RUNNING':
                        zone_name = zone.split('/')[-1]
                        metrics = self.get_instance_metrics(instance.name, zone_name)
                        all_metrics[f"{instance.name}_{zone_name}"] = metrics
        
        if not all_metrics:
            print("No running instances found for metric collection")
            # Create some sample data for testing
            all_metrics['sample_instance'] = self.create_sample_metrics()
        
        return all_metrics
    
    def create_sample_metrics(self):
        """Create sample metrics data for testing when no instances exist"""
        print("Creating sample metrics data for testing...")
        
        now = datetime.now()
        sample_data = {}
        
        metric_types = [
            'compute.googleapis.com/instance/network/received_bytes_count',
            'compute.googleapis.com/instance/network/sent_bytes_count',
        ]
        
        for metric_type in metric_types:
            values = []
            for i in range(12):  # 12 data points over last hour
                timestamp = now - timedelta(minutes=i*5)
                values.append({
                    'timestamp': timestamp.isoformat(),
                    'value': 1000000 + (i * 50000)  # Sample increasing values
                })
            
            sample_data[metric_type] = values
        
        return sample_data

def main():
    project_id = os.environ.get('GOOGLE_CLOUD_PROJECT')
    if not project_id:
        import subprocess
        try:
            result = subprocess.run(['gcloud', 'config', 'get-value', 'project'], 
                                  capture_output=True, text=True)
            project_id = result.stdout.strip()
        except:
            print("Could not determine project ID")
            return
    
    collector = GCPMetricsCollector(project_id)
    
    try:
        metrics_data = collector.collect_all_instance_metrics()
        
        # Save metrics data
        output_file = 'metrics_data.json'
        with open(output_file, 'w') as f:
            json.dump({
                'collection_timestamp': datetime.now().isoformat(),
                'project_id': project_id,
                'metrics': metrics_data
            }, f, indent=2, default=str)
        
        print(f"\nMetrics data saved to {output_file}")
        
    except Exception as e:
        print(f"Error collecting metrics: {e}")
        print("This is normal if monitoring permissions aren't set up yet.")

if __name__ == "__main__":
    main()