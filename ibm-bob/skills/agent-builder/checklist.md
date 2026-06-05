# Agent Development Quality Checklist

Comprehensive checklist for verifying agent development quality and completeness.

## Pre-Implementation Checklist

### Discovery Phase
- [ ] Conducted discovery questionnaire with user
- [ ] Gathered business problem and use case
- [ ] Identified primary users
- [ ] Documented key tasks and workflows
- [ ] Identified data sources and systems
- [ ] Determined knowledge base requirements
- [ ] Established complexity level
- [ ] Selected LLM model
- [ ] Identified interaction channels
- [ ] Defined required environments

### Planning Phase
- [ ] Searched MCP docs for relevant patterns
- [ ] Created IBM-recommended project structure
- [ ] Switched to Plan mode
- [ ] Created comprehensive plan.md
- [ ] Included all required plan sections
- [ ] Got explicit plan approval from user
- [ ] Switched back to Agent Builder mode

## Implementation Checklist

### Project Structure
- [ ] Created agents/ folder
- [ ] Created tools/ folder
- [ ] Created knowledge/ folder (if needed)
- [ ] Created connections/ folder (if needed)
- [ ] Created scripts/ folder
- [ ] Created README.md
- [ ] Created .gitignore
- [ ] Created requirements.txt
- [ ] All folders use snake_case naming

### Naming Conventions
- [ ] All agent names use snake_case
- [ ] All tool names use snake_case
- [ ] All file names use snake_case
- [ ] No spaces, hyphens, or special characters in names
- [ ] Names are descriptive and domain-specific
- [ ] Avoided generic names (helper, processor, etc.)

### Python Tools
- [ ] Searched MCP docs for tool template
- [ ] Used @tool decorator
- [ ] Function names are snake_case
- [ ] All parameters have type hints
- [ ] Return type is specified
- [ ] Comprehensive docstring provided
- [ ] Error handling implemented
- [ ] Input validation added
- [ ] Used @expect_credentials for authenticated tools
- [ ] Linked to connections via app_id
- [ ] Tested tools independently

### Native Agents
- [ ] Searched MCP docs for agent creation
- [ ] Agent name is snake_case
- [ ] Description is clear and routing-oriented
- [ ] Instructions are specific and actionable
- [ ] LLM model specified (default: groq/openai/gpt-oss-120b)
- [ ] Agent style selected appropriately
- [ ] Tools attached correctly
- [ ] Collaborators specified (if multi-agent)
- [ ] Knowledge bases attached (if needed)
- [ ] Instructions include tool usage guidelines
- [ ] Instructions include error handling approach
- [ ] Tested agent behavior in draft

### Knowledge Bases
- [ ] Searched MCP docs for KB setup
- [ ] Documents prepared in supported formats
- [ ] KB specification created
- [ ] Imported knowledge base
- [ ] Verified indexing status with check_knowledge_base_status
- [ ] Attached to agent correctly
- [ ] Agent instructions specify when to use KB
- [ ] Agent told not to invent information
- [ ] Tested KB retrieval

### Connections
- [ ] Searched MCP docs for connection types
- [ ] Created connection with appropriate type
- [ ] Configured for draft environment
- [ ] Configured for live environment
- [ ] Set credentials securely
- [ ] Linked to tools/agents via app_id
- [ ] No credentials hardcoded in code
- [ ] Tested connection authentication

### Channels
- [ ] Searched MCP docs for channel setup
- [ ] Selected appropriate channel type
- [ ] Created/configured channel
- [ ] Tested channel integration
- [ ] Generated webchat embed (if applicable)

### Multi-Agent Systems
- [ ] Searched MCP docs for multi-agent patterns
- [ ] Designed agent hierarchy
- [ ] Created specialist agents first
- [ ] Parent agent has clear routing instructions
- [ ] Each specialist has focused responsibility
- [ ] Routing scenarios documented
- [ ] Tested collaboration flow

## Testing Checklist

### Component Testing
- [ ] Tested Python tools independently
- [ ] Tested agent with tools
- [ ] Tested knowledge base retrieval
- [ ] Tested multi-agent routing (if applicable)
- [ ] Tested channel integration

### Test Scenarios
- [ ] Happy path - everything works
- [ ] Error handling - tool failures
- [ ] Edge cases - unexpected inputs
- [ ] Performance - response times
- [ ] Security - no data leakage

### Draft Environment Testing
- [ ] All assets imported to draft
- [ ] Tested in Orchestrate UI
- [ ] Tested with orchestrate chat ask
- [ ] Verified tool execution
- [ ] Verified KB retrieval
- [ ] Verified connection authentication
- [ ] All issues resolved

## Deployment Checklist

### Deployment Scripts
- [ ] Searched MCP docs for CLI commands
- [ ] Validated project structure with list_files
- [ ] Created deploy.sh in scripts/ folder
- [ ] Script changes to project root first
- [ ] Used exact CLI syntax from MCP docs
- [ ] Included all required flags
- [ ] Added error handling (set -e)
- [ ] Added progress messages
- [ ] Made script executable (chmod +x)
- [ ] Created rollback.sh
- [ ] Tested script syntax (dry run if possible)
- [ ] **Did NOT execute deployment commands directly**

### Deployment Script Contents
- [ ] Environment activation
- [ ] Tool imports
- [ ] Knowledge base imports
- [ ] Connection configuration
- [ ] Agent imports
- [ ] Channel setup
- [ ] Verification steps

### Documentation
- [ ] Created comprehensive README.md
- [ ] Included project overview
- [ ] Documented architecture
- [ ] Listed prerequisites
- [ ] Provided installation instructions
- [ ] Documented deployment process
- [ ] Included usage examples
- [ ] Added troubleshooting section
- [ ] Documented maintenance procedures
- [ ] Included project structure diagram

### Final Verification
- [ ] All deliverables present
- [ ] All documentation complete
- [ ] Deployment scripts ready
- [ ] User informed how to deploy
- [ ] plan.md preserved in project

## Security Checklist

- [ ] No credentials hardcoded in code
- [ ] All credentials stored in connections
- [ ] Used @expect_credentials for authenticated tools
- [ ] Input validation implemented
- [ ] Output sanitization implemented
- [ ] Appropriate connection types used (team vs member)
- [ ] Sensitive data not logged
- [ ] Error messages don't expose secrets

## Performance Checklist

- [ ] Tool implementations are efficient
- [ ] Appropriate agent style selected
- [ ] Knowledge base document size reasonable
- [ ] No unnecessary API calls
- [ ] Caching implemented where appropriate
- [ ] Response times acceptable

## Documentation Checklist

- [ ] Agent purpose documented
- [ ] Tool functionality documented
- [ ] Connection requirements documented
- [ ] Channel configurations documented
- [ ] Testing procedures documented
- [ ] Deployment steps documented
- [ ] Troubleshooting guide included

## MCP Documentation Usage

- [ ] Searched MCP docs before each component
- [ ] Verified latest syntax and parameters
- [ ] Cited sources in responses
- [ ] Used --help flag when uncertain
- [ ] Kept documentation references current

## Best Practices Adherence

- [ ] Followed snake_case naming everywhere
- [ ] Used default model unless specified
- [ ] Wrote clear, specific agent instructions
- [ ] Tested components independently
- [ ] Created both deploy and rollback scripts
- [ ] Never executed deployment commands directly
- [ ] Kept user informed of progress
- [ ] Used update_todo_list to track progress

## Final Deliverables

- [ ] Fully functional agents
- [ ] Python tools with proper authentication
- [ ] Configured knowledge bases
- [ ] Set up connections
- [ ] Configured channels
- [ ] Automated deployment script
- [ ] Automated rollback script
- [ ] Comprehensive README.md
- [ ] plan.md (implementation plan)
- [ ] All source files in version control

## Sign-Off

- [ ] All checklist items completed
- [ ] User reviewed and approved
- [ ] Ready for deployment
- [ ] Deployment instructions provided to user