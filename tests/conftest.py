"""
Pytest configuration and fixtures.
Mocks database connections so tests run without real Neo4j/PostgreSQL.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.fixture(autouse=True)
def mock_databases():
    """
    Mock all database connections so tests run without real Neo4j/PostgreSQL.
    Applied automatically to every test.
    """
    mock_engine = MagicMock()
    mock_db_session = MagicMock()
    mock_session_factory = MagicMock(return_value=mock_db_session)

    # Mock Neo4j driver and session
    mock_neo4j_session = AsyncMock()
    mock_neo4j_session.run = AsyncMock()
    mock_neo4j_driver = AsyncMock()
    mock_neo4j_driver.session = MagicMock(return_value=AsyncMock(
        __aenter__=AsyncMock(return_value=mock_neo4j_session),
        __aexit__=AsyncMock(return_value=False),
    ))

    with patch("app.db.postgres.get_engine", return_value=mock_engine), \
         patch("app.db.postgres.get_session_local", return_value=mock_session_factory), \
         patch("app.db.neo4j.neo4j_connection.connect", new_callable=AsyncMock), \
         patch("app.db.neo4j.neo4j_connection.initialize_schema", new_callable=AsyncMock), \
         patch("app.db.neo4j.neo4j_connection.disconnect", new_callable=AsyncMock):
        yield
