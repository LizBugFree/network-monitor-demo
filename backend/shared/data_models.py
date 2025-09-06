from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime

@dataclass
class NetworkResource:
    name: str
    resource_type: str
    project_id: str
    region: Optional[str] = None
    zone: Optional[str] = None
    creation_timestamp: Optional[str] = None
    metadata: Optional[Dict] = None

@dataclass  
class NetworkMetric:
    resource_name: str
    metric_type: str
    timestamp: datetime
    value: float
    unit: str
    labels: Optional[Dict[str, str]] = None

@dataclass
class NetworkSummary:
    project_id: str
    collection_timestamp: datetime
    total_networks: int
    total_subnets: int
    total_instances: int
    total_firewall_rules: int
    
class DataProcessor:
    """Process and aggregate network data"""
    
    def __init__(self, raw_data: Dict):
        self.raw_data = raw_data
        
    def get_network_summary(self) -> NetworkSummary:
        """Create a summary of network resources"""
        return NetworkSummary(
            project_id=self.raw_data.get('project_id', ''),
            collection_timestamp=datetime.fromisoformat(self.raw_data.get('collection_timestamp', datetime.now().isoformat())),
            total_networks=len(self.raw_data.get('networks', [])),
            total_subnets=len(self.raw_data.get('subnets', [])),
            total_instances=len(self.raw_data.get('instances', [])),
            total_firewall_rules=len(self.raw_data.get('firewall_rules', []))
        )
    
    def get_security_insights(self) -> List[str]:
        """Generate security insights from firewall rules"""
        insights = []
        
        firewall_rules = self.raw_data.get('firewall_rules', [])
        
        for rule in firewall_rules:
            # Check for overly permissive rules
            source_ranges = rule.get('source_ranges', [])
            if '0.0.0.0/0' in source_ranges:
                allowed = rule.get('allowed', [])
                for allow in allowed:
                    if allow.get('protocol') == 'tcp' and ('22' in allow.get('ports', []) or not allow.get('ports')):
                        insights.append(f"⚠️  Firewall rule '{rule['name']}' allows SSH from anywhere (0.0.0.0/0)")
        
        return insights
    
    def get_cost_insights(self) -> List[str]:
        """Generate cost optimization insights"""
        insights = []
        
        instances = self.raw_data.get('instances', [])
        
        # Check for instances with external IPs
        external_ip_count = sum(1 for instance in instances if instance.get('external_ip'))
        if external_ip_count > 0:
            insights.append(f"💰 {external_ip_count} instances have external IPs - consider Cloud NAT for cost savings")
        
        # Check for instances in expensive zones (this is just an example)
        premium_zones = [instance for instance in instances if 'us-west' in instance.get('zone', '')]
        if premium_zones:
            insights.append(f"💰 {len(premium_zones)} instances in potentially more expensive regions")
        
        return insights