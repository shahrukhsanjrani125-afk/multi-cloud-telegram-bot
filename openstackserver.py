from flask import Flask, request, jsonify
from flask_restx import Api, Resource, fields
import os
import json
import logging
from datetime import datetime

app = Flask(__name__)
api = Api(app, version='1.0', title='OpenStack Swift API',
          description='Headless OpenStack Swift Compatible API')

ns = api.namespace('v1/AUTH_shark', description='Swift operations')

# In-memory storage (replace with database in production)
storage = {}

object_model = api.model('Object', {
    'name': fields.String(required=True),
    'content': fields.String,
    'content_type': fields.String
})

@ns.route('/<container>/<object_name>')
class SwiftObject(Resource):
    def put(self, container, object_name):
        """Store object in container"""
        try:
            if container not in storage:
                storage[container] = {}
            
            data = {
                'content': request.get_data(),
                'content_type': request.headers.get('Content-Type', 'application/octet-stream'),
                'timestamp': datetime.utcnow().isoformat(),
                'size': len(request.get_data())
            }
            
            storage[container][object_name] = data
            
            # Log to file
            log_entry = {
                'timestamp': datetime.utcnow().isoformat(),
                'operation': 'PUT',
                'container': container,
                'object': object_name,
                'size': data['size']
            }
            
            with open('logs/openstack_operations.log', 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
            
            return {'status': 'created', 'object': object_name}, 201
            
        except Exception as e:
            return {'error': str(e)}, 500
    
    def get(self, container, object_name):
        """Retrieve object from container"""
        if container in storage and object_name in storage[container]:
            data = storage[container][object_name]
            return data['content'], 200, {'Content-Type': data['content_type']}
        return {'error': 'Not found'}, 404

@ns.route('/<container>')
class SwiftContainer(Resource):
    def get(self, container):
        """List objects in container"""
        if container in storage:
            return {'objects': list(storage[container].keys())}, 200
        return {'error': 'Container not found'}, 404

if __name__ == '__main__':
    # Create logs directory
    os.makedirs('logs', exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/openstack_server.log'),
            logging.StreamHandler()
        ]
    )
    
    app.run(host='127.0.0.1', port=8080, debug=True)