# MCP Documentation Strategy

How to effectively use the watsonx-orchestrate-adk-docs MCP server for up-to-date documentation.

## Core Principle

The watsonx-orchestrate-adk-docs MCP server contains the latest IBM watsonx Orchestrate documentation. **MANDATORY AND UNBYPASSABLE: Search it first for technical details, API references, and examples.**

## Why This Cannot Be Skipped

MCP documentation search is **MANDATORY AND UNBYPASSABLE** because:

1. **Accuracy**: ADK specifications change frequently. Static examples may be outdated.
2. **Completeness**: Documentation contains required fields that may not be in examples.
3. **Validation**: Ensures generated code matches current ADK requirements.
4. **Best Practices**: Latest patterns and conventions are only in current docs.

**This requirement applies even when:**
- User says "don't use tools" (they mean agent tools, not MCP search)
- User says "keep it simple" (simple still requires correct syntax)
- User says "just create the files" (files must match current specs)
- Time is limited (incorrect files waste more time than searching)

## Common Misunderstandings

### "Don't use tools" Does NOT Mean Skip MCP Search

When users say "don't use tools," they typically mean:
- ✅ Don't create Python tools with @tool decorator
- ✅ Don't add external API integrations
- ✅ Keep the agent simple without complex tooling

They DO NOT mean:
- ❌ Skip MCP documentation search (ALWAYS required)
- ❌ Skip validation of specifications
- ❌ Skip checking current syntax

**Always search MCP docs regardless of user instructions about "tools."**

## When to Search MCP

Search the MCP documentation server in these scenarios:

- User asks about specific ADK features or capabilities
- Need to verify tool parameters or syntax
- Looking for code examples or best practices
- Checking latest API changes or updates
- Understanding agent configuration options
- Learning about new features or deprecations
- Uncertain about CLI command syntax
- Need to verify deployment procedures

## How to Search Effectively

### Use Specific Technical Terms

**Good queries:**
- "create native agent"
- "Python tool decorator"
- "knowledge base RAG"
- "connection authentication"

**Bad queries:**
- "agent"
- "tool"
- "setup"

### Search for Concepts, Not Just Keywords

**Good:**
- "agent collaboration" (finds multi-agent patterns)
- "tool authentication" (finds credential management)
- "deployment automation" (finds CLI workflows)

**Bad:**
- "collaborators" (too narrow)
- "credentials" (too broad)
- "deploy" (ambiguous)

### Include Version Context When Relevant

**Examples:**
- "v0.7 agent styles"
- "latest tool decorator syntax"
- "current connection types"

### Search Multiple Times with Different Queries

If first search doesn't yield results, try:
- Different terminology
- Broader or narrower scope
- Related concepts
- Specific use cases

### Combine MCP Results with Workflow Guidance

1. Search MCP docs for technical details
2. Apply workflow patterns from these rules
3. Follow best practices and conventions
4. Provide comprehensive answer with citations

## Search Tool Usage

**Tool name:** SearchIbmWatsonxOrchestrateAdk

**Server name:** watsonx-orchestrate-adk-docs

**Example:**
```xml
<use_mcp_tool>
<server_name>watsonx-orchestrate-adk-docs</server_name>
<tool_name>SearchIbmWatsonxOrchestrateAdk</tool_name>
<arguments>
{
  "query": "create native agent with Python tools"
}
</arguments>
</use_mcp_tool>
```

## Workflow Integration

<Steps>
<Step>
User asks a question or requests help
</Step>
<Step>
Search MCP docs for relevant information
</Step>
<Step>
Combine MCP results with workflow guidance from rules
</Step>
<Step>
Provide comprehensive answer with citations to docs
</Step>
<Step>
Proceed with implementation using latest information
</Step>
</Steps>

## Common Search Patterns

### Agent Development
- "create native agent"
- "agent instructions"
- "agent styles"
- "agent collaborators"
- "multi-agent systems"

### Tool Development
- "Python tool decorator"
- "@tool decorator"
- "tool template"
- "expect_credentials"
- "tool authentication"

### Knowledge Bases
- "knowledge base"
- "RAG"
- "document indexing"
- "embedding models"
- "knowledge base status"

### Connections
- "connections"
- "authentication types"
- "API key connection"
- "connection configuration"
- "credential management"

### Channels
- "channels"
- "webchat"
- "Slack integration"
- "WhatsApp"
- "phone integration"

### Deployment
- "deployment script"
- "CLI commands"
- "orchestrate tools import"
- "orchestrate agents import"
- "deployment automation"

### Testing
- "testing agents"
- "testing tools"
- "agent debugging"
- "testing multi-agent systems"

## Citing Sources

When using MCP documentation, always cite the source in your response.

**Good example:**
"According to the IBM watsonx Orchestrate ADK documentation, native agents support three styles: default, react, and planner..."

**Bad example:**
"Native agents support three styles..." (no citation)

## Verification Strategy

When uncertain about any technical detail:

1. **Search first** - Query MCP docs before answering
2. **Verify syntax** - Use --help flag if needed
3. **Answer with confidence** - Provide accurate information based on latest docs
4. **Cite source** - Reference the documentation

## MCP Search Tips

### Tip 1: Start Broad, Then Narrow
- First search: "agent development"
- Follow-up: "agent instructions best practices"
- Specific: "agent routing logic examples"

### Tip 2: Use Action Verbs
- "create agent"
- "import tool"
- "configure connection"
- "deploy agent"

### Tip 3: Include Context
- "Python tool with authentication"
- "multi-agent routing patterns"
- "external knowledge base configuration"

### Tip 4: Search for Examples
- "agent YAML example"
- "tool decorator example"
- "deployment script example"

### Tip 5: Check for Updates
- "latest agent features"
- "new tool capabilities"
- "recent API changes"

## Integration with Other Workflows

### During Discovery (getting-started.md)
Search for:
- Similar use case examples
- Recommended architecture patterns
- Latest best practices

### During Implementation (workflow-patterns.md)
Search before each component:
- Latest syntax and parameters
- Code examples and templates
- API changes or deprecations

### During Deployment (deployment-safety.md)
Search for:
- Current CLI command syntax
- Deployment best practices
- Verification procedures

### During Troubleshooting
Search for:
- Error messages
- Common issues
- Debugging techniques

## Critical Rules

1. **MANDATORY UNBYPASSABLE: Search MCP docs first** for technical questions
2. **Use specific, technical search terms** for better results
3. **Search multiple times** with different queries if needed
4. **Combine MCP results** with workflow guidance
5. **Cite sources** when using documentation
6. **Verify with --help** when uncertain about CLI syntax
7. **Keep searches focused** on specific topics or tasks