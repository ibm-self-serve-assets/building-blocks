# MCP Builder Mode - Guide

## Why Use This Custom Mode?

The **MCP Builder** mode transforms IBM Bob from a general-purpose coding assistant into an expert MCP (Model Context Protocol) server developer. Instead of learning MCP patterns through trial and error, this mode gives Bob comprehensive knowledge of MCP architecture, best practices, and common pitfalls.

### The Problem with Default Code Mode

When using Bob's default Code mode for MCP server development:
- ❌ Bob doesn't know MCP-specific patterns and protocol requirements
- ❌ You have to explain JSON-RPC 2.0, transport protocols, and tool schemas repeatedly
- ❌ Bob might suggest approaches that work generally but violate MCP specification
- ❌ No built-in knowledge of security patterns for MCP servers
- ❌ You spend time debugging protocol compliance issues

### What This Mode Provides

With the MCP Builder mode:
- ✅ **Expert Context**: Bob understands MCP protocol, transport types, and implementation patterns
- ✅ **Specification Compliance**: Automatically follows MCP spec for protocol messages and lifecycle
- ✅ **Production-Ready Code**: Generates secure, performant MCP servers with proper error handling
- ✅ **Multi-Language Support**: Expert guidance for both Python and TypeScript/Node.js
- ✅ **Time Savings**: No need to explain MCP concepts or debug protocol issues


## Key Advantages

### 1. Protocol Expertise

The mode includes deep knowledge about:
- JSON-RPC 2.0 message format
- MCP initialization and capability advertisement
- Tool, Resource, and Prompt implementation patterns
- Transport protocols (stdio, SSE, HTTP)
- Error handling and response formats

### 2. Security by Default

Every suggestion includes:
- Input validation against schemas
- Credential management patterns
- Path traversal prevention
- SQL injection prevention
- Rate limiting strategies
- Secure error messages

### 3. Multi-Language Support

Expert guidance for:
- **Python**: Async patterns, type hints, proper project structure
- **TypeScript/Node.js**: Type safety, async/await, package configuration
- Both languages follow MCP best practices

### 4. Production-Ready Patterns

Built-in knowledge of:
- Caching strategies
- Connection pooling
- Performance optimization
- Testing approaches
- Deployment patterns
- Integration with AI platforms

## Installation

### Prerequisites

**For Python:**
```bash
python --version  # 3.10 or higher
pip install mcp
```

**For TypeScript/Node.js:**
```bash
node --version  # 18 or higher
npm install @modelcontextprotocol/sdk
```

### Setup Steps

1. Copy contents of `mcp_builder_mode.yml`
2. Create/edit `.bobmodes` in your workspace root
3. Paste the mode configuration
4. Reload IBM Bob (`Cmd/Ctrl + Shift + P` → "Reload Window")
5. Select "🔌 MCP Builder" from mode selector

## Usage Patterns

### Pattern 1: New MCP Server

```
"Create a Python MCP server for file system operations"
```

Bob will:
- Set up complete project structure
- Implement stdio transport
- Create tools with proper schemas
- Add security validation
- Include tests and documentation

### Pattern 2: Adding Tools

```
"Add a tool to query PostgreSQL database"
```

Bob will:
- Create tool with comprehensive schema
- Implement connection pooling
- Add SQL injection prevention
- Handle errors properly
- Include usage examples

### Pattern 3: Transport Conversion

```
"Convert my stdio server to use SSE transport for remote access"
```

Bob will:
- Add SSE transport implementation
- Configure HTTP server (Starlette/Express)
- Implement authentication
- Add CORS configuration
- Update deployment documentation

### Pattern 4: Integration

```
"Configure this MCP server for watsonx Orchestrate"
```

Bob will:
- Ensure stdio transport compatibility
- Optimize tool descriptions for agent routing
- Add environment variable configuration
- Create integration documentation
- Provide toolkit import commands

## When to Use This Mode

**Use MCP Builder Mode when:**
- Creating new MCP servers
- Adding tools, resources, or prompts to MCP servers
- Converting between transport protocols
- Implementing security patterns
- Optimizing MCP server performance
- Integrating with AI platforms
- Debugging MCP protocol issues

**Use Default Code Mode when:**
- Writing general Python/JavaScript code
- Working on non-MCP projects
- General debugging tasks
- Unrelated programming work

## Learning Resources

This mode complements (not replaces) official documentation:

- **[MCP Specification](https://spec.modelcontextprotocol.io/)**: Complete protocol specification
- **[MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)**: Python implementation guide
- **[MCP TypeScript SDK](https://github.com/modelcontextprotocol/typescript-sdk)**: TypeScript implementation guide
- **[Example MCP Servers](https://github.com/modelcontextprotocol/servers)**: Reference implementations

The mode uses this knowledge to provide contextual, specification-compliant guidance.

## Tips for Maximum Effectiveness

1. **Start Simple**: Begin with basic tools, then add complexity
2. **Test Early**: Use MCP Inspector to validate protocol compliance
3. **Security First**: Always ask Bob to include security validation
4. **Document Well**: Request comprehensive README and tool documentation
5. **Version Control**: Export and commit after each major change

## Integration Examples

### watsonx Orchestrate

```
"Configure this MCP server for watsonx Orchestrate integration"
```

Bob will provide:
- Toolkit import command
- Environment variable configuration
- Tool description optimization
- Integration testing approach

### Claude Desktop

```
"Add Claude Desktop configuration for this server"
```

Bob will provide:
- claude_desktop_config.json example
- Installation instructions
- Troubleshooting guide

### Generic MCP Client

```
"Show me how to use this server with a generic MCP client"
```

Bob will provide:
- Client code example
- Connection setup
- Tool invocation examples

## Troubleshooting

### Mode Not Appearing
- Verify `.bobmodes` file is in workspace root
- Check YAML syntax is valid
- Reload IBM Bob window

### Bob Doesn't Seem to Know MCP
- Verify you've selected "🔌 MCP Builder" mode
- Try asking: "Explain MCP tool schemas"
- Check mode is properly loaded in Bob's status

### Protocol Compliance Issues
- Ask Bob: "Validate this against MCP specification"
- Use MCP Inspector to test: `npx @modelcontextprotocol/inspector python -m your_server`
- Request Bob to review JSON-RPC message format

## Common Commands

```bash
# Python Development
pip install mcp                    # Install SDK
python -m your_mcp_server          # Run server
pytest tests/                      # Run tests

# Node.js Development
npm install @modelcontextprotocol/sdk  # Install SDK
npm run build                      # Build TypeScript
npm start                          # Run server
npm test                           # Run tests

# Testing with MCP Inspector
npx @modelcontextprotocol/inspector python -m your_mcp_server
npx @modelcontextprotocol/inspector node dist/index.js
```

## Getting Help

- **Within the mode**: Ask Bob specific questions about MCP concepts
- **Official docs**: Refer to [spec.modelcontextprotocol.io](https://spec.modelcontextprotocol.io/)
- **Examples**: Check [github.com/modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers)

## Summary

The MCP Builder mode is your expert pair programmer for MCP server development. It ensures protocol compliance, implements security best practices, and generates production-ready code without requiring you to memorize the MCP specification or debug protocol issues. Think of it as having an MCP expert guiding every implementation decision.