#!/usr/bin/env node

const url = process.env.BOBSERVER_MCP_URL || "http://localhost:18080/mcp";
const authorization = process.env.BOBSERVER_MCP_AUTH || "Basic YWRtaW46bm93aWJt";

process.stdin.setEncoding("utf8");

let buffer = "";
process.stdin.on("data", async (chunk) => {
  buffer += chunk;
  const lines = buffer.split(/\r?\n/);
  buffer = lines.pop() || "";

  for (const line of lines) {
    const trimmed = line.trim();
    if (!trimmed) continue;
    await forwardMessage(trimmed);
  }
});

process.stdin.on("end", async () => {
  const trimmed = buffer.trim();
  if (trimmed) {
    await forwardMessage(trimmed);
  }
});

async function forwardMessage(rawMessage) {
  let message;
  try {
    message = JSON.parse(rawMessage);
  } catch (error) {
    writeMessage({
      jsonrpc: "2.0",
      id: null,
      error: {
        code: -32700,
        message: `Parse error: ${error.message}`,
      },
    });
    return;
  }

  try {
    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
        "Authorization": authorization,
      },
      body: JSON.stringify(message),
    });

    if (response.status === 202) {
      return;
    }

    const text = await response.text();
    if (!response.ok) {
      writeMessage({
        jsonrpc: "2.0",
        id: message.id ?? null,
        error: {
          code: -32000,
          message: text || `Bobserver MCP HTTP ${response.status}`,
        },
      });
      return;
    }

    if (text.trim()) {
      process.stdout.write(`${text.trim()}\n`);
    }
  } catch (error) {
    writeMessage({
      jsonrpc: "2.0",
      id: message.id ?? null,
      error: {
        code: -32000,
        message: `Unable to reach Bobserver MCP at ${url}: ${error.message}`,
      },
    });
  }
}

function writeMessage(message) {
  process.stdout.write(`${JSON.stringify(message)}\n`);
}
