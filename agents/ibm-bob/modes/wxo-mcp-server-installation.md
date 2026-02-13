# How to install watsonx Orchestrate's MCP Server in IBM Bob

Follow these instructions to install both watsonx Orchestrate MCP servers:
1. Open the IBM Bob IDE
2. Open your project
3. In the right pane for IBM Bob, click ... > MCP Servers

![Screenshot of MCP server selection](./images/select-mcp-server.png)

4. Search for watsonx Orchestrate:

![Screenshot of MCP server selection](./images/wxo-mcp-servers.png)

5. Select the **watsonx Orchestrate ADK Docs** MCP server and click **Install**. Choose the installation scope (current Project or Global), then click Install. Important: Make sure Python and uv are installed in your system before you continue.

![Screenshot of MCP server selection](./images/wxo-adk-docs-mcp-server.png)

6. Click Install on **watsonx Orchestrate ADK** MCP server.
   
    a. Set the installation scope to Project.
    
    b. Set the installation method to Latest ADK Version.
    
    c. Enter the absolute path of your project directory in Current Project Working Directory.
    
    d. Click Install.

![Screenshot of MCP server selection](./images/wxo-adk-mcp-server.png)

6. Both MCP servers should now be marked as healthy. Close the Settings page to continue.

![Screenshot of MCP server selection](./images/wxo-mcp-server-installed.png)