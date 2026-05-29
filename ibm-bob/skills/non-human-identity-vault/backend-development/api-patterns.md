# Flask API Patterns Reference

## Basic Flask Setup

```python
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

app.config['JSON_SORT_KEYS'] = False
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
```

## RESTful Endpoint Patterns

```python
# Health check
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'})

# List resources
@app.route('/api/resources', methods=['GET'])
def list_resources():
    return jsonify({'resources': []})

# Create resource
@app.route('/api/resources', methods=['POST'])
def create_resource():
    data = request.get_json()
    # Process data
    return jsonify({'id': 1, 'data': data}), 201

# Get resource
@app.route('/api/resources/<int:id>', methods=['GET'])
def get_resource(id):
    return jsonify({'id': id})

# Update resource
@app.route('/api/resources/<int:id>', methods=['PUT'])
def update_resource(id):
    data = request.get_json()
    return jsonify({'id': id, 'data': data})

# Delete resource
@app.route('/api/resources/<int:id>', methods=['DELETE'])
def delete_resource(id):
    return '', 204
```

## Error Handling Pattern

```python
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/endpoint', methods=['POST'])
def endpoint():
    try:
        data = request.get_json()
        
        # Validate input
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Process request
        result = process_data(data)
        return jsonify({'success': True, 'data': result})
        
    except ValueError as e:
        return jsonify({'error': f'Invalid input: {str(e)}'}), 400
    except Exception as e:
        app.logger.error(f'Error: {str(e)}')
        return jsonify({'error': 'Internal server error'}), 500
```

## Vault Client Pattern

```python
import hvac

class VaultClient:
    def __init__(self, vault_addr, vault_token):
        self.client = hvac.Client(url=vault_addr, token=vault_token)
    
    def get_status(self):
        try:
            health = self.client.sys.read_health_status()
            return {
                'connected': True,
                'sealed': health.get('sealed', True),
                'version': health.get('version', 'unknown')
            }
        except Exception as e:
            return {'connected': False, 'error': str(e)}
    
    def encrypt(self, plaintext, key_name='transit-key'):
        response = self.client.secrets.transit.encrypt_data(
            name=key_name,
            plaintext=plaintext
        )
        return response['data']['ciphertext']
    
    def store_secret(self, path, secret_data):
        self.client.secrets.kv.v2.create_or_update_secret(
            path=path,
            secret=secret_data
        )
```

## Secret Scanning Pattern

```python
import re

SECRET_PATTERNS = {
    'aws_access_key': {
        'pattern': r'AKIA[0-9A-Z]{16}',
        'severity': 'critical'
    },
    'github_token': {
        'pattern': r'ghp_[a-zA-Z0-9]{36}',
        'severity': 'high'
    }
}

def scan_code(code):
    findings = []
    lines = code.split('\n')
    
    for line_num, line in enumerate(lines, 1):
        for secret_type, config in SECRET_PATTERNS.items():
            matches = re.finditer(config['pattern'], line, re.IGNORECASE)
            for match in matches:
                findings.append({
                    'type': secret_type,
                    'severity': config['severity'],
                    'line': line_num,
                    'match': match.group(0)
                })
    
    return {'total': len(findings), 'findings': findings}
```

## Input Validation Pattern

```python
def validate_input(data, required_fields):
    missing = [f for f in required_fields if f not in data]
    if missing:
        raise ValueError(f"Missing required fields: {', '.join(missing)}")
    return True

@app.route('/api/scan', methods=['POST'])
def scan():
    data = request.get_json()
    validate_input(data, ['code'])
    results = scan_code(data['code'])
    return jsonify(results)
```

## Logging Pattern

```python
import logging
from logging.handlers import RotatingFileHandler

# Setup logging
file_handler = RotatingFileHandler('app.log', maxBytes=10240000, backupCount=10)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))
file_handler.setLevel(logging.INFO)
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)

# Usage
app.logger.info('Processing request')
app.logger.error('Operation failed')
```

## Response Format

```python
# Success
{
    "status": "success",
    "data": {...},
    "message": "Operation completed"
}

# Error
{
    "status": "error",
    "error": "Error message",
    "details": {...}
}
```

## Testing Pattern

```python
import unittest

class APITestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
    
    def test_health_check(self):
        response = self.app.get('/api/health')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['status'], 'healthy')