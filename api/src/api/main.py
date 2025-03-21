import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .clients.couchbase import CouchbaseChatClient
from .routes import router
from .utils import log

log.init(os.getenv("LOG_LEVEL", "INFO"))
logger = log.get_logger(__name__)

api_reload = os.getenv("API_RELOAD", "False").lower() == "true"

app = FastAPI(title="Customer Support Chat API", version="1.0.0", docs_url="/docs")
app.include_router(router, prefix="/api")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    # Initialize the Couchbase collections
    logger.info("Initializing database collections")
    db = CouchbaseChatClient()
    db.connect()
    db.close()
    logger.info("Database collections initialized successfully")

def main():
    api_port = os.getenv("API_PORT")
    if not api_port:
        raise ValueError("API_PORT environment variable is not set")

    logger.info(f"Starting API on port {api_port}")
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=int(api_port),
        reload=api_reload,
    )
