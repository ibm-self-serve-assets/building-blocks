from fastapi import APIRouter, requests as request
from fastapi.responses import HTMLResponse

root_api_route = APIRouter(tags=["Default"])

API_PREFIX = "/"

@root_api_route.get(API_PREFIX)
def root_api():
    return HTMLResponse(
        """
        <html>
                <head>
                    <title>Milvus RAG API</title>
                </head>
                <body>
                    <h1>Milvus RAG API</h1>
                    <h3>For complete API documentation visit <a href="/docs">docs</a></h3>
                </body>
        </html>
        """
    )