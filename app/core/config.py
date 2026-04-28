from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Neo4j
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "password"
    
    # PostgreSQL
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/knowledge_graph_audit"
    
    # API
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Application
    DEBUG: bool = False
    APP_NAME: str = "Knowledge Graph Query API"
    API_VERSION: str = "1.0.0"
    
    class Config:
        env_file = ".env"


settings = Settings()
