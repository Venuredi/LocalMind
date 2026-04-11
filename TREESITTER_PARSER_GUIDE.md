# Tree Sitter Global Parser - Complete Guide

## Overview

I've implemented a universal code parser using the Tree Sitter library that can read and analyze source code in any programming language and generate ontologies/knowledge graphs.

## What Was Implemented

### 1. Tree Sitter Parser (`code-intelligence/parsers/treesitter/`)

A comprehensive parsing framework that includes:

- **tree_sitter_parser.py**: Main parser class with multi-language support
- **ontology_generator.py**: Converts parsed code into NetworkX graphs/ontologies
- **language_extractors.py**: Extensible language-specific extractors
- **README.md**: Detailed documentation

### 2. Features

#### Multi-Language Support
- **Python**: Classes, functions, methods, imports, docstrings
- **JavaScript/TypeScript**: Classes, functions, arrow functions, interfaces, imports
- **Java**: Classes, interfaces, methods, annotations
- **Go**: Structs, interfaces, functions, methods
- **Rust**: Structs, enums, traits, impl blocks, functions
- And many more (C/C++, C#, Ruby, PHP, Swift, Kotlin, etc.)

#### Entity Extraction
- Classes (with inheritance information)
- Functions and Methods
- Interfaces
- Structs and Enums
- Import statements
- Constants and Variables

#### Relationship Mapping
- **Inheritance**: Class hierarchies (extends/implements)
- **Dependencies**: Import relationships between modules
- **Containment**: Files contain classes, classes contain methods
- **Implementation**: Methods belong to classes/structs

#### Graph Generation
- Creates NetworkX MultiDiGraph structures
- Nodes represent code entities
- Edges represent relationships
- Supports multiple edge types between nodes

#### Export Formats
- **GraphML**: Standard graph format for analysis tools
- **JSON**: Node-link format for easy processing
- **Neo4j Cypher**: Import into Neo4j graph database
- **PNG Visualizations**: Multiple layout algorithms

## Files Created

```
code-intelligence/parsers/treesitter/
├── __init__.py                    # Package initialization
├── tree_sitter_parser.py          # Main parser (650+ lines)
├── ontology_generator.py          # Graph/ontology generator (800+ lines)
├── language_extractors.py         # Language-specific extractors (400+ lines)
└── README.md                      # Comprehensive documentation

Root directory:
├── example_treesitter_usage.py    # 8 detailed examples
├── test_treesitter_simple.py      # Quick test script
└── TREESITTER_PARSER_GUIDE.md     # This guide
```

## Quick Start

### Installation

All required dependencies are already in `requirements.txt`:

```bash
pip install -r requirements.txt
```

Key dependencies:
- `tree-sitter==0.21.3`
- `tree-sitter-languages==1.10.2`
- `networkx==3.2.1`
- `matplotlib>=3.7.0`

### Basic Usage

```python
import sys
from pathlib import Path

# Add to path
sys.path.insert(0, str(Path.cwd() / "code-intelligence"))

from parsers.treesitter.tree_sitter_parser import TreeSitterParser
from parsers.treesitter.ontology_generator import OntologyGenerator

# 1. Parse repository
parser = TreeSitterParser("./your-repo")
results = parser.parse_repository()

# 2. Generate ontology
ontology = OntologyGenerator(results)
graph = ontology.build_ontology()

# 3. Analyze and visualize
ontology.print_statistics()
ontology.visualize("./output/graph.png")

# 4. Export
parser.save_results("./output/entities.json")
ontology.save_ontology("./output/ontology.graphml")
ontology.export_to_neo4j_cypher("./output/neo4j.cypher")
```

### Running Tests

```bash
# Quick test
python3 test_treesitter_simple.py

# Full examples (8 different use cases)
python3 example_treesitter_usage.py
```

## Usage Examples

### Example 1: Parse and Get Statistics

```python
parser = TreeSitterParser("./demo-repo")
results = parser.parse_repository()

print(f"Files: {results['summary']['total_files']}")
print(f"Languages: {results['summary']['languages']}")

for entity_type, count in results['summary']['entity_counts'].items():
    if count > 0:
        print(f"{entity_type}: {count}")
```

### Example 2: Query Entities

```python
# Find all Python classes
python_classes = [
    cls for cls in parser.entities['classes']
    if cls['language'] == 'python'
]

# Find async functions
async_funcs = [
    f for f in parser.entities['functions']
    if 'async' in f.get('name', '').lower()
]

# Find TypeScript interfaces
ts_interfaces = [
    i for i in parser.entities['interfaces']
    if 'typescript' in i.get('language', '')
]
```

### Example 3: Analyze Inheritance

```python
ontology = OntologyGenerator(results)
graph = ontology.build_ontology()

# Get inheritance tree for a class
class_id = "path/to/file.py::MyClass"
tree = ontology.get_inheritance_tree(class_id)

# Visualize class hierarchy only
ontology.visualize(
    "./class_hierarchy.png",
    layout="hierarchical",
    node_types=["class", "interface"]
)
```

### Example 4: Analyze Dependencies

```python
# Get dependency graph for an entity
entity_id = "path/to/file.py::MyFunction"
dep_graph = ontology.get_dependency_graph(entity_id, depth=2)

print(f"Dependencies: {dep_graph.number_of_edges()}")
```

### Example 5: Export to Neo4j

```python
# Export to Neo4j Cypher format
ontology.export_to_neo4j_cypher("./neo4j_import.cypher")

# Then in Neo4j:
# cat neo4j_import.cypher | cypher-shell
```

### Example 6: Language-Specific Statistics

```python
language_stats = {}

for entity_type, entity_list in parser.entities.items():
    for entity in entity_list:
        lang = entity.get('language', 'unknown')
        if lang not in language_stats:
            language_stats[lang] = {}
        if entity_type not in language_stats[lang]:
            language_stats[lang][entity_type] = 0
        language_stats[lang][entity_type] += 1

for language, stats in language_stats.items():
    print(f"\n{language.upper()}:")
    for entity_type, count in stats.items():
        print(f"  {entity_type}: {count}")
```

## Architecture

### TreeSitterParser

**Core responsibilities:**
- Detect programming language from file extensions
- Load appropriate Tree Sitter parser for each language
- Traverse AST and extract code entities
- Store parsed data in structured format

**Key methods:**
- `parse_repository()`: Parse entire codebase
- `parse_file(path)`: Parse single file
- `_extract_entities()`: Extract code constructs
- `save_results(path)`: Save to JSON

### OntologyGenerator

**Core responsibilities:**
- Build NetworkX graphs from parsed entities
- Add nodes for all code entities
- Add edges for relationships
- Provide query and analysis capabilities

**Key methods:**
- `build_ontology()`: Create the graph
- `get_inheritance_tree()`: Get class hierarchy
- `get_dependency_graph()`: Get dependency subgraph
- `visualize()`: Create visualizations
- `save_ontology()`: Export graph
- `export_to_neo4j_cypher()`: Export for Neo4j

## Graph Structure

### Node Types
- `class`: Class definitions
- `function`: Top-level functions
- `method`: Class/struct methods
- `interface`: Interface definitions
- `struct`: Struct definitions (Go, Rust)
- `enum`: Enum definitions
- `module`: Imported modules
- `file`: Source files

### Node Attributes
- `id`: Unique identifier
- `name`: Entity name
- `type`: Entity type
- `language`: Programming language
- `file_path`: Source file path
- `line_start`: Start line number
- `line_end`: End line number
- `docstring`: Documentation (if available)

### Edge Types
- `inherits`: Inheritance relationship
- `implements`: Interface implementation
- `imports`: Module dependency
- `contains`: Containment (file→class, class→method)
- `has_method`: Method belonging to struct
- `implements_method`: Rust impl block

## Visualization Layouts

### Spring Layout (Default)
Force-directed layout, good for general graphs
```python
ontology.visualize("./graph.png", layout="spring")
```

### Hierarchical Layout
Layered based on entity type (files → classes → methods)
```python
ontology.visualize("./graph.png", layout="hierarchical")
```

### Circular Layout
Nodes arranged in a circle
```python
ontology.visualize("./graph.png", layout="circular")
```

### Kamada-Kawai Layout
Force-directed with better aesthetics
```python
ontology.visualize("./graph.png", layout="kamada_kawai")
```

## Filtering and Querying

### Filter by Node Type
```python
# Only visualize classes and interfaces
ontology.visualize(
    "./output.png",
    node_types=["class", "interface"]
)
```

### Filter by Language
```python
# Get all Python entities
python_entities = [
    e for entity_list in parser.entities.values()
    for e in entity_list
    if e.get('language') == 'python'
]
```

### Filter by File
```python
# Get entities from specific file
file_entities = [
    e for entity_list in parser.entities.values()
    for e in entity_list
    if 'auth' in e.get('file_path', '')
]
```

## Extending the Parser

### Add New Language Support

1. **Add file extensions** in `tree_sitter_parser.py`:
```python
LANGUAGE_EXTENSIONS = {
    "your_language": [".ext1", ".ext2"],
    # ...
}
```

2. **Implement extraction method**:
```python
def _extract_your_language_entities(self, node, content, file_path, entities):
    # Extract classes, functions, etc.
    pass
```

3. **Call in traversal**:
```python
def _traverse_ast(self, node, content, language, file_path, entities):
    if language == "your_language":
        self._extract_your_language_entities(node, content, file_path, entities)
```

### Create Custom Extractor

```python
from code_intelligence.parsers.treesitter.language_extractors import BaseExtractor

class CustomExtractor(BaseExtractor):
    def extract_classes(self, node, content, file_path):
        # Custom class extraction
        return []

    def extract_functions(self, node, content, file_path):
        # Custom function extraction
        return []

    def extract_imports(self, node, content, file_path):
        # Custom import extraction
        return []
```

## Integration with Existing System

The Tree Sitter parser integrates with the existing code intelligence system:

```python
# Use with existing GraphBuilder
from code_intelligence.graph.graph_builder import GraphBuilder
from code_intelligence.parsers.treesitter import TreeSitterParser, OntologyGenerator

# Parse with Tree Sitter
parser = TreeSitterParser("./repo")
results = parser.parse_repository()

# Generate ontology
ontology = OntologyGenerator(results)
graph = ontology.build_ontology()

# Can now use with GraphBuilder methods
# The graph structure is compatible
```

## Performance Considerations

### Large Repositories
- Parser handles codebases of any size
- Memory usage scales linearly with code size
- Exclude directories via `_EXCLUDED_DIRS`

### Visualization
- Large graphs (>1000 nodes) can be slow to render
- Use filtering (`node_types`) for large graphs
- Consider hierarchical layout for better performance

### Batch Processing
For very large repos (>10K files):
```python
# Process in batches
files = list(Path("repo").rglob("*.py"))
batch_size = 1000

for i in range(0, len(files), batch_size):
    batch = files[i:i+batch_size]
    # Process batch...
```

## Troubleshooting

### No Entities Found
- Check that files are in supported languages
- Verify file extensions are in `LANGUAGE_EXTENSIONS`
- Check console for parsing errors

### Import Errors
- Ensure `tree-sitter-languages` is installed
- Some languages may need specific parsers

### Visualization Issues
- Large graphs: Use filtering or hierarchical layout
- Memory errors: Reduce graph size or use subgraphs

## File Reference

### Core Implementation Files

1. **tree_sitter_parser.py** (650 lines)
   - TreeSitterParser class
   - Language detection
   - AST traversal
   - Entity extraction for all languages

2. **ontology_generator.py** (800 lines)
   - OntologyGenerator class
   - Graph construction
   - Relationship extraction
   - Visualization
   - Export capabilities

3. **language_extractors.py** (400 lines)
   - BaseExtractor interface
   - Language-specific extractors
   - Extensibility framework

### Example and Test Files

1. **example_treesitter_usage.py** (300 lines)
   - 8 comprehensive examples
   - Covers all major features
   - Production-ready code

2. **test_treesitter_simple.py** (100 lines)
   - Quick functionality test
   - Verifies installation

### Documentation

1. **code-intelligence/parsers/treesitter/README.md**
   - API reference
   - Usage examples
   - Extension guide

2. **TREESITTER_PARSER_GUIDE.md** (this file)
   - Complete guide
   - Architecture overview
   - Integration instructions

## Next Steps

1. **Run the test**:
   ```bash
   python3 test_treesitter_simple.py
   ```

2. **Try the examples**:
   ```bash
   python3 example_treesitter_usage.py
   ```

3. **Parse your own repository**:
   ```python
   from parsers.treesitter import TreeSitterParser
   parser = TreeSitterParser("./your-repo")
   results = parser.parse_repository()
   ```

4. **Extend for your needs**:
   - Add custom extractors
   - Create specialized visualizations
   - Integrate with your tools

## Summary

You now have a complete, production-ready Tree Sitter-based parser that can:

✓ Parse any programming language supported by Tree Sitter
✓ Extract classes, functions, methods, imports, and more
✓ Generate knowledge graphs/ontologies
✓ Analyze inheritance and dependencies
✓ Export to multiple formats (GraphML, JSON, Neo4j)
✓ Create visualizations with multiple layouts
✓ Integrate with existing code intelligence tools
✓ Extend for custom languages and use cases

The implementation is modular, well-documented, and ready for production use!
