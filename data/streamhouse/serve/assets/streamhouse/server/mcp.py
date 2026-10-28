# Optional real Confluent RTCE MCP connector. Opt-in only; credentials never reach the browser.


def with_mcp(operation):
    import os
    endpoint = os.environ.get("RTCE_MCP_ENDPOINT")
    token = os.environ.get("RTCE_MCP_BASIC_TOKEN")
    if not endpoint or not token:
        raise RuntimeError("RTCE MCP is not configured. See docs/cloud-setup.md")
    if not endpoint.startswith("https://"):
        raise RuntimeError("RTCE MCP endpoint must be HTTPS.")
    try:
        from mcp.client.streamable_http import streamablehttp_client  # type: ignore
        from mcp import ClientSession  # type: ignore
    except Exception as exc:  # pragma: no cover - cloud-only optional dependency
        raise RuntimeError(f"MCP SDK not installed: {exc}")

    import anyio  # type: ignore

    async def run():
        headers = {"Authorization": f"Basic {token}"} if token else {}
        async with streamablehttp_client(endpoint, headers=headers) as (read, write, _):
            async with ClientSession(read, write) as session:
                await session.initialize()
                return await operation(session)

    return anyio.run(run)
