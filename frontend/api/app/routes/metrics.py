from flask import Blueprint, jsonify, request
from app.services.firestore_service import FirestoreService
import logging

metrics_bp = Blueprint('metrics', __name__)
firestore_service = FirestoreService()

@metrics_bp.route('/timeseries', methods=['GET'])
def get_timeseries_metrics():
    """Get time-series metrics for charts"""
    try:
        resource_type = request.args.get('type', 'vpc')
        hours = int(request.args.get('hours', 24))
        
        metrics = firestore_service.get_metrics_data(resource_type, hours)
        
        return jsonify({
            'success': True,
            'data': metrics,
            'count': len(metrics)
        })
        
    except Exception as e:
        logging.error(f"Error in get_timeseries_metrics: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@metrics_bp.route('/summary', methods=['GET'])
def get_metrics_summary():
    """Get aggregated metrics summary"""
    try:
        # Get recent metrics for summary
        vpc_metrics = firestore_service.get_metrics_data('vpc', 1)
        nat_metrics = firestore_service.get_metrics_data('nat_gateway', 1)
        lb_metrics = firestore_service.get_metrics_data('load_balancer', 1)
        
        summary = {
            'total_vpcs': len(set(m.get('resource_id') for m in vpc_metrics)),
            'total_nat_gateways': len(set(m.get('resource_id') for m in nat_metrics)),
            'total_load_balancers': len(set(m.get('resource_id') for m in lb_metrics)),
            'avg_utilization': 0,
            'total_bytes_processed': 0
        }
        
        # Calculate averages
        all_metrics = vpc_metrics + nat_metrics + lb_metrics
        if all_metrics:
            utilizations = [m.get('utilization', 0) for m in all_metrics if m.get('utilization')]
            if utilizations:
                summary['avg_utilization'] = sum(utilizations) / len(utilizations)
            
            bytes_processed = [m.get('bytes_sent', 0) + m.get('bytes_received', 0) for m in all_metrics]
            summary['total_bytes_processed'] = sum(bytes_processed)
        
        return jsonify({
            'success': True,
            'data': summary
        })
        
    except Exception as e:
        logging.error(f"Error in get_metrics_summary: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@metrics_bp.route('/costs', methods=['GET'])
def get_cost_metrics():
    """Get cost analytics data"""
    try:
        days = int(request.args.get('days', 30))
        costs = firestore_service.get_cost_data(days)
        
        return jsonify({
            'success': True,
            'data': costs,
            'count': len(costs)
        })
        
    except Exception as e:
        logging.error(f"Error in get_cost_metrics: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500