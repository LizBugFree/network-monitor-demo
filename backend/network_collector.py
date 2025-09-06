from google.cloud import compute_v1
import json
from datetime import datetime
import os

class GCPNetworkCollector:
    def __init__(self, project_id):
        self.project_id = project_id
        self.compute_client = compute_v1.InstancesClient()
        self.networks_client = compute_v1.NetworksClient()
        self.subnetworks_client = compute_v1.SubnetworksClient()
        self.firewalls_client = compute_v1.FirewallsClient()
        self.routers_client = compute_v1.RoutersClient()
    
    def collect_networks(self):
        """Collect VPC network information"""
        print("Collecting VPC networks...")
        networks = []
        
        try:
            request = compute_v1.ListNetworksRequest(project=self.project_id)
            network_list = self.networks_client.list(request=request)
            
            for network in network_list:
                networks.append({
                    'name': network.name,
                    'id': network.id,
                    'self_link': network.self_link,
                    'auto_create_subnetworks': network.auto_create_subnetworks,
                    'routing_mode': network.routing_config.routing_mode if network.routing_config else 'REGIONAL',
                    'creation_timestamp': network.creation_timestamp
                })
                
            print(f"Found {len(networks)} VPC networks")
            return networks
            
        except Exception as e:
            print(f"Error collecting networks: {e}")
            return []
    
    def collect_subnets(self):
        """Collect subnet information"""
        print("Collecting subnets...")
        subnets = []
        
        try:
            # List subnets across all regions
            regions = ['us-central1', 'us-east1', 'us-west1', 'europe-west1']
            
            for region in regions:
                try:
                    request = compute_v1.ListSubnetworksRequest(
                        project=self.project_id,
                        region=region
                    )
                    subnet_list = self.subnetworks_client.list(request=request)
                    
                    for subnet in subnet_list:
                        subnets.append({
                            'name': subnet.name,
                            'region': region,
                            'network': subnet.network.split('/')[-1],
                            'ip_cidr_range': subnet.ip_cidr_range,
                            'gateway_address': subnet.gateway_address,
                            'private_ip_google_access': subnet.private_ip_google_access,
                            'creation_timestamp': subnet.creation_timestamp
                        })
                except Exception as e:
                    # Region might not have subnets, that's okay
                    continue
                    
            print(f"Found {len(subnets)} subnets")
            return subnets
            
        except Exception as e:
            print(f"Error collecting subnets: {e}")
            return []
    
    def collect_firewall_rules(self):
        """Collect firewall rules"""
        print("Collecting firewall rules...")
        firewalls = []
        
        try:
            request = compute_v1.ListFirewallsRequest(project=self.project_id)
            firewall_list = self.firewalls_client.list(request=request)
            
            for firewall in firewall_list:
                firewalls.append({
                    'name': firewall.name,
                    'direction': firewall.direction,
                    'priority': firewall.priority,
                    'network': firewall.network.split('/')[-1] if firewall.network else 'default',
                    'source_ranges': list(firewall.source_ranges) if firewall.source_ranges else [],
                    'target_tags': list(firewall.target_tags) if firewall.target_tags else [],
                    'allowed': [{'protocol': rule.I_p_protocol, 'ports': list(rule.ports) if rule.ports else []} 
                              for rule in firewall.allowed] if firewall.allowed else [],
                    'creation_timestamp': firewall.creation_timestamp
                })
                
            print(f"Found {len(firewalls)} firewall rules")
            return firewalls
            
        except Exception as e:
            print(f"Error collecting firewall rules: {e}")
            return []
    
    def collect_instances(self):
        """Collect VM instances"""
        print("Collecting VM instances...")
        instances = []
        
        try:
            request = compute_v1.AggregatedListInstancesRequest(project=self.project_id)
            instance_list = self.compute_client.aggregated_list(request=request)
            
            for zone, response in instance_list:
                if hasattr(response, 'instances') and response.instances:
                    for instance in response.instances:
                        instances.append({
                            'name': instance.name,
                            'zone': zone.split('/')[-1],
                            'machine_type': instance.machine_type.split('/')[-1],
                            'status': instance.status,
                            'internal_ip': instance.network_interfaces[0].network_i_p if instance.network_interfaces else None,
                            'external_ip': instance.network_interfaces[0].access_configs[0].nat_i_p 
                                         if instance.network_interfaces and instance.network_interfaces[0].access_configs 
                                         else None,
                            'network': instance.network_interfaces[0].network.split('/')[-1] 
                                     if instance.network_interfaces else None,
                            'subnet': instance.network_interfaces[0].subnetwork.split('/')[-1] 
                                    if instance.network_interfaces else None,
                            'creation_timestamp': instance.creation_timestamp
                        })
                        
            print(f"Found {len(instances)} VM instances")
            return instances
            
        except Exception as e:
            print(f"Error collecting instances: {e}")
            return []
    
    def collect_all_data(self):
        """Collect all network data"""
        print(f"Starting data collection for project: {self.project_id}")
        print("=" * 60)
        
        data = {
            'collection_timestamp': datetime.now().isoformat(),
            'project_id': self.project_id,
            'networks': self.collect_networks(),
            'subnets': self.collect_subnets(),
            'firewall_rules': self.collect_firewall_rules(),
            'instances': self.collect_instances()
        }
        
        print("=" * 60)
        print(f"Collection complete! Summary:")
        print(f"  - Networks: {len(data['networks'])}")
        print(f"  - Subnets: {len(data['subnets'])}")
        print(f"  - Firewall Rules: {len(data['firewall_rules'])}")
        print(f"  - VM Instances: {len(data['instances'])}")
        
        return data

def main():
    # Get project ID from environment or gcloud config
    project_id = os.environ.get('GOOGLE_CLOUD_PROJECT')
    if not project_id:
        import subprocess
        try:
            result = subprocess.run(['gcloud', 'config', 'get-value', 'project'], 
                                  capture_output=True, text=True)
            project_id = result.stdout.strip()
        except:
            print("Could not determine project ID. Please set GOOGLE_CLOUD_PROJECT environment variable.")
            return
    
    collector = GCPNetworkCollector(project_id)
    data = collector.collect_all_data()
    
    # Save to JSON file
    output_file = 'network_data.json'
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2, default=str)
    
    print(f"\nData saved to {output_file}")

if __name__ == "__main__":
    main()