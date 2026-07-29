# watsonx Orchestrate Integration Code Examples

This folder contains ready-to-use code examples for integrating with watsonx Orchestrate agents.

## Files

### Python Examples

- **`watsonx_client.py`** - Complete Python client library
  - Supports IBM Cloud, AWS, and On-premises
  - Automatic platform detection
  - Token management (IAM and JWT)
  - Full API coverage (list agents, invoke, polling, chat completions)
  - Easy-to-use wrapper functions

- **`chat_cli.py`** - Interactive CLI chat application
  - Menu-driven interface
  - Platform auto-detection
  - List agents, invoke agents, interactive sessions
  - Streaming support

- **`test_connection.py`** - Connection test script
  - Validates credentials
  - Tests authentication
  - Verifies API connectivity
  - Platform detection

### Node.js Examples

- **`server.js`** - Express REST API server
  - Multi-platform support
  - REST endpoints for agent operations
  - Automatic token management
  - Ready for web/mobile integration

- **`package.json`** - Node.js dependencies

## Setup

### Python Setup

1. Create `.env` file:
```bash
WATSONX_API_KEY=your-api-key
WATSONX_SERVICE_URL=https://api.us-south.watson-orchestrate.cloud.ibm.com/instances/your-instance-id
```

2. Run examples:
```bash
# Test connection
python test_connection.py

# Interactive CLI
python chat_cli.py

# Use client library
python watsonx_client.py
```

### Node.js Setup

1. Install dependencies:
```bash
npm install
```

2. Create `.env` file (same as Python)

3. Run server:
```bash
npm start
```

## Platform Support

All examples automatically detect and support:
- **IBM Cloud** - IAM token authentication
- **AWS** - JWT token authentication  
- **On-premises** - JWT token authentication

## Usage Examples

See the parent folder's `code-examples.md` for detailed usage patterns and integration workflows.