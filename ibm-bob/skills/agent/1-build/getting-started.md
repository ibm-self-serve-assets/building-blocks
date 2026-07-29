# Getting Started with Agent Builder

Complete workflow for building watsonx Orchestrate agents with MCP-first approach.

## ⚠️ MANDATORY First Step: Verify MCP Connection

**Before starting ANY agent development work, verify the MCP ADK documentation server is accessible:**

```xml
<use_mcp_tool>
<server_name>watsonx-orchestrate-adk-docs</server_name>
<tool_name>SearchIbmWatsonxOrchestrateAdk</tool_name>
<arguments>
{
  "query": "agent development"
}
</arguments>
</use_mcp_tool>
```

**If the connection test fails:**
1. Check MCP server configuration in `.bob/mcp.json`
2. Verify the server is running and accessible
3. Confirm authentication credentials are valid
4. **DO NOT proceed with implementation until connection is working**

**If the connection succeeds:**
- You'll receive documentation results about agent development
- This confirms the MCP server is ready for use
- You can now proceed with the workflow below

## Core Workflow

### Phase 1: Discovery and Requirements

<Steps>
<Step>
**Conduct interactive questionnaire** to gather all requirements:
- Primary business problem or use case
- Target users and their needs
- Key tasks and workflows
- Data sources and system integrations
- Document/knowledge base requirements
- Complexity level (simple/moderate/complex/multi-agent)
- LLM model preferences
- User interaction channels
- Environment requirements
</Step>

<Step>
**Search MCP docs for relevant patterns** based on requirements:
- Similar use case examples
- Recommended architecture patterns
- Latest best practices
- Model capabilities and selection
</Step>

<Step>
**Summarize gathered information** and confirm understanding with user before proceeding.
</Step>
</Steps>

### Phase 2: Project Structure

<Steps>
<Step>
**Search MCP docs** for current project structure recommendations:
```
Query: "project structure best practices"
Query: "getting started with ADK"
```
</Step>

<Step>
**Create IBM-recommended folder structure** based on project complexity:

```bash
mkdir -p project-name/{agents,tools,knowledge,connections,scripts}
```

Standard structure:
- `agents/` - Agent specification files (YAML/JSON)
- `tools/` - Python tools and tool packages
- `knowledge/` - Knowledge base specifications and documents
- `connections/` - Connection specifications
- `scripts/` - Deployment and utility scripts
</Step>

<Step>
**Create foundational files:**
- `README.md` - Project documentation
- `.gitignore` - Exclude sensitive files
- `requirements.txt` - Python dependencies
</Step>
</Steps>

### Phase 3: Planning

<Steps>
<Step>
**Search MCP docs** for architecture guidance:
```
Query: "agent architecture patterns"
Query: "multi-agent design"
Query: "[specific use case] examples"
```
</Step>

<Step>
**Create comprehensive plan.md** with:
- Executive Summary
- Requirements Summary
- Architecture Design
- Implementation Plan (phased approach)
- Technical Specifications
- Testing Strategy
- Deployment Strategy
- Timeline and Milestones
</Step>

<Step>
**Present plan for user review and approval** before implementation.
</Step>
</Steps>

### Phase 4: Implementation

**CRITICAL: Search MCP docs before implementing EACH component**

<Steps>
<Step>
**For each agent:**
1. Search: "create native agent", "agent YAML specification"
2. Verify current syntax and required fields
3. Create agent YAML with proper structure
4. Follow snake_case naming convention
</Step>

<Step>
**For each tool:**
1. Search: "Python tool decorator", "@tool decorator template"
2. Verify current decorator syntax
3. Create tool with proper type hints and docstring
4. Add authentication if needed (@expect_credentials)
</Step>

<Step>
**For each knowledge base:**
1. Search: "knowledge base configuration", "RAG setup"
2. Verify document format requirements
3. Create knowledge base specification
4. Prepare and validate documents
</Step>

<Step>
**For each connection:**
1. Search: "connection types", "authentication methods"
2. Verify connection configuration format
3. Create connection specification
4. Link to tools via app_id
</Step>

<Step>
**For each channel:**
1. Search: "[channel type] integration", "channel setup"
2. Verify channel configuration requirements
3. Create channel specification
4. Configure webhooks and credentials
</Step>
</Steps>

### Phase 5: Testing

<Steps>
<Step>
**Test each component independently:**
- Test Python tools in isolation
- Test agent with tools
- Test knowledge base retrieval
- Test multi-agent routing (if applicable)
- Test channel integration
</Step>

<Step>
**Search MCP docs for testing guidance:**
```
Query: "testing agents"
Query: "debugging agent behavior"
Query: "testing best practices"
```
</Step>

<Step>
**Validate in draft environment** before promoting to live.
</Step>
</Steps>

### Phase 6: Deployment

<Steps>
<Step>
**Search MCP docs for deployment procedures:**
```
Query: "deployment automation"
Query: "orchestrate CLI commands"
Query: "deployment best practices"
```
</Step>

<Step>
**Generate deployment script** (deploy.sh or deploy.py) with:
- Environment setup
- Tool imports
- Knowledge base imports
- Connection configuration
- Agent imports
- Channel setup
- Verification steps
</Step>

<Step>
**Create comprehensive README.md** documenting:
- Project overview
- Architecture
- Prerequisites
- Installation steps
- Deployment instructions
- Usage examples
- Testing procedures
- Troubleshooting
</Step>

<Step>
**Execute deployment** and verify all components.
</Step>
</Steps>

## Critical Rules

1. **MANDATORY UNBYPASSABLE:** Search MCP docs before implementing ANY component
2. **NEVER skip the discovery questionnaire** - understanding requirements is essential
3. **NEVER start implementation without approved plan** - planning prevents rework
4. **ALWAYS use snake_case** for all names (agents, tools, files)
5. **ALWAYS test in draft** before promoting to live
6. **ALWAYS cite MCP documentation** sources in responses

## When User Says "Don't Use Tools"

This typically means:
- ✅ Don't create Python tools with @tool decorator
- ✅ Don't add external API integrations
- ✅ Keep the agent simple

This does NOT mean:
- ❌ Skip MCP documentation search (ALWAYS required)
- ❌ Skip validation of specifications
- ❌ Skip checking current syntax

**Always search MCP docs regardless of user instructions about "tools."**

## Quick Reference

### Essential MCP Searches

**Agent Development:**
- "create native agent"
- "agent instructions best practices"
- "agent styles"
- "agent collaborators"

**Tool Development:**
- "Python tool decorator"
- "@tool decorator template"
- "expect_credentials"
- "tool authentication"

**Knowledge Bases:**
- "knowledge base configuration"
- "RAG setup"
- "document indexing"

**Connections:**
- "connection types"
- "authentication methods"
- "connection configuration"

**Deployment:**
- "deployment automation"
- "orchestrate CLI commands"
- "deployment best practices"

## Next Steps

After completing this workflow:
1. Review [Best Practices](best-practices.md) for critical conventions
2. Check [Deployment Safety](deployment-safety.md) for safe automation
3. Use [Quality Checklist](checklist.md) to verify completeness
4. Consult [MCP Documentation Guide](mcp-documentation-guide.md) for search strategies