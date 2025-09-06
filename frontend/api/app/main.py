from flask import Flask, jsonify
from flask_cors import CORS
from app.routes.network import network_bp
from app.routes.metrics import metrics_bp
import os
import logging

def create_app():
    app = Flask(__name__)
    CORS(app)  # Enable CORS for frontend
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Register blueprints
    app.register_blueprint(network_bp, url_prefix='/api/network')
    app.register_blueprint(metrics_bp, url_prefix='/api/metrics')
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        return jsonify({'status': 'healthy', 'service': 'network-monitor-api'})
    
    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)