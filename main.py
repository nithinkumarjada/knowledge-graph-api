from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.core.config import settings
from app.db.neo4j import neo4j_connection
from app.db.postgres import create_tables
from app.routers import auth, documents, queries, audit

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown."""
    # Startup
    logger.info("Starting up Knowledge Graph Query API")
    try:
        await neo4j_connection.connect()
        await neo4j_connection.initialize_schema()
        logger.info("Neo4j connected and schema initialized")
    except Exception as e:
        logger.error(f"Failed to connect to Neo4j: {e}")
    
    try:
        create_tables()
        logger.info("PostgreSQL tables created")
    except Exception as e:
        logger.error(f"Failed to create PostgreSQL tables: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Knowledge Graph Query API")
    await neo4j_connection.disconnect()
    logger.info("Neo4j connection closed")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.API_VERSION,
    description="Knowledge Graph Query API with Neo4j, FastAPI, and PostgreSQL",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(documents.router)
app.include_router(queries.router)
app.include_router(audit.router)


@app.get("/")
async def root() -> dict:
    """Root endpoint."""
    return {
        "message": "Welcome to Knowledge Graph Query API",
        "docs": "/docs",
        "version": settings.API_VERSION
    }


@app.get("/health")
async def health_check() -> dict:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": settings.APP_NAME
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
