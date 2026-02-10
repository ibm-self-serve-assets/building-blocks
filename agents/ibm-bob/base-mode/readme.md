# Base custom mode for IBM Bob using watsonx Orchestrate
This [custom mode for IBM Bob](https://internal.bob.ibm.com/docs/ide/features/custom-modes) is a simple example that configured Bob to use watsonx Orchestrate.  You will need to import both the Bob mode plus add the two watsonx Orchestrate MCP servers listed in the [mcp_watsonx_orchestrate.json](mcp_watsonx_orchestrate.json).  


## Setting up the watsonx Orchestrate MCP Servers
If you haven't added MCP servers into your IBM Bob instance year, read about [mcp servers in IBM Bob](https://internal.bob.ibm.com/docs/ide/features/mcp/using-mcp-in-bob).  There are two MCP servers provided in the [mcp_watsonx_orchestrate.json](mcp_watsonx_orchestrate.json).

1. Documentation for watsonx Orchestrate
2. watsonX orchestrate ADK

For the 2nd MCP server to work, you need to install the [watsonX orchestrate ADK](https://developer.watson-orchestrate.ibm.com/).  You must also update the value for the environment variable of **WXO_MCP_WORKING_DIRECTORY** in [mcp_watsonx_orchestrate.json](mcp_watsonx_orchestrate.json) by providing the full path to your code project directory.  Since this value will change across different projects as you work with IBM Bob, you should add the MCP server at the Project rather than Global level.



