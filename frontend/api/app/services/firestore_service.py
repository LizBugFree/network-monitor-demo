from google.cloud import firestore
from datetime import datetime, timedelta
import logging

class FirestoreService:
    def __init__(self):
        self.db = firestore.Client()
        
    def get_network_resources(self, project_id=None):
        """Get current network resource inventory"""
        try:
            collection_ref = self.db.collection('network_resources')
            
            if project_id:
                docs = collection_ref.where('project_id', '==', project_id).stream()
            else:
                docs = collection_ref.limit(100).stream()
                
            resources = []
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                resources.append(data)
                
            return resources
        except Exception as e:
            logging.error(f"Error fetching network resources: {str(e)}")
            return []
    
    def get_metrics_data(self, resource_type, time_range_hours=24):
        """Get time-series metrics data"""
        try:
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(hours=time_range_hours)
            
            collection_ref = self.db.collection('metrics')
            docs = collection_ref.where('resource_type', '==', resource_type)\
                                .where('timestamp', '>=', start_time)\
                                .where('timestamp', '<=', end_time)\
                                .order_by('timestamp')\
                                .stream()
            
            metrics = []
            for doc in docs:
                data = doc.to_dict()
                # Convert Firestore timestamp to ISO string
                if 'timestamp' in data:
                    data['timestamp'] = data['timestamp'].isoformat()
                metrics.append(data)
                
            return metrics
        except Exception as e:
            logging.error(f"Error fetching metrics: {str(e)}")
            return []
            
    def get_cost_data(self, time_range_days=30):
        """Get cost analytics data"""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=time_range_days)
            
            collection_ref = self.db.collection('costs')
            docs = collection_ref.where('date', '>=', start_date)\
                                .where('date', '<=', end_date)\
                                .order_by('date')\
                                .stream()
            
            costs = []
            for doc in docs:
                data = doc.to_dict()
                if 'date' in data:
                    data['date'] = data['date'].isoformat()
                costs.append(data)
                
            return costs
        except Exception as e:
            logging.error(f"Error fetching cost data: {str(e)}")
            return []