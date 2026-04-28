# Knowledge-Graph Query API

A comprehensive REST API built with FastAPI, Neo4j, and PostgreSQL for managing knowledge graphs with advanced traceability, gap detection, and impact analysis capabilities.

## Features

- **Graph Schema**: 6+ node types (Document, Framework, Concept, Technology, Impact, Citation) with 6+ relationship types
- **Constraints & Indexes**: Uniqueness constraints, existence constraints, and composite indexes tuned for query performance
- **Idempotent Ingestion**: Document corpus and framework catalog ingestion with automatic citation extraction and deduplication
- **Query Library**: 
  - Forward traceability (downstream dependencies)
  - Backward traceability (upstream dependencies)
  - Framework coverage analysis
  - Gap detection between frameworks and requirements
  - Impact analysis for change management
- **FastAPI REST Service**: Token-based authentication and OpenAPI documentation
- **PostgreSQL Audit Logging**: Complete audit trail of all operations
- **Multi-Tenancy**: Tenant-scoped schema constraints and data isolation

## Architecture

```
knowledge-graph-api/
├── app/
│   ├── core/
│   │   ├── config.py           # Settings and configuration
│   │   └── security.py          # JWT token handling
│   ├── db/
│   │   ├── neo4j.py            # Neo4j connection and schema
│   │   └── postgres.py          # PostgreSQL ORM models
│   ├── schemas/
│   │   └── models.py            # Pydantic data models
│   ├── services/
│   │   ├── ingestion.py         # Document ingestion pipeline
│   │   ├── query.py             # Cypher query library
│   │   └── audit.py             # Audit logging service
│   └── routers/
│       ├── auth.py              # Authentication endpoints
│       ├── documents.py         # Document ingestion endpoints
│       ├── queries.py           # Query analysis endpoints
│       └── audit.py             # Audit log endpoints
├── tests/
├── main.py                      # FastAPI application entry point
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment variables template
└── README.md
```

## Prerequisites

- Python 3.9+
- Neo4j 5.x
- PostgreSQL 12+
- pip

## Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/knowledge-graph-api.git
cd knowledge-graph-api
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your database credentials
```

5. **Set up Neo4j**
```bash
# Using Docker
docker run -d \
  --name neo4j \
  -p 7474:7474 \
  -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  neo4j:5.14-community
```

6. **Set up PostgreSQL**
```bash
# Using Docker
docker run -d \
  --name postgres \
  -e POSTGRES_DB=knowledge_graph_audit \
  -e POSTGRES_PASSWORD=password \
  -p 5432:5432 \
  postgres:15
```

## Running the Application

```bash
python main.py
```

The API will be available at `http://localhost:8000`

- **API Documentation**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Authentication

### Get Access Token

```bash
curl -X POST "http://localhost:8000/auth/token" \
  -H "Content-Type: application/json" \
  -d '{"tenant_id": "tenant-1", "user_id": "user-1"}'
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Use Token in Requests

```bash
curl -X POST "http://localhost:8000/documents/ingest" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Example Document",
    "content": "Document content here [cite:ref-1]",
    "source": "example-source",
    "metadata": {"author": "John Doe"}
  }'
```

## API Endpoints

### Authentication
- `POST /auth/token` - Get access token

### Documents
- `POST /documents/ingest` - Ingest single document
- `POST /documents/ingest-batch` - Batch ingest documents

### Queries
- `GET /queries/forward-traceability/{source_id}` - Forward traceability analysis
- `GET /queries/backward-traceability/{target_id}` - Backward traceability analysis
- `GET /queries/framework-coverage/{framework_id}` - Framework coverage analysis
- `GET /queries/gap-detection/{framework_id}` - Gap detection analysis
- `GET /queries/impact-analysis/{node_id}` - Impact analysis

### Audit Logs
- `GET /audit/logs` - Get tenant audit logs
- `GET /audit/logs/{user_id}` - Get user-specific audit logs

### Health
- `GET /health` - Health check
- `GET /` - Root endpoint

## Graph Schema

### Node Types

1. **Document** - Source documents and requirements
   - Properties: id, tenant_id, title, content, source, metadata, created_at

2. **Framework** - Technology frameworks and standards
   - Properties: id, tenant_id, name, category, description, version, created_at

3. **Concept** - Requirements and concepts
   - Properties: id, tenant_id, name, type, description

4. **Technology** - Technology stack components
   - Properties: id, tenant_id, name, category, description

5. **Impact** - Impact analysis results
   - Properties: id, tenant_id, source_id, impact_score, created_at

6. **Citation** - Document citations and references
   - Properties: id, tenant_id, source_id, target_id, confidence_score, created_at

### Relationship Types

- `COVERS` - Framework covers a concept
- `IMPLEMENTS` - Framework implements a technology
- `REQUIRES` - Concept requires a technology
- `RELATED_TO` - Semantic relationship between nodes
- `DEPENDS_ON` - Dependency relationship
- `REFERENCES` - Citation reference
- `IMPACTS` - Impact relationship

## Multi-Tenancy

All operations are tenant-scoped. Multi-tenancy is enforced through:

1. **Schema constraints**: All nodes include `tenant_id` field
2. **Query filtering**: All queries filter by `tenant_id` from JWT token
3. **Audit isolation**: Audit logs are tenant-specific
4. **Data isolation**: No cross-tenant data access possible

## Example Usage

### 1. Get Token
```bash
TOKEN=$(curl -s -X POST "http://localhost:8000/auth/token" \
  -H "Content-Type: application/json" \
  -d '{"tenant_id": "acme-corp", "user_id": "john@acme.com"}' \
  | jq -r '.access_token')
```

### 2. Ingest Document
```bash
curl -X POST "http://localhost:8000/documents/ingest" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "System Architecture",
    "content": "Our system uses microservices [cite:kubernetes] with event-driven [cite:kafka] communication",
    "source": "internal-docs",
    "metadata": {"version": "2.0"}
  }'
```

### 3. Analyze Forward Traceability
```bash
curl -X GET "http://localhost:8000/queries/forward-traceability/doc-123?max_depth=3" \
  -H "Authorization: Bearer $TOKEN"
```

### 4. Detect Gaps
```bash
curl -X GET "http://localhost:8000/queries/gap-detection/framework-456" \
  -H "Authorization: Bearer $TOKEN"
```

### 5. Check Audit Logs
```bash
curl -X GET "http://localhost:8000/audit/logs" \
  -H "Authorization: Bearer $TOKEN"
```

## Development

### Run Tests
```bash
pytest tests/ -v
```

### Code Style
```bash
# Format code
black app/

# Lint
flake8 app/
```

## Performance Optimization

The graph schema includes composite indexes on frequently queried combinations:
- `(tenant_id, created_at)` on Document nodes
- `(tenant_id, category)` on Framework nodes
- `(tenant_id, type)` on Concept nodes

These indexes optimize the query patterns for forward/backward traceability and gap detection.

## Security Considerations

- **JWT Tokens**: Short-lived tokens with configurable expiration
- **Tenant Isolation**: All data strictly scoped by tenant_id
- **Audit Trail**: Complete audit log of all operations
- **CORS**: Configured for security
- **Environment Variables**: Sensitive configuration via .env

## Deployment

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
```

### Kubernetes

Example deployment manifest available in `k8s/deployment.yaml`

### Environment Variables

Required for production:
- `NEO4J_URI` - Neo4j cluster URI
- `NEO4J_USER` - Neo4j username
- `NEO4J_PASSWORD` - Neo4j password
- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - JWT signing key (generate with `openssl rand -hex 32`)
- `DEBUG` - Set to False

## License

MIT License

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

## Support

For issues and questions, please open a GitHub issue.

## Roadmap

- [ ] Batch query optimization
- [ ] GraphQL endpoint
- [ ] Real-time graph updates via WebSocket
- [ ] Advanced filtering and search
- [ ] Graph visualization endpoints
- [ ] Bulk data export
- [ ] Custom relationship definitions
