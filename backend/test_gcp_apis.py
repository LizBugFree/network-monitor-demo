from google.cloud import compute_v1
from google.cloud import monitoring_v3
import os
import google.auth

def check_authentication():
    """Check if we're properly authenticated"""
    try:
        credentials, project = google.auth.default()
        print(f"✅ Authentication working, project: {project}")
        return project
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        print("\nTry running:")
        print("  gcloud auth application-default login")
        print("  gcloud config set project your-project-id")
        return None

def test_compute_api(project):
    """Test basic Compute Engine API access"""
    try:
        client = compute_v1.InstancesClient()
        # Just try to create the client and make a simple call
        request = compute_v1.AggregatedListInstancesRequest(project=project)
        instances = client.aggregated_list(request=request)
        print("✅ Compute Engine API working")
        
        # Count instances
        instance_count = 0
        for zone, response in instances:
            if response.instances:
                instance_count += len(response.instances)
        print(f"   Found {instance_count} VM instances")
        return True
    except Exception as e:
        print(f"❌ Compute Engine API error: {e}")
        return False

def test_monitoring_api(project):
    """Test Cloud Monitoring API access"""
    try:
        client = monitoring_v3.MetricServiceClient()
        project_name = f"projects/{project}"
        
        # List first few metrics to test connectivity
        request = monitoring_v3.ListMetricDescriptorsRequest(
            name=project_name,
            page_size=5
        )
        metrics = client.list_metric_descriptors(request=request)
        
        print("✅ Cloud Monitoring API working")
        metric_count = len(list(metrics))
        print(f"   Found {metric_count} metric types available")
        return True
    except Exception as e:
        print(f"❌ Cloud Monitoring API error: {e}")
        return False

if __name__ == "__main__":
    print("Testing GCP API connectivity...\n")
    
    # First check authentication
    project = check_authentication()
    if not project:
        exit(1)
    
    # Set environment variable for other parts of the script
    os.environ['GOOGLE_CLOUD_PROJECT'] = project
    
    print(f"\nTesting APIs for project: {project}")
    print("-" * 50)
    
    test_compute_api(project)
    test_monitoring_api(project)
    
    print("\nIf both APIs are working, you're ready for Day 2! 🎉")

