# Code Intelligence System - Usage Guide

A comprehensive guide to using the Cross-Layer Context Engine for multi-stack repositories.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Installation](#installation)
3. [Command Line Interface](#command-line-interface)
4. [REST API](#rest-api)
5. [Programmatic Usage](#programmatic-usage)
6. [Integration with Cursor/AI Tools](#integration-with-cursor-ai-tools)
7. [Advanced Features](#advanced-features)

---

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Index the demo repository
python -m code_intelligence index --repo ./demo-repo

# Query for context
python -m code_intelligence query --repo ./demo-repo --query "Fix login issue"

# Start API server
python -m code_intelligence serve
```

## Installation

### Prerequisites

- Python 3.8+
- pip

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Verify Installation

```bash
python -m code_intelligence --help
```

## Command Line Interface

### 1. Index a Repository

Index your multi-stack repository to build the code intelligence database.

```bash
python -m code_intelligence index \
  --repo /path/to/your/repo \
  --output ./data/index.json
```

**What it does:**
- Parses all code files (Flutter, React, NestJS, Terraform, ArgoCD)
- Extracts components, dependencies, and relationships
- Creates a unified intermediate representation
- Saves to JSON file

**Output:**
- `./data/index.json` - Unified code index

### 2. Build Dependency Graph

Build and visualize the cross-layer dependency graph.

```bash
python -m code_intelligence graph \
  --index-file ./data/index.json \
  --output-graph ./data/graph.graphml \
  --output-viz ./data/graph.png \
  --layout spring
```

**Options:**
- `--layout`: `spring`, `kamada_kawai`, or `circular`

**Output:**
- `./data/graph.graphml` - Graph file (can be loaded in tools like Gephi)
- `./data/graph.png` - Visual representation

### 3. Query for Context

Query the system to get relevant code context for a task.

```bash
python -m code_intelligence query \
  --index-file ./data/index.json \
  --repo /path/to/your/repo \
  --query "Fix login issue" \
  --output ./data/context.txt
```

**Example queries:**
- `"Fix login issue"`
- `"How does user registration work?"`
- `"Debug authentication problems"`
- `"Add password reset functionality"`
- `"Where are API keys stored?"`

**Output:**
- `./data/context.txt` - Formatted context for AI tools
- `./data/context.json` - Raw context data

### 4. Get Execution Flow

Trace the execution flow from a component through all layers.

```bash
python -m code_intelligence flow \
  --index-file ./data/index.json \
  --repo /path/to/your/repo \
  --component LoginScreen
```

**Output:**
```
FRONTEND-MOBILE:
  - LoginScreen (screen)
    lib/screens/login_screen.dart:15
  - AuthService (service)
    lib/services/auth_service.dart:20

BACKEND:
  - AuthController (controller)
    src/auth/auth.controller.ts:10
  - AuthService (service)
    src/auth/auth.service.ts:15

DATA:
  - UserRepository (repository)
    src/users/user.repository.ts:8
```

### 5. Impact Analysis

Analyze what components would be affected by changing specific components.

```bash
python -m code_intelligence impact \
  --index-file ./data/index.json \
  --component AuthService \
  --component UserRepository
```

**Output:**
```
Impact Analysis:
Changed components: 2
Affected components: 8

Affected components:
  - LoginScreen (screen) in frontend-mobile
  - LoginPage (page) in frontend-web
  - ProfileScreen (screen) in frontend-mobile
  - AuthController (controller) in backend
  ...
```

### 6. Start API Server

Start the REST API server for programmatic access.

```bash
python -m code_intelligence serve \
  --host 0.0.0.0 \
  --port 8000 \
  --reload
```

**Access:**
- API: `http://localhost:8000`
- Interactive docs: `http://localhost:8000/docs`
- Redoc: `http://localhost:8000/redoc`

### 7. Show Statistics

View statistics about the indexed repository.

```bash
python -m code_intelligence stats \
  --index-file ./data/index.json
```

**Output:**
```
Repository Statistics

Totals:
  Components: 45
  Relationships: 67
  API Endpoints: 12
  Infrastructure: 8

By Layer:
  frontend-mobile: 12
  frontend-web: 15
  backend: 18
  ...
```

---

## REST API

### Endpoints

#### Health Check

```bash
GET /
```

#### Index Repository

```bash
POST /api/index
{
  "repo_path": "/path/to/repo"
}
```

#### Query for Context

```bash
POST /api/query
{
  "query": "Fix login issue",
  "include_tests": false,
  "max_components": 20
}
```

**Response:**
```json
{
  "query": "Fix login issue",
  "context": {
    "summary": "Context includes: 3 mobile components, 2 web components, 4 backend components",
    "layers": {
      "frontend-mobile": [...],
      "frontend-web": [...],
      "backend": [...]
    },
    "api_contracts": [...]
  },
  "formatted_context": "# Context for: Fix login issue\n..."
}
```

#### Get Component Details

```bash
GET /api/components/{component_id}?include_dependencies=true
```

#### List Components

```bash
GET /api/components?layer=backend&type=controller&limit=100
```

#### Search Components

```bash
GET /api/search?q=login&limit=20
```

#### Get Dependency Graph

```bash
GET /api/graph
```

#### Get Execution Flow

```bash
GET /api/flow/{component_id}
```

#### Impact Analysis

```bash
POST /api/impact
{
  "component_ids": ["AuthService", "UserRepository"]
}
```

#### Get API Contracts

```bash
GET /api/contracts?method=POST
```

#### System Statistics

```bash
GET /api/stats
```

### Example with cURL

```bash
# Query for context
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Fix login issue",
    "max_components": 20
  }'

# Get component details
curl http://localhost:8000/api/components/AuthController

# Search components
curl "http://localhost:8000/api/search?q=login&limit=10"
```

---

## Programmatic Usage

### Python API

```python
from code_intelligence import UnifiedIndexer, GraphBuilder, ContextAssembler

# Index repository
indexer = UnifiedIndexer("./my-repo")
index_data = indexer.index_repository()
indexer.save_index("./data/index.json")

# Build graph
graph_builder = GraphBuilder(index_data)
graph = graph_builder.build_graph()

# Create context assembler
assembler = ContextAssembler(
    "./data/index.json",
    "./my-repo",
    graph_builder
)

# Query for context
context = assembler.assemble_context("Fix login issue")

# Format for AI tools
formatted = assembler.format_for_ai(context)

print(formatted)
```

### Get Component Dependencies

```python
# Find what a component depends on
dependencies = graph_builder.find_dependencies("AuthController", depth=2)

# Find what depends on a component
dependents = graph_builder.find_dependents("AuthService", depth=3)
```

### Get Execution Flow

```python
# Get full flow from entry point
flow = assembler.get_flow_context("LoginScreen")

for layer, components in flow["flow"].items():
    print(f"{layer}:")
    for comp in components:
        print(f"  - {comp['name']} ({comp['type']})")
```

---

## Integration with Cursor/AI Tools

### Cursor Integration

The context assembler output is designed to be directly consumed by AI coding tools like Cursor.

#### Method 1: Use as Context Provider

1. Index your repository:
   ```bash
   python -m code_intelligence index --repo ./your-repo
   ```

2. Query for context before asking Cursor to make changes:
   ```bash
   python -m code_intelligence query \
     --repo ./your-repo \
     --query "Fix authentication bug" \
     --output ./cursor-context.txt
   ```

3. Include the context in your Cursor prompt:
   ```
   Use the following context to fix the authentication bug:

   [Paste contents of cursor-context.txt]

   Now fix the bug where users can't login.
   ```

#### Method 2: Run API Server

1. Start the API server:
   ```bash
   python -m code_intelligence serve
   ```

2. Configure your tool to query the API:
   ```javascript
   // Example: Fetch context from API
   const response = await fetch('http://localhost:8000/api/query', {
     method: 'POST',
     headers: { 'Content-Type': 'application/json' },
     body: JSON.stringify({
       query: 'Fix login issue',
       max_components: 20
     })
   });

   const { formatted_context } = await response.json();
   // Use formatted_context in your AI prompt
   ```

### Example Workflow

```bash
# 1. Index your repo (once)
python -m code_intelligence index --repo ./my-project

# 2. When working on a feature, get context
python -m code_intelligence query \
  --repo ./my-project \
  --query "Add password reset feature" \
  --output ./context.txt

# 3. Use context.txt in Cursor:
# - Open Cursor
# - Reference context.txt in your chat
# - Ask Cursor to implement the feature

# 4. Check impact before committing
python -m code_intelligence impact \
  --index-file ./data/index.json \
  --component PasswordResetController
```

---

## Advanced Features

### Custom Queries

The system supports various query patterns:

```bash
# Feature-based
"Implement dark mode"
"Add two-factor authentication"

# Bug-based
"Fix login timeout issue"
"Debug slow API responses"

# Exploration
"How does user authentication work?"
"Where are environment variables stored?"

# Refactoring
"Refactor authentication service"
"Extract common validation logic"
```

### Filtering Results

```python
# Filter by layer
context = assembler.assemble_context(
    "Fix login issue",
    max_components=20
)

# Only get backend components
backend_components = context["layers"]["backend"]
```

### Layer-Specific Analysis

```bash
# Analyze frontend only
python -m code_intelligence query \
  --repo ./repo \
  --query "UI bug in login screen"

# Analyze backend only
python -m code_intelligence query \
  --repo ./repo \
  --query "API endpoint performance"
```

### Graph Analysis

```python
# Find shortest path between components
path = graph_builder.find_path("LoginScreen", "UserRepository")

# Get component context with dependencies
context = graph_builder.get_component_context(
    "AuthController",
    include_deps=True
)
```

### Infrastructure Awareness

The system automatically tracks:
- Environment variables
- Secrets
- ConfigMaps
- Deployment configs
- Feature flags

```python
# Get infrastructure context
infra_components = context["infrastructure"]

for infra in infra_components:
    if infra["type"] == "k8s_secret":
        print(f"Secret: {infra['name']}")
        print(f"Keys: {infra['keys']}")
```

---

## Tips and Best Practices

### 1. Re-index After Major Changes

```bash
# After pulling new code or making major changes
python -m code_intelligence index --repo ./your-repo
```

### 2. Use Specific Queries

Better:
- "Fix email validation in registration"
- "Debug JWT token expiration"

Worse:
- "Fix bug"
- "Make it work"

### 3. Check Impact Before Refactoring

```bash
# Before refactoring AuthService
python -m code_intelligence impact \
  --index-file ./data/index.json \
  --component AuthService

# You'll see what breaks!
```

### 4. Use Flow Analysis for Complex Features

```bash
# Understand the full flow first
python -m code_intelligence flow \
  --index-file ./data/index.json \
  --repo ./your-repo \
  --component PaymentCheckoutScreen
```

### 5. API Server for CI/CD

Run the API server in your CI/CD pipeline to provide context to automated tools:

```yaml
# .github/workflows/ai-review.yml
- name: Start Code Intelligence API
  run: python -m code_intelligence serve --port 8000 &

- name: Get PR context
  run: |
    curl -X POST http://localhost:8000/api/query \
      -d '{"query": "Review changes in ${{ github.event.pull_request.title }}"}' \
      > pr-context.json
```

---

## Troubleshooting

### Index Not Found

```
Error: Index file not found
```

**Solution:** Run the index command first:
```bash
python -m code_intelligence index --repo ./your-repo
```

### Parser Errors

```
Error parsing file.ts: ...
```

**Solution:** The parser uses regex-based fallback. Check if:
- File is syntactically valid
- File encoding is UTF-8
- File paths don't contain special characters

### API Server Won't Start

```
Address already in use
```

**Solution:** Change the port:
```bash
python -m code_intelligence serve --port 8001
```

### Empty Context

```
Context includes: 0 components
```

**Solution:**
- Check if your query matches component names
- Try more generic queries
- Verify the index contains your components:
  ```bash
  python -m code_intelligence stats --index-file ./data/index.json
  ```

---

## Support

For issues, questions, or contributions:
- Create an issue on GitHub
- Check the example_usage.py for reference
- Review the demo-repo for expected structure

---

## Next Steps

1. **Index your real repository**
2. **Try example queries**
3. **Integrate with your AI tool**
4. **Set up the API server**
5. **Customize for your needs**

Happy coding! 🚀
