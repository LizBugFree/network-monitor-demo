import json
import logging
from datetime import datetime
import functions_framework
from network_collector import collect_network_data
from metrics_collector import collect_network_metrics

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@functions_framework.http 
def network_data_collector(request):
    """Network resource data collection function"""
    return collect_network_data(request)

@functions_framework.http
def network_metrics_collector(request):
    """Network metrics collection function"""
    return collect_network_metrics(request)