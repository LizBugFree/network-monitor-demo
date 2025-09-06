from flask import Blueprint, jsonify, request
from app.services.firestore_service import FirestoreService
import logging

network_bp = Blueprint('network', __name__)
firestore_service = FirestoreService()

@network_bp.route('/topology', methods=['GET'])
def get_network_topology():
    """Get network topology data for visualization"""
    try:
        project_id = request.args.get('project_id')
        resources = firestore_service.get_network_resources(project_id)
        
        # Transform data for topology visualization
        topology = {
            'vpcs': [],
            'subnets': [],
            'nat_gateways': [],
            'load_balancers': [],
            'connections': []
        }
        
        for resource in resources:
            resource_type = resource.get('resource_type', '').lower()
            
            if 'vpc' in resource_type:
                topology['vpcs'].append({
                    'id': resource['id'],
                    'name': resource.get('name', ''),
                    'region': resource.get('region', ''),
                    'cidr_block': resource.get('cidr_block', ''),
                    'status': resource.get('status', 'unknown')
                })
            elif 'subnet' in resource_type:
                topology['subnets'].append({
                    'id': resource['id'],
                    'name': resource.get('name', ''),
                    'vpc_id': resource.get('vpc_id', ''),
                    'cidr_block': resource.get('cidr_block', ''),
                    'zone': resource.get('zone', '')
                })
            elif 'nat' in resource_type:
                topology['nat_gateways'].append({
                    'id': resource['id'],
                    'name': resource.get('name', ''),
                    'subnet_id': resource.get('subnet_id', ''),
                    'status': resource.get('status', 'unknown')
                })
            elif 'load_balancer' in resource_type or 'lb' in resource_type:
                topology['load_balancers'].append({
                    'id': resource['id'],
                    'name': resource.get('name', ''),
                    'type': resource.get('lb_type', 'unknown'),
                    'status': resource.get('status', 'unknown')
                })
        
        return jsonify({
            'success': True,
            'data': topology,
            'timestamp': firestore_service.db.collection('_').document().create_time
        })
        
    except Exception as e:
        logging.error(f"Error in get_network_topology: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@network_bp.route('/resources', methods=['GET'])
def get_network_resources():
    """Get paginated list of network resources"""
    try:
        project_id = request.args.get('project_id')
        resource_type = request.args.get('type')
        
        resources = firestore_service.get_network_resources(project_id)
        
        if resource_type:
            resources = [r for r in resources if resource_type.lower() in r.get('resource_type', '').lower()]
        
        return jsonify({
            'success': True,
            'data': resources,
            'count': len(resources)
        })
        
    except Exception as e:
        logging.error(f"Error in get_network_resources: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500