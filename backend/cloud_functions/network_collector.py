import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Any
import functions_framework
from google.cloud import compute_v1
from google.cloud import monitoring_v3
from google.cloud import firestore
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Firestore client
db = firestore.Client()

class NetworkDataCollector:
    def __init__(self, project_id: str):
        self.project_id = project_id
        self.compute_client = compute_v1.InstancesClient()
        self.networks_client = compute_v1.NetworksClient()
        self.subnetworks_client = compute_v1.SubnetworksClient()
        self.routers_client = compute_v1.RoutersClient()
        self.firewalls_client = compute_v1.FirewallsClient()
        self.nat_gateways_client = compute_v1.RoutersClient()
        self.monitoring_client = monitoring_v3.MetricServiceClient()
        
    def collect_network_resources(self) -> Dict[str, Any]:
        """Collect all network resource information"""
        try:
            data = {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'project_id': self.project_id,
                'networks': self._get_networks(),
                'subnetworks': self._get_subnetworks(),
                'firewall_rules': self._get_firewall_rules(),
                'routers': self._get_routers(),
                'nat_gateways': self._get_nat_gateways()
            }
            logger.info(f"Collected network resources for project {self.project_id}")
            return data
        except Exception as e:
            logger.error(f"Error collecting network resources: {str(e)}")
            raise
    
    def _get_networks(self) -> List[Dict]:
        """Get all VPC networks in the project"""
        networks = []
        try:
            request = compute_v1.ListNetworksRequest(project=self.project_id)
            page_result = self.networks_client.list(request=request)
            
            for network in page_result:
                networks.append({
                    'name': network.name,
                    'id': str(network.id),
                    'description': getattr(network, 'description', ''),
                    'auto_create_subnetworks': network.auto_create_subnetworks,
                    'routing_mode': network.routing_config.routing_mode if network.routing_config else 'REGIONAL',
                    'creation_timestamp': network.creation_timestamp,
                    'self_link': network.self_link,
                    'subnet_count': len(network.subnetworks) if hasattr(network, 'subnetworks') else 0
                })
        except Exception as e:
            logger.error(f"Error fetching networks: {str(e)}")
            
        return networks
    
    def _get_subnetworks(self) -> List[Dict]:
        """Get all subnetworks across all regions"""
        subnetworks = []
        try:
            # Get all regions first
            regions_client = compute_v1.RegionsClient()
            regions_request = compute_v1.ListRegionsRequest(project=self.project_id)
            regions = regions_client.list(request=regions_request)
            
            for region in regions:
                request = compute_v1.ListSubnetworksRequest(
                    project=self.project_id, 
                    region=region.name
                )
                page_result = self.subnetworks_client.list(request=request)
                
                for subnet in page_result:
                    subnetworks.append({
                        'name': subnet.name,
                        'id': str(subnet.id),
                        'region': region.name,
                        'network': subnet.network.split('/')[-1] if subnet.network else '',
                        'ip_cidr_range': subnet.ip_cidr_range,
                        'gateway_address': subnet.gateway_address,
                        'private_ip_google_access': subnet.private_ip_google_access,
                        'purpose': getattr(subnet, 'purpose', 'PRIVATE_RFC_1918'),
                        'creation_timestamp': subnet.creation_timestamp,
                        'available_ips': self._calculate_available_ips(subnet.ip_cidr_range)
                    })
        except Exception as e:
            logger.error(f"Error fetching subnetworks: {str(e)}")
            
        return subnetworks
    
    def _get_firewall_rules(self) -> List[Dict]:
        """Get all firewall rules"""
        firewall_rules = []
        try:
            request = compute_v1.ListFirewallsRequest(project=self.project_id)
            page_result = self.firewalls_client.list(request=request)
            
            for firewall in page_result:
                firewall_rules.append({
                    'name': firewall.name,
                    'id': str(firewall.id),
                    'description': getattr(firewall, 'description', ''),
                    'network': firewall.network.split('/')[-1] if firewall.network else '',
                    'direction': firewall.direction,
                    'priority': firewall.priority,
                    'source_ranges': list(firewall.source_ranges) if firewall.source_ranges else [],
                    'target_tags': list(firewall.target_tags) if firewall.target_tags else [],
                    'allowed_ports': self._format_firewall_allowed(firewall.allowed) if firewall.allowed else [],
                    'denied_ports': self._format_firewall_denied(firewall.denied) if firewall.denied else [],
                    'creation_timestamp': firewall.creation_timestamp,
                    'disabled': getattr(firewall, 'disabled', False)
                })
        except Exception as e:
            logger.error(f"Error fetching firewall rules: {str(e)}")
            
        return firewall_rules
    
    def _get_routers(self) -> List[Dict]:
        """Get all Cloud Routers"""
        routers = []
        try:
            # Get all regions
            regions_client = compute_v1.RegionsClient()
            regions_request = compute_v1.ListRegionsRequest(project=self.project_id)
            regions = regions_client.list(request=regions_request)
            
            for region in regions:
                request = compute_v1.ListRoutersRequest(
                    project=self.project_id,
                    region=region.name
                )
                page_result = self.routers_client.list(request=request)
                
                for router in page_result:
                    routers.append({
                        'name': router.name,
                        'id': str(router.id),
                        'region': region.name,
                        'network': router.network.split('/')[-1] if router.network else '',
                        'description': getattr(router, 'description', ''),
                        'bgp_asn': router.bgp.asn if router.bgp else None,
                        'bgp_advertise_mode': router.bgp.advertise_mode if router.bgp else None,
                        'nat_count': len(router.nats) if router.nats else 0,
                        'creation_timestamp': router.creation_timestamp
                    })
        except Exception as e:
            logger.error(f"Error fetching routers: {str(e)}")
            
        return routers
    
    def _get_nat_gateways(self) -> List[Dict]:
        """Get all Cloud NAT gateways"""
        nat_gateways = []
        try:
            # Get all regions
            regions_client = compute_v1.RegionsClient()
            regions_request = compute_v1.ListRegionsRequest(project=self.project_id)
            regions = regions_client.list(request=regions_request)
            
            for region in regions:
                request = compute_v1.ListRoutersRequest(
                    project=self.project_id,
                    region=region.name
                )
                routers = self.routers_client.list(request=request)
                
                for router in routers:
                    if router.nats:
                        for nat in router.nats:
                            nat_gateways.append({
                                'name': nat.name,
                                'router_name': router.name,
                                'region': region.name,
                                'nat_ip_allocate_option': nat.nat_ip_allocate_option,
                                'source_subnetwork_ip_ranges_to_nat': nat.source_subnetwork_ip_ranges_to_nat,
                                'min_ports_per_vm': getattr(nat, 'min_ports_per_vm', 0),
                                'max_ports_per_vm': getattr(nat, 'max_ports_per_vm', 0),
                                'enable_endpoint_independent_mapping': getattr(nat, 'enable_endpoint_independent_mapping', False),
                                'log_config_enabled': nat.log_config.enable if nat.log_config else False
                            })
        except Exception as e:
            logger.error(f"Error fetching NAT gateways: {str(e)}")
            
        return nat_gateways
    
    def _format_firewall_allowed(self, allowed_rules) -> List[Dict]:
        """Format firewall allowed rules"""
        formatted = []
        for rule in allowed_rules:
            formatted.append({
                'protocol': rule.I_p_protocol,
                'ports': list(rule.ports) if rule.ports else []
            })
        return formatted
    
    def _format_firewall_denied(self, denied_rules) -> List[Dict]:
        """Format firewall denied rules"""
        formatted = []
        for rule in denied_rules:
            formatted.append({
                'protocol': rule.I_p_protocol,
                'ports': list(rule.ports) if rule.ports else []
            })
        return formatted
    
    def _calculate_available_ips(self, cidr_range: str) -> int:
        """Calculate available IP addresses in a CIDR range"""
        try:
            import ipaddress
            network = ipaddress.IPv4Network(cidr_range, strict=False)
            # Subtract network, broadcast, and gateway addresses
            return network.num_addresses - 3
        except Exception:
            return 0

def store_network_data(data: Dict[str, Any]) -> None:
    """Store network data in Firestore"""
    try:
        # Store in network-inventory collection with timestamp-based document ID
        doc_id = f"{data['project_id']}_{int(datetime.now().timestamp())}"
        
        # Store main inventory
        db.collection('network-inventory').document(doc_id).set(data)
        
        # Store individual resource types for easier querying
        timestamp = data['timestamp']
        project_id = data['project_id']
        
        # Networks
        for network in data.get('networks', []):
            network['timestamp'] = timestamp
            network['project_id'] = project_id
            db.collection('networks').add(network)
        
        # Subnetworks  
        for subnet in data.get('subnetworks', []):
            subnet['timestamp'] = timestamp
            subnet['project_id'] = project_id
            db.collection('subnetworks').add(subnet)
            
        # Firewall rules
        for firewall in data.get('firewall_rules', []):
            firewall['timestamp'] = timestamp
            firewall['project_id'] = project_id
            db.collection('firewall-rules').add(firewall)
            
        logger.info(f"Successfully stored network data for {project_id}")
        
    except Exception as e:
        logger.error(f"Error storing network data: {str(e)}")
        raise

@functions_framework.http
def collect_network_data(request):
    """HTTP Cloud Function entry point"""
    try:
        # Get project ID from environment or request
        project_id = os.environ.get('GCP_PROJECT') or os.environ.get('GOOGLE_CLOUD_PROJECT')
        if not project_id:
            return {'error': 'Project ID not found'}, 400
        
        # Initialize collector
        collector = NetworkDataCollector(project_id)
        
        # Collect data
        network_data = collector.collect_network_resources()
        
        # Store in Firestore
        store_network_data(network_data)
        
        # Return success response
        response = {
            'status': 'success',
            'timestamp': network_data['timestamp'],
            'resources_collected': {
                'networks': len(network_data.get('networks', [])),
                'subnetworks': len(network_data.get('subnetworks', [])),
                'firewall_rules': len(network_data.get('firewall_rules', [])),
                'routers': len(network_data.get('routers', [])),
                'nat_gateways': len(network_data.get('nat_gateways', []))
            }
        }
        
        logger.info(f"Network data collection completed: {response}")
        return response, 200
        
    except Exception as e:
        logger.error(f"Network data collection failed: {str(e)}")
        return {'error': str(e), 'status': 'failed'}, 500

# For local testing
if __name__ == '__main__':
    import os
    os.environ['GOOGLE_CLOUD_PROJECT'] = 'your-project-id'
    
    # Test the function
    class MockRequest:
        pass
    
    result = collect_network_data(MockRequest())
    print(json.dumps(result, indent=2))