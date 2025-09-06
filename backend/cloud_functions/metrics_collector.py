import json
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional
import functions_framework
from google.cloud import monitoring_v3
from google.cloud import firestore
from google.protobuf import duration_pb2
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize clients
db = firestore.Client()

class NetworkMetricsCollector:
    def __init__(self, project_id: str):
        self.project_id = project_id
        self.monitoring_client = monitoring_v3.MetricServiceClient()
        self.project_name = f"projects/{project_id}"
        
    def collect_network_metrics(self, duration_minutes: int = 60) -> Dict[str, Any]:
        """Collect network metrics from Cloud Monitoring"""
        try:
            end_time = datetime.now(timezone.utc)
            start_time = end_time - timedelta(minutes=duration_minutes)
            
            metrics_data = {
                'timestamp': end_time.isoformat(),
                'project_id': self.project_id,
                'collection_period_minutes': duration_minutes,
                'vpc_metrics': self._get_vpc_metrics(start_time, end_time),
                'gce_metrics': self._get_gce_network_metrics(start_time, end_time),
                'nat_metrics': self._get_nat_gateway_metrics(start_time, end_time),
                'firewall_metrics': self._get_firewall_metrics(start_time, end_time),
                'load_balancer_metrics': self._get_load_balancer_metrics(start_time, end_time)
            }
            
            logger.info(f"Collected network metrics for project {self.project_id}")
            return metrics_data
            
        except Exception as e:
            logger.error(f"Error collecting network metrics: {str(e)}")
            raise
    
    def _get_vpc_metrics(self, start_time: datetime, end_time: datetime) -> List[Dict]:
        """Get VPC Flow Logs derived metrics"""
        vpc_metrics = []
        
        metric_types = [
            'compute.googleapis.com/instance/network/sent_bytes_count',
            'compute.googleapis.com/instance/network/received_bytes_count',
            'compute.googleapis.com/instance/network/sent_packets_count',
            'compute.googleapis.com/instance/network/received_packets_count'
        ]
        
        for metric_type in metric_types:
            try:
                metric_data = self._query_time_series(
                    metric_type=metric_type,
                    start_time=start_time,
                    end_time=end_time,
                    aggregation_alignment_period=300,  # 5 minutes
                    aggregation_per_series_aligner=monitoring_v3.Aggregation.Aligner.ALIGN_RATE
                )
                
                if metric_data:
                    vpc_metrics.extend(metric_data)
                    
            except Exception as e:
                logger.warning(f"Failed to collect VPC metric {metric_type}: {str(e)}")
        
        return vpc_metrics
    
    def _get_gce_network_metrics(self, start_time: datetime, end_time: datetime) -> List[Dict]:
        """Get GCE instance network metrics"""
        gce_metrics = []
        
        metric_types = [
            'compute.googleapis.com/instance/network/sent_bytes_count',
            'compute.googleapis.com/instance/network/received_bytes_count'
        ]
        
        for metric_type in metric_types:
            try:
                metric_data = self._query_time_series(
                    metric_type=metric_type,
                    start_time=start_time,
                    end_time=end_time,
                    aggregation_alignment_period=300,
                    aggregation_per_series_aligner=monitoring_v3.Aggregation.Aligner.ALIGN_RATE
                )
                
                if metric_data:
                    gce_metrics.extend(metric_data)
                    
            except Exception as e:
                logger.warning(f"Failed to collect GCE metric {metric_type}: {str(e)}")
        
        return gce_metrics
    
    def _get_nat_gateway_metrics(self, start_time: datetime, end_time: datetime) -> List[Dict]:
        """Get Cloud NAT gateway metrics"""
        nat_metrics = []
        
        metric_types = [
            'compute.googleapis.com/nat/sent_bytes_count',
            'compute.googleapis.com/nat/received_bytes_count',
            'compute.googleapis.com/nat/sent_packets_count',
            'compute.googleapis.com/nat/received_packets_count',
            'compute.googleapis.com/nat/new_connections',
            'compute.googleapis.com/nat/port_usage',
            'compute.googleapis.com/nat/allocated_ports'
        ]
        
        for metric_type in metric_types:
            try:
                metric_data = self._query_time_series(
                    metric_type=metric_type,
                    start_time=start_time,
                    end_time=end_time,
                    aggregation_alignment_period=300,
                    aggregation_per_series_aligner=monitoring_v3.Aggregation.Aligner.ALIGN_MEAN
                )
                
                if metric_data:
                    nat_metrics.extend(metric_data)
                    
            except Exception as e:
                logger.warning(f"Failed to collect NAT metric {metric_type}: {str(e)}")
        
        return nat_metrics
    
    def _get_firewall_metrics(self, start_time: datetime, end_time: datetime) -> List[Dict]:
        """Get firewall-related metrics"""
        firewall_metrics = []
        
        # Note: Firewall hit counts are not directly available as metrics
        # We would need to analyze VPC Flow Logs for this
        # For now, we'll return placeholder for firewall rule usage
        
        return firewall_metrics
    
    def _get_load_balancer_metrics(self, start_time: datetime, end_time: datetime) -> List[Dict]:
        """Get load balancer metrics"""
        lb_metrics = []
        
        metric_types = [
            'loadbalancing.googleapis.com/https/request_count',
            'loadbalancing.googleapis.com/https/request_bytes_count',
            'loadbalancing.googleapis.com/https/response_bytes_count',
            'loadbalancing.googleapis.com/https/backend_latencies'
        ]
        
        for metric_type in metric_types:
            try:
                metric_data = self._query_time_series(
                    metric_type=metric_type,
                    start_time=start_time,
                    end_time=end_time,
                    aggregation_alignment_period=300,
                    aggregation_per_series_aligner=monitoring_v3.Aggregation.Aligner.ALIGN_RATE
                )
                
                if metric_data:
                    lb_metrics.extend(metric_data)
                    
            except Exception as e:
                logger.warning(f"Failed to collect LB metric {metric_type}: {str(e)}")
        
        return lb_metrics
    
    def _query_time_series(
        self, 
        metric_type: str, 
        start_time: datetime, 
        end_time: datetime,
        aggregation_alignment_period: int = 300,
        aggregation_per_series_aligner: monitoring_v3.Aggregation.Aligner = monitoring_v3.Aggregation.Aligner.ALIGN_MEAN
    ) -> List[Dict]:
        """Query time series data from Cloud Monitoring"""
        
        results = []
        
        try:
            # Create time interval
            interval = monitoring_v3.TimeInterval({
                "end_time": {"seconds": int(end_time.timestamp())},
                "start_time": {"seconds": int(start_time.timestamp())}
            })
            
            # Create aggregation
            aggregation = monitoring_v3.Aggregation({
                "alignment_period": duration_pb2.Duration(seconds=aggregation_alignment_period),
                "per_series_aligner": aggregation_per_series_aligner,
            })
            
            # Build the request
            request = monitoring_v3.ListTimeSeriesRequest({
                "name": self.project_name,
                "filter": f'metric.type="{metric_type}"',
                "interval": interval,
                "view": monitoring_v3.ListTimeSeriesRequest.TimeSeriesView.FULL,
                "aggregation": aggregation
            })
            
            # Make the request
            page_result = self.monitoring_client.list_time_series(request=request)
            
            # Process results
            for time_series in page_result:
                resource_labels = dict(time_series.resource.labels)
                metric_labels = dict(time_series.metric.labels)
                
                for point in time_series.points:
                    result = {
                        'metric_type': metric_type,
                        'resource_type': time_series.resource.type,
                        'resource_labels': resource_labels,
                        'metric_labels': metric_labels,
                        'timestamp': point.interval.end_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
                        'value': self._extract_point_value(point),
                        'value_type': str(time_series.value_type),
                        'metric_kind': str(time_series.metric_kind)
                    }
                    results.append(result)
            
        except Exception as e:
            logger.error(f"Error querying time series for {metric_type}: {str(e)}")
            
        return results
    
    def _extract_point_value(self, point) -> Optional[float]:
        """Extract numeric value from monitoring point"""
        try:
            if point.value.HasField('double_value'):
                return point.value.double_value
            elif point.value.HasField('int64_value'):
                return float(point.value.int64_value)
            elif point.value.HasField('bool_value'):
                return float(point.value.bool_value)
        except Exception:
            pass
        return None

def store_metrics_data(data: Dict[str, Any]) -> None:
    """Store metrics data in Firestore"""
    try:
        # Store in metrics collection with timestamp-based document ID
        doc_id = f"{data['project_id']}_{int(datetime.now().timestamp())}"
        
        # Store aggregated metrics summary
        metrics_summary = {
            'timestamp': data['timestamp'],
            'project_id': data['project_id'],
            'collection_period_minutes': data['collection_period_minutes'],
            'metrics_count': {
                'vpc_metrics': len(data.get('vpc_metrics', [])),
                'gce_metrics': len(data.get('gce_metrics', [])),
                'nat_metrics': len(data.get('nat_metrics', [])),
                'firewall_metrics': len(data.get('firewall_metrics', [])),
                'load_balancer_metrics': len(data.get('load_balancer_metrics', []))
            }
        }
        
        db.collection('metrics-summaries').document(doc_id).set(metrics_summary)
        
        # Store individual metrics for detailed analysis
        all_metrics = (
            data.get('vpc_metrics', []) +
            data.get('gce_metrics', []) +
            data.get('nat_metrics', []) +
            data.get('load_balancer_metrics', [])
        )
        
        # Batch write metrics (Firestore has a limit of 500 operations per batch)
        batch_size = 450
        for i in range(0, len(all_metrics), batch_size):
            batch = db.batch()
            batch_metrics = all_metrics[i:i + batch_size]
            
            for metric in batch_metrics:
                # Add collection metadata
                metric['collection_timestamp'] = data['timestamp']
                metric['project_id'] = data['project_id']
                
                # Create document reference and add to batch
                doc_ref = db.collection('network-metrics').document()
                batch.set(doc_ref, metric)
            
            # Commit the batch
            batch.commit()
        
        logger.info(f"Successfully stored {len(all_metrics)} metrics for {data['project_id']}")
        
    except Exception as e:
        logger.error(f"Error storing metrics data: {str(e)}")
        raise

@functions_framework.http
def collect_network_metrics(request):
    """HTTP Cloud Function entry point for metrics collection"""
    try:
        # Get project ID from environment
        project_id = os.environ.get('GCP_PROJECT') or os.environ.get('GOOGLE_CLOUD_PROJECT')
        if not project_id:
            return {'error': 'Project ID not found'}, 400
        
        # Get duration from request parameters (default 60 minutes)
        duration_minutes = 60
        if request.args.get('duration'):
            try:
                duration_minutes = int(request.args.get('duration'))
                duration_minutes = min(max(duration_minutes, 5), 1440)  # Limit between 5 minutes and 24 hours
            except ValueError:
                duration_minutes = 60
        
        # Initialize collector
        collector = NetworkMetricsCollector(project_id)
        
        # Collect metrics
        metrics_data = collector.collect_network_metrics(duration_minutes)
        
        # Store in Firestore
        store_metrics_data(metrics_data)
        
        # Return success response
        total_metrics = sum([
            len(metrics_data.get('vpc_metrics', [])),
            len(metrics_data.get('gce_metrics', [])),
            len(metrics_data.get('nat_metrics', [])),
            len(metrics_data.get('firewall_metrics', [])),
            len(metrics_data.get('load_balancer_metrics', []))
        ])
        
        response = {
            'status': 'success',
            'timestamp': metrics_data['timestamp'],
            'duration_minutes': duration_minutes,
            'total_metrics_collected': total_metrics,
            'metrics_breakdown': {
                'vpc_metrics': len(metrics_data.get('vpc_metrics', [])),
                'gce_metrics': len(metrics_data.get('gce_metrics', [])),
                'nat_metrics': len(metrics_data.get('nat_metrics', [])),
                'firewall_metrics': len(metrics_data.get('firewall_metrics', [])),
                'load_balancer_metrics': len(metrics_data.get('load_balancer_metrics', []))
            }
        }
        
        logger.info(f"Metrics collection completed: {response}")
        return response, 200
        
    except Exception as e:
        logger.error(f"Metrics collection failed: {str(e)}")
        return {'error': str(e), 'status': 'failed'}, 500

# For local testing
if __name__ == '__main__':
    import os
    os.environ['GOOGLE_CLOUD_PROJECT'] = 'your-project-id'
    
    # Test the function
    class MockRequest:
        def __init__(self):
            self.args = {}
    
    result = collect_network_metrics(MockRequest())
    print(json.dumps(result, indent=2))