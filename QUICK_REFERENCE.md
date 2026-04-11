# Quick Reference Card

## Setup Verification

### Check All Dependencies
```bash
python3 check_setup.py
```

### Quick Test
```bash
python3 test_treesitter_simple.py
```

---

## Requirements to Prompt Feature (NEW!)

### Generate AI-Ready Prompts

```python
from parsers.treesitter import TreeSitterParser, PromptGenerator

# Parse codebase
parser = TreeSitterParser("./your-repo")
results = parser.parse_repository()

# Generate prompt
prompt_gen = PromptGenerator(results, "./your-repo")
prompt = prompt_gen.generate_prompt(
    requirement="Add user profile editing feature",
    context_type="feature",
    constraints=["Use TypeScript", "Follow React hooks"]
)

# Save and use with AI
prompt_gen.save_prompt(prompt, "./prompt.md")
```

### Context Types
- `feature` - New functionality
- `bugfix` - Fix issues
- `refactor` - Improve code
- `test` - Write tests

### Batch Generation
```python
requirements = [
    {"requirement": "Add dark mode", "context_type": "feature"},
    {"requirement": "Fix login bug", "context_type": "bugfix"}
]
files = prompt_gen.generate_batch_prompts(requirements, "./prompts")
```

### Run Examples
```bash
python3 example_prompt_generation.py
```

---

## Tree Sitter Parser

### Basic Usage

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / "code-intelligence"))

from parsers.treesitter import TreeSitterParser, OntologyGenerator

# Parse repository
parser = TreeSitterParser("./your-repo")
results = parser.parse_repository()

# Generate ontology
ontology = OntologyGenerator(results)
graph = ontology.build_ontology()

# Analyze
ontology.print_statistics()
```

### Save Results

```python
# Save parsed data
parser.save_results("./output/data.json")

# Save graph
ontology.save_ontology("./output/graph.graphml")
ontology.save_ontology("./output/graph.json", format="json")

# Export to Neo4j
ontology.export_to_neo4j_cypher("./output/neo4j.cypher")
```

### Visualize

```python
# Complete graph
ontology.visualize("./output/complete.png")

# Only classes
ontology.visualize(
    "./output/classes.png",
    node_types=["class", "interface"]
)

# Different layouts
ontology.visualize("./output/graph.png", layout="hierarchical")
ontology.visualize("./output/graph.png", layout="spring")
ontology.visualize("./output/graph.png", layout="circular")
```

### Query Entities

```python
# Python classes
python_classes = [
    c for c in parser.entities['classes']
    if c['language'] == 'python'
]

# Async functions
async_funcs = [
    f for f in parser.entities['functions']
    if 'async' in f.get('name', '')
]

# TypeScript interfaces
interfaces = [
    i for i in parser.entities['interfaces']
    if 'typescript' in i.get('language', '')
]
```

### Analyze Relationships

```python
# Inheritance tree
tree = ontology.get_inheritance_tree("file.py::MyClass")

# Dependency graph
deps = ontology.get_dependency_graph("file.py::MyFunc", depth=2)

# Statistics
stats = ontology.get_statistics()
ontology.print_statistics()
```

---

## Code Intelligence System

### Index Repository

```bash
python -m code_intelligence index --repo ./demo-repo --output ./data/index.json
```

### Build Graph

```bash
python -m code_intelligence graph \
    --index-file ./data/index.json \
    --output-graph ./data/graph.graphml \
    --output-viz ./data/graph.png
```

### Query Context

```bash
python -m code_intelligence query \
    --index-file ./data/index.json \
    --repo ./demo-repo \
    --query "Fix login issue" \
    --output ./data/context.txt
```

### Get Flow

```bash
python -m code_intelligence flow \
    --index-file ./data/index.json \
    --repo ./demo-repo \
    --component "LoginScreen"
```

### Impact Analysis

```bash
python -m code_intelligence impact \
    --index-file ./data/index.json \
    --component "AuthController" \
    --component "UserService"
```

### Statistics

```bash
python -m code_intelligence stats --index-file ./data/index.json
```

### Start API Server

```bash
python -m code_intelligence serve --port 8000 --reload
```

API docs: http://localhost:8000/docs

---

## Supported Languages

✓ Python • JavaScript • TypeScript • Java • Go • Rust
✓ C/C++ • C# • Ruby • PHP • Kotlin

---

## File Locations

| File | Purpose |
|------|---------|
| `check_setup.py` | Verify dependencies |
| `test_treesitter_simple.py` | Quick test |
| `example_treesitter_usage.py` | Full examples |
| `TREESITTER_PARSER_GUIDE.md` | Complete guide |
| `SETUP_STATUS.md` | Setup report |
| `code-intelligence/parsers/treesitter/README.md` | API docs |

---

## Common Commands

### Check Setup
```bash
python3 check_setup.py
```

### Run Tests
```bash
python3 test_treesitter_simple.py
```

### Run Examples
```bash
python3 example_treesitter_usage.py
```

### Parse Directory
```python
from parsers.treesitter import TreeSitterParser
parser = TreeSitterParser("./path")
parser.parse_repository()
```

---

## Visualization Layouts

- **spring** - Force-directed (default)
- **hierarchical** - Layered by type
- **circular** - Circular arrangement
- **kamada_kawai** - Force-directed with better aesthetics

---

## Export Formats

- **GraphML** - `.graphml` - Standard graph format
- **JSON** - `.json` - Node-link format
- **Neo4j** - `.cypher` - Database import
- **PNG** - `.png` - Visualization

---

## Tips

### Performance
- Exclude directories in `_EXCLUDED_DIRS`
- Use filtering for large graphs
- Process very large repos in batches

### Debugging
- Check `check_setup.py` first
- Verify file extensions in `LANGUAGE_EXTENSIONS`
- Use `test_treesitter_simple.py` to isolate issues

### Customization
- Add languages in `tree_sitter_parser.py`
- Create custom extractors in `language_extractors.py`
- Extend ontology in `ontology_generator.py`

---

## Getting Help

1. Read `TREESITTER_PARSER_GUIDE.md`
2. Check `SETUP_STATUS.md`
3. See examples in `example_treesitter_usage.py`
4. Review API docs in `code-intelligence/parsers/treesitter/README.md`
