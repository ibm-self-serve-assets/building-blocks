# MCP Builder Mode - User Guide

## Overview

The **MCP Builder** mode is an expert-level custom mode for IBM Bob designed specifically for building production-grade Model Context Protocol (MCP) servers in Python and TypeScript/Node.js. This mode provides comprehensive guidance, best practices, and patterns for MCP server development.

## Target Audience

This mode is designed for expert developers who:
- Understand the Model Context Protocol specification
- Have experience with Python 3.10+ or Node.js 18+
- Are comfortable with async programming patterns
- Need to build production-ready MCP servers
- Want to integrate MCP servers with AI platforms

## Prerequisites

Before using this mode, ensure you have:

1. **Python 3.10+ or Node.js 18+ installed**
   ```bash
   # Python
   python --version  # Should be 3.10 or higher
   
   # Node.js
   node --version    # Should be 18 or higher
   ```

2. **MCP SDK installed**
   ```bash
   # Python
   pip install mcp
   
   # Node.js
   npm install @modelcontextprotocol/sdk
   ```

3. **Understanding of MCP concepts**
   - Client-server architecture
   - Tools, Resources, and Prompts
   - Transport protocols (stdio, SSE, HTTP)
   - JSON-RPC 2.0 protocol

## Installation

### Project-Level Installation (Recommended)

1. Copy the contents of `mcp_builder_mode.yml`
2. Create or edit `.bobmodes` file in your workspace root directory
3. Paste the content (or add to existing `customModes` list)
4. Reload IBM Bob: `Cmd/Ctrl + Shift + P` → "Reload Window"
5. Select "🔌 MCP Builder" from the mode selector

### Global Installation

Copy `mcp_builder_mode.yml` to:
- **Windows**: `%APPDATA%\IBM Bob\User\globalStorage\ibm.bob-code\settings\custom_modes.yaml`
- **macOS**: `~/Library/Application Support/IBM Bob/User/globalStorage/ibm.bob-code/settings/custom_modes.yaml`
- **Linux**: `~/.config/IBM Bob/User/globalStorage/ibm.bob-code/settings/custom_modes.yaml`

## Mode Capabilities

### What This Mode Excels At

1. **MCP Server Development**
   - Creating Python MCP servers with proper async patterns
   - Building TypeScript/Node.js MCP servers
   - Implementing stdio, SSE, and HTTP transports
   - Setting up project structure and dependencies

2. **Tool Implementation**
   - Designing tools with clear schemas
   - Implementing input validation and error handling
   - Creating tools for file system access, API integration, database queries
   - Writing comprehensive tool documentation

3. **Resource Management**
   - Implementing static and dynamic resources
   - Managing resource URIs and MIME types
   - Implementing resource caching strategies
   - Handling resource subscriptions

4. **Prompt Templates**
   - Creating reusable prompt templates
   - Implementing prompt arguments and composition
   - Designing prompts for specific use cases

5. **Security & Performance**
   - Implementing credential management
   - Input validation and sanitization
   - Caching and optimization strategies
   - Rate limiting and access control

### Tool Groups Enabled

- **read**: File reading and analysis
- **edit**: Complete file editing capabilities
- **execute**: Command execution for testing and deployment
- **browser**: Testing MCP servers with web clients

## Common Use Cases

### 1. Creating a New Python MCP Server

**Task**: "Create a Python MCP server that provides file system access tools"

The mode will:
1. Create project structure with proper directories
2. Generate server.py with MCP server setup
3. Implement tools for reading, writing, and listing files
4. Add input validation and security checks
5. Create pyproject.toml with dependencies
6. Add comprehensive error handling
7. Include logging configuration
8. Provide testing examples

### 2. Building a TypeScript MCP Server

**Task**: "Create a TypeScript MCP server for API integration"

The mode will:
1. Set up TypeScript project structure
2. Generate index.ts with server implementation
3. Create tools for API requests (GET, POST, etc.)
4. Implement credential management
5. Add type definitions
6. Create package.json and tsconfig.json
7. Include error handling and logging
8. Provide build and test scripts

### 3. Implementing Custom Tools

**Task**: "Add a tool to query a PostgreSQL database"

The mode will:
1. Create tool with proper JSON Schema
2. Implement async database connection
3. Add SQL injection prevention
4. Handle connection pooling
5. Implement error handling
6. Add comprehensive logging
7. Include usage examples
8. Document security considerations

### 4. Adding Resource Support

**Task**: "Add resources for accessing documentation files"

The mode will:
1. Implement list_resources handler
2. Create read_resource handler
3. Define resource URIs and MIME types
4. Add caching for static resources
5. Implement error handling
6. Document resource structure
7. Provide usage examples

### 5. Deploying MCP Server

**Task**: "Deploy MCP server to production with SSE transport"

The mode will:
1. Convert stdio server to SSE transport
2. Add HTTP server setup (Starlette/Express)
3. Implement authentication middleware
4. Add health check endpoints
5. Create Dockerfile for containerization
6. Configure environment variables
7. Add monitoring and logging
8. Provide deployment documentation

## Best Practices When Using This Mode

### 1. Start with Clear Requirements

Provide specific details about:
- What tools/resources/prompts the server should provide
- What external systems it needs to integrate with
- Security and authentication requirements
- Performance and scalability needs
- Target deployment environment

### 2. Follow MCP Specification

- Implement all required protocol methods
- Use proper JSON-RPC 2.0 message format
- Follow capability advertisement patterns
- Support standard initialization flow
- Handle errors according to spec

### 3. Implement Security First

- Validate all inputs against schemas
- Sanitize user-provided data
- Use environment variables for credentials
- Implement rate limiting
- Log security events
- Follow least privilege principle

### 4. Test Thoroughly

- Unit test individual tools
- Integration test full server
- Test with multiple MCP clients
- Test error conditions
- Validate schema compliance
- Performance test under load

### 5. Document Comprehensively

- Write clear README with examples
- Document all tools, resources, prompts
- Provide client configuration examples
- Include troubleshooting guide
- Document security considerations
- Maintain changelog

## Example Workflows

### Workflow 1: Building a File System MCP Server

```
User: "Create a Python MCP server for file system operations"

Mode Actions:
1. Creates project structure:
   - src/mcp_server_fs/
   - tests/
   - pyproject.toml
   - README.md

2. Implements server.py with:
   - Server initialization
   - stdio transport setup
   - Logging configuration

3. Creates tools.py with:
   - read_file tool
   - write_file tool
   - list_directory tool
   - Each with proper schemas and validation

4. Adds security:
   - Path validation (prevent directory traversal)
   - Allowed directory restriction
   - File size limits

5. Creates tests:
   - test_tools.py with unit tests
   - test_server.py with integration tests

6. Generates documentation:
   - README with installation and usage
   - Tool documentation
   - Configuration examples
```

### Workflow 2: Adding API Integration Tools

```
User: "Add tools to interact with GitHub API"

Mode Actions:
1. Adds httpx dependency to pyproject.toml

2. Creates github_tools.py with:
   - get_repository tool
   - list_issues tool
   - create_issue tool
   - Each with proper GitHub API schemas

3. Implements credential management:
   - Reads GITHUB_TOKEN from environment
   - Validates token before use
   - Handles authentication errors

4. Adds error handling:
   - HTTP error handling
   - Rate limit handling
   - Network timeout handling

5. Updates server.py to register new tools

6. Adds tests for GitHub tools

7. Documents GitHub API integration
```

### Workflow 3: Converting to Remote Server (SSE)

```
User: "Convert my stdio server to use SSE transport for remote access"

Mode Actions:
1. Adds Starlette dependency

2. Creates sse_server.py with:
   - SSE endpoint handler
   - CORS configuration
   - Health check endpoint

3. Implements authentication:
   - API key validation
   - Bearer token support
   - Request logging

4. Updates deployment:
   - Creates Dockerfile
   - Adds docker-compose.yml
   - Configures environment variables

5. Adds monitoring:
   - Prometheus metrics endpoint
   - Structured logging
   - Error tracking

6. Updates documentation:
   - Deployment instructions
   - Client configuration for SSE
   - Security setup guide
```

## Tool Implementation Patterns

### Pattern 1: File System Access Tool

**Use Case**: Reading files from allowed directories

**Key Elements**:
- Path validation to prevent directory traversal
- Allowed directory restriction via environment variable
- File size limits
- Proper error handling for file not found, permission denied
- MIME type detection

### Pattern 2: API Integration Tool

**Use Case**: Making HTTP requests to external APIs

**Key Elements**:
- Credential management via environment variables
- Request timeout configuration
- Retry logic for transient failures
- Rate limit handling
- Response caching
- Comprehensive error messages

### Pattern 3: Database Query Tool

**Use Case**: Querying databases safely

**Key Elements**:
- Connection pooling
- SQL injection prevention (parameterized queries or query validation)
- Read-only query enforcement
- Query timeout
- Result size limits
- Connection error handling

### Pattern 4: Data Processing Tool

**Use Case**: Processing and transforming data

**Key Elements**:
- Input validation against schema
- Streaming for large data
- Progress reporting for long operations
- Cancellation support
- Memory-efficient processing
- Clear error messages

## Troubleshooting

### Server Not Starting

**Symptoms**: Server fails to start or crashes immediately

**Solutions**:
- Check Python/Node.js version compatibility
- Verify all dependencies are installed
- Check for syntax errors in code
- Review environment variables
- Check logs for error messages
- Validate JSON-RPC message format

### Tools Not Appearing in Client

**Symptoms**: Client doesn't see tools after connection

**Solutions**:
- Verify list_tools handler is registered
- Check tool schemas are valid JSON Schema
- Ensure server advertises tool capability
- Verify initialization completed successfully
- Check client logs for errors
- Test with MCP Inspector

### Tool Execution Failing

**Symptoms**: Tool calls return errors or timeout

**Solutions**:
- Validate input arguments match schema
- Check for exceptions in tool implementation
- Verify external dependencies are accessible
- Check credential configuration
- Review timeout settings
- Add more detailed error logging

### Transport Issues

**Symptoms**: Connection drops or messages not received

**Solutions**:
- Verify transport type matches client configuration
- Check stdio streams aren't being used for logging
- For SSE: verify CORS configuration
- Check network connectivity for remote servers
- Verify message format is correct JSON-RPC
- Test with simple echo tool first

### Performance Issues

**Symptoms**: Slow tool execution or high resource usage

**Solutions**:
- Implement caching for repeated operations
- Use connection pooling for databases
- Add request batching
- Optimize database queries
- Implement streaming for large responses
- Profile code to find bottlenecks
- Add timeout limits

## Advanced Patterns

### Pattern 1: Multi-Tool Composition

Create tools that orchestrate multiple sub-tools for complex workflows.

**Key Elements**:
- Tool dependency management
- Error handling across tool chain
- Partial result handling
- Transaction-like semantics
- Progress reporting

### Pattern 2: Streaming Responses

Implement tools that stream large responses incrementally.

**Key Elements**:
- Async generators for streaming
- Chunk size optimization
- Progress updates
- Cancellation support
- Error handling mid-stream

### Pattern 3: Resource Subscriptions

Implement resources that notify clients of updates.

**Key Elements**:
- Subscription management
- Change detection
- Notification delivery
- Subscription cleanup
- Rate limiting notifications

### Pattern 4: Prompt Composition

Create prompts that combine multiple prompt templates.

**Key Elements**:
- Prompt template registry
- Argument passing between prompts
- Conditional prompt inclusion
- Prompt versioning
- Context management

## Integration Examples

### watsonx Orchestrate Integration

```yaml
# In mcp_watsonx_orchestrate.json
{
  "mcpServers": {
    "my-mcp-server": {
      "command": "python",
      "args": ["-m", "mcp_server_name"],
      "env": {
        "API_KEY": "${API_KEY}",
        "ALLOWED_DIR": "/path/to/allowed/directory"
      },
      "alwaysAllow": [
        "tool_name_1",
        "tool_name_2"
      ],
      "disabled": false
    }
  }
}
```

### Claude Desktop Integration

```json
// In claude_desktop_config.json
{
  "mcpServers": {
    "my-mcp-server": {
      "command": "python",
      "args": ["-m", "mcp_server_name"],
      "env": {
        "API_KEY": "your-api-key"
      }
    }
  }
}
```

### Generic MCP Client Integration

```python
from mcp.client import ClientSession
from mcp.client.stdio import stdio_client

async def use_mcp_server():
    async with stdio_client("python", ["-m", "mcp_server_name"]) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # List available tools
            tools = await session.list_tools()
            print(f"Available tools: {[t.name for t in tools]}")
            
            # Call a tool
            result = await session.call_tool("tool_name", {"param": "value"})
            print(f"Result: {result.content[0].text}")
```

## Performance Optimization Tips

1. **Caching**
   - Cache expensive computations
   - Use TTL for cache entries
   - Implement LRU cache for memory limits
   - Cache external API responses
   - Cache resource content

2. **Async Operations**
   - Use async/await for all I/O
   - Parallelize independent operations
   - Use connection pooling
   - Implement request batching
   - Set appropriate timeouts

3. **Resource Management**
   - Close connections properly
   - Implement connection pooling
   - Limit concurrent operations
   - Stream large responses
   - Clean up temporary resources

4. **Code Optimization**
   - Profile code to find bottlenecks
   - Optimize hot paths
   - Use efficient data structures
   - Minimize memory allocations
   - Avoid blocking operations

## Security Checklist

- [ ] All credentials stored in environment variables
- [ ] Input validation for all tool arguments
- [ ] Path validation to prevent directory traversal
- [ ] SQL injection prevention (parameterized queries)
- [ ] Rate limiting implemented
- [ ] Timeout limits set for all operations
- [ ] Error messages don't expose sensitive information
- [ ] Logging doesn't include credentials
- [ ] HTTPS used for remote servers
- [ ] Authentication implemented for remote access
- [ ] CORS configured properly for web servers
- [ ] File size limits enforced
- [ ] Resource access restricted to allowed paths
- [ ] Regular security audits performed

## Testing Checklist

- [ ] Unit tests for all tools
- [ ] Integration tests for server lifecycle
- [ ] Schema validation tests
- [ ] Error condition tests
- [ ] Performance tests under load
- [ ] Security tests (injection, traversal, etc.)
- [ ] Client compatibility tests
- [ ] Timeout and cancellation tests
- [ ] Resource cleanup tests
- [ ] Concurrent operation tests

## Deployment Checklist

- [ ] README with installation instructions
- [ ] Environment variable documentation
- [ ] Client configuration examples
- [ ] Dockerfile created (if containerizing)
- [ ] Health check endpoint implemented
- [ ] Monitoring and logging configured
- [ ] Error tracking set up
- [ ] Backup and recovery plan
- [ ] Scaling strategy defined
- [ ] Security review completed
- [ ] Performance testing done
- [ ] Documentation complete

## Getting Help

### Within the Mode

Ask Bob to:
- "Show me an example of a file system access tool"
- "How do I implement SSE transport?"
- "Create a tool for querying PostgreSQL"
- "Add caching to my MCP server"
- "Implement authentication for remote access"
- "Convert my server to use TypeScript"

### External Resources

- **MCP Specification**: https://spec.modelcontextprotocol.io/
- **MCP Python SDK**: https://github.com/modelcontextprotocol/python-sdk
- **MCP TypeScript SDK**: https://github.com/modelcontextprotocol/typescript-sdk
- **MCP Inspector**: Tool for debugging MCP servers
- **Example Servers**: https://github.com/modelcontextprotocol/servers

### Common Commands

```bash
# Python Development
pip install mcp                    # Install MCP SDK
python -m mcp_server_name          # Run server
pytest tests/                      # Run tests
black src/                         # Format code
mypy src/                          # Type check

# Node.js Development
npm install @modelcontextprotocol/sdk  # Install MCP SDK
npm run build                      # Build TypeScript
npm start                          # Run server
npm test                           # Run tests
npm run lint                       # Lint code

# Testing with MCP Inspector
npx @modelcontextprotocol/inspector python -m mcp_server_name

# Publishing
python -m build                    # Build Python package
twine upload dist/*                # Publish to PyPI
npm publish                        # Publish to npm
```

## Next Steps

After creating your MCP server:

1. **Test Locally**: Use MCP Inspector or simple client to test
2. **Document**: Write comprehensive README and tool documentation
3. **Integrate**: Test with target platforms (watsonx Orchestrate, Claude, etc.)
4. **Optimize**: Profile and optimize performance
5. **Secure**: Complete security review and testing
6. **Deploy**: Package and deploy to target environment
7. **Monitor**: Set up monitoring and logging
8. **Maintain**: Keep dependencies updated and respond to issues

## Conclusion

The MCP Builder mode provides expert-level guidance for building production-grade MCP servers. Use it to create robust, secure, and performant MCP servers that integrate seamlessly with AI platforms and agents.

For questions or issues, refer to the MCP specification and SDK documentation, or ask Bob for specific guidance on your use case.