# Cross-Layer Context Engine

A comprehensive code intelligence system that understands multi-stack repositories and provides rich context for AI-assisted development, impact analysis, and code exploration.

## Architecture

```
Flutter (Mobile) ↔ React (Web) ↔ NestJS (Backend) ↔ Infra (Terraform + ArgoCD)
```

## Features

- **Multi-Language Parsing**: Dart, TypeScript, JavaScript, HCL, YAML
- **Cross-Layer Traceability**: UI action → API → Service → DB → Infra
- **Dependency Graph**: Understand relationships across all layers
- **Semantic Search**: Vector-based code search with context
- **Impact Analysis**: Know what breaks when you change code
- **Infrastructure Awareness**: Track env vars, secrets, and deployment configs
- **Smart Context Assembly**: Provide AI tools with precisely relevant code

## Use Cases

1. **AI-Assisted Coding**: Give Cursor/Copilot the right context
2. **Code Exploration**: Understand complex cross-layer flows
3. **Impact Analysis**: QA and testing support
4. **Documentation**: Auto-generate architecture docs
5. **Refactoring**: Safe large-scale changes

## Project Structure

```
code-intelligence/
├── parsers/           # Language-specific parsers
│   ├── flutter/       # Dart/Flutter parser
│   ├── react/         # React/TypeScript parser
│   ├── nestjs/        # NestJS parser
│   ├── terraform/     # HCL parser
│   └── argocd/        # Kubernetes YAML parser
├── indexer/           # Unified code index
├── graph/             # Dependency graph builder
├── embeddings/        # Vector embeddings
├── context_builder/   # Context assembly engine
├── api/               # REST API
├── tests/             # Test suite
└── utils/             # Shared utilities

demo-repo/
├── mobile/            # Flutter app
├── web/               # React app
├── backend/           # NestJS API
└── infra/             # Terraform + ArgoCD
```

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Index a repository
python -m code_intelligence index --repo ./demo-repo

# Query the system
python -m code_intelligence query "Fix login issue"

# Start API server
python -m code_intelligence serve
```

## Output Example

When you query "Fix login issue", the system provides:

```
📱 Flutter Layer:
  - LoginScreen widget (mobile/lib/screens/login_screen.dart:15)
  - API call to POST /auth/login (mobile/lib/services/auth_service.dart:42)

🌐 React Layer:
  - LoginPage component (web/src/pages/Login.tsx:20)
  - useAuth hook (web/src/hooks/useAuth.ts:10)

⚙️ Backend Layer:
  - AuthController.login (backend/src/auth/auth.controller.ts:25)
  - AuthService.validateCredentials (backend/src/auth/auth.service.ts:50)
  - LoginDto (backend/src/auth/dto/login.dto.ts:5)

🗄️ Data Layer:
  - User entity (backend/src/users/user.entity.ts:10)

☸️ Infrastructure:
  - JWT_SECRET env var (infra/argocd/auth-service-config.yaml:15)
  - Auth service deployment (infra/terraform/auth_service.tf:10)

⚠️  Impact Analysis:
  - Affects: Mobile login, Web login
  - Related APIs: 3 endpoints
  - Tests: 12 test files
```

## Phases

### Phase 1: Backend Focus (Week 1-2)
- ✅ NestJS parser
- ✅ API → Service graph
- ✅ Basic context builder

### Phase 2: Frontend Integration (Week 3-4)
- ✅ React + Flutter parsers
- ✅ Cross-layer mapping
- ✅ Vector search

### Phase 3: Infrastructure & Advanced (Week 5-6)
- ✅ Terraform + ArgoCD parsers
- ✅ Impact analysis
- ✅ Test mapping

## API Endpoints

```
POST /api/index              # Index a repository
GET  /api/query              # Query for context
GET  /api/graph              # Get dependency graph
GET  /api/impact             # Analyze change impact
GET  /api/components         # List all components
```

## Technology Stack

- **Parser**: Tree-sitter, LibCST, Esprima
- **Graph**: NetworkX (upgradable to Neo4j)
- **Vector DB**: ChromaDB, FAISS
- **API**: FastAPI
- **LLM**: OpenAI (for semantic enrichment)

## Configuration

Create `.env`:

```bash
OPENAI_API_KEY=your_key_here
CHROMA_PERSIST_DIR=./data/chroma
GRAPH_CACHE_DIR=./data/graphs
LOG_LEVEL=INFO
```

## Development

```bash
# Run tests
pytest

# Format code
black code-intelligence/

# Type checking
mypy code-intelligence/

# Lint
ruff check code-intelligence/
```

## Advanced Features

- **Test Mapping**: Gherkin → API → UI linking
- **CI/CD Integration**: Track deployment triggers
- **Feature Flags**: Config-based behavior analysis
- **Security Analysis**: Track secrets and sensitive data flows

## Contributing

This is a QE-driven code intelligence system. Contributions welcome!

## License

MIT
