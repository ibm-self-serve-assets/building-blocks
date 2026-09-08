# Claude Desktop MCP

Bobserver exposes a Bob-only MCP endpoint over HTTP:

```text
http://localhost:18080/mcp
```

After deployment, use the same path on the route:

```text
https://<bobserver-route>/mcp
```

The endpoint accepts either OAuth bearer tokens or the same Basic Auth
credentials as the UI.

Default local credentials:

- username: `admin`
- password: `nowibm`

## OAuth 2.1

MCP clients that support OAuth discovery should still use the MCP resource URL:

```text
https://<bobserver-route>/mcp
```

Bobserver advertises OAuth metadata from:

```text
https://<bobserver-route>/.well-known/oauth-protected-resource
https://<bobserver-route>/.well-known/oauth-protected-resource/mcp
https://<bobserver-route>/.well-known/oauth-authorization-server
```

The authorization-code flow uses PKCE with `S256`, dynamic client registration
at `/oauth/register`, browser authorization at `/oauth/authorize`, and token
exchange at `/oauth/token`. The browser authorization page asks for the same
Bobserver admin username and password.

For Glama Inspector:

- URL: `https://<bobserver-route>/mcp`
- Transport: HTTP / Streamable HTTP
- Auth: OAuth

## Tools

The MCP server exposes these Bob tools:

- `bob_prompt_start`: start Bob asynchronously and return a `jobId`.
- `bob_prompt_status`: read current state and new output for a `jobId`.
- `bob_prompt_cancel`: cancel a running `jobId`.

`bob_prompt_start` arguments:

- `prompt`: prompt to send to Bob Shell.
- `timeoutSeconds`: maximum runtime, default `120`.
- `yolo`: allow Bob to create and update files under `/workspace`, default `true`.

`bob_prompt_status` arguments:

- `jobId`: id returned by `bob_prompt_start`.
- `offset`: output offset returned by the previous status call, default `0`.

## Local Smoke Test

```bash
curl -u admin:nowibm \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  http://localhost:18080/mcp \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"curl","version":"1.0.0"}}}'
```

```bash
curl -u admin:nowibm \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  http://localhost:18080/mcp \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/list"}'
```

```bash
curl -u admin:nowibm \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  http://localhost:18080/mcp \
  -d '{"jsonrpc":"2.0","id":4,"method":"tools/call","params":{"name":"bob_prompt_start","arguments":{"prompt":"Read @bob_context.md first. List /workspace files.","timeoutSeconds":120,"yolo":true}}}'
```

Then read with the returned `jobId`:

```bash
curl -u admin:nowibm \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  http://localhost:18080/mcp \
  -d '{"jsonrpc":"2.0","id":5,"method":"tools/call","params":{"name":"bob_prompt_status","arguments":{"jobId":"<jobId>","offset":0}}}'
```

## Claude Desktop Pointer

Use the local URL while testing:

```text
http://localhost:18080/mcp
```

When the updated container is deployed, change only the URL:

```text
https://<bobserver-route>/mcp
```

If Claude Desktop asks for headers instead of username/password, use:

```text
Authorization: Basic <base64(admin:nowibm)>
```
