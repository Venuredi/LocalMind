# Tree Sitter Global Parser

A universal code parser using Tree Sitter that can analyze source code in any programming language and generate ontologies/knowledge graphs.

## Features

- **Multi-language Support**: Parse code in Python, JavaScript, TypeScript, Java, Go, Rust, C/C++, and many more
- **AST-based Parsing**: Uses Tree Sitter for accurate, syntax-aware parsing
- **Entity Extraction**: Automatically extracts classes, functions, methods, imports, interfaces, structs, enums, etc.
- **Relationship Mapping**: Identifies inheritance, dependencies, imports, and containment relationships
- **Graph Generation**: Creates NetworkX graphs representing code structure and relationships
- **Multiple Export Formats**: Export to GraphML, JSON, Neo4j Cypher, and visualizations
- **Extensible**: Easy to add custom extractors for specific languages or frameworks

## Installation

The required dependencies are already in `requirements.txt`:

```bash
pip install tree-sitter==0.21.3
pip install tree-sitter-languages==1.10.2
pip install networkx==3.2.1
pip install matplotlib>=3.7.0
```

## Quick Start

```python
from code_intelligence.parsers.treesitter import TreeSitterParser, OntologyGenerator

# 1. Parse a repository
parser = TreeSitterParser("./path/to/your/repo")
results = parser.parse_repository()

# 2. Generate ontology/graph
ontology = OntologyGenerator(results)
graph = ontology.build_ontology()

# 3. Visualize
ontology.visualize("./output/graph.png")

# 4. Save results
parser.save_results("./output/parsed_data.json")
ontology.save_ontology("./output/ontology.graphml")
```

## Supported Languages

The parser automatically detects and parses the following languages:

- **Python** (`.py`)
- **JavaScript** (`.js`, `.mjs`, `.cjs`)
- **TypeScript** (`.ts`, `.tsx`)
- **Java** (`.java`)
- **Go** (`.go`)
- **Rust** (`.rs`)
- **C/C++** (`.c`, `.cpp`, `.h`, `.hpp`)
- **C#** (`.cs`)
- **Ruby** (`.rb`)
- **PHP** (`.php`)
- **Swift** (`.swift`)
- **Kotlin** (`.kt`)
- **Scala** (`.scala`)
- And more...

## What Gets Extracted

### Entities

- **Classes**: Name, base classes, methods, properties
- **Functions**: Name, parameters, docstrings
- **Methods**: Name, parameters, parent class/struct
- **Imports**: Modules, imported names
- **Interfaces**: Name, methods (TypeScript, Java, Go)
- **Structs**: Name, fields (Go, Rust)
- **Enums**: Name, variants (Rust, Java)

### Relationships

- **Inheritance**: Class extends/inherits from other classes
- **Implementation**: Class implements interfaces
- **Dependencies**: Import relationships between modules
- **Containment**: File contains classes, classes contain methods
- **Association**: Method belongs to class/struct

## Examples

### Example 1: Parse and Analyze a Repository

```python
from code_intelligence.parsers.treesitter import TreeSitterParser

parser = TreeSitterParser("./my-project")
results = parser.parse_repository()

print(f"Parsed {results['summary']['total_files']} files")
print(f"Languages: {results['summary']['languages']}")
print(f"Found {len(results['entities']['classes'])} classes")
print(f"Found {len(results['entities']['functions'])} functions")
```

### Example 2: Generate and Visualize Ontology

```python
from code_intelligence.parsers.treesitter import TreeSitterParser, OntologyGenerator

# Parse
parser = TreeSitterParser("./my-project")
results = parser.parse_repository()

# Generate ontology
ontology = OntologyGenerator(results)
graph = ontology.build_ontology()

# Visualize complete graph
ontology.visualize("./complete_graph.png", layout="spring")

# Visualize only classes
ontology.visualize(
    "./class_hierarchy.png",
    layout="hierarchical",
    node_types=["class", "interface"]
)

# Print statistics
ontology.print_statistics()
```

### Example 3: Analyze Inheritance

```python
# Get inheritance tree for a class
class_id = "path/to/file.py::MyClass"
tree = ontology.get_inheritance_tree(class_id)
print(tree)
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

# Then import into Neo4j:
# cat neo4j_import.cypher | cypher-shell
```

### Example 6: Query Specific Entities

```python
# Find all Python classes
python_classes = [
    cls for cls in parser.entities["classes"]
    if cls["language"] == "python"
]

# Find all async functions
async_funcs = [
    func for func in parser.entities["functions"]
    if "async" in func["name"]
]

# Find all TypeScript interfaces
ts_interfaces = [
    iface for iface in parser.entities["interfaces"]
    if "typescript" in iface["language"]
]
```

## Graph Structure

### Nodes

Each node represents a code entity with attributes:

- `id`: Unique identifier (e.g., "file.py::ClassName")
- `name`: Entity name
- `type`: Entity type (class, function, method, etc.)
- `language`: Programming language
- `file_path`: Relative path to source file
- `line_start`: Starting line number
- `line_end`: Ending line number

### Edges

Edges represent relationships:

- **inherits**: Class inherits from another class
- **implements**: Class implements an interface
- **imports**: Module/file imports another module
- **contains**: File contains class, class contains method
- **has_method**: Struct/class has a method

## Visualization Options

### Layouts

- `spring`: Force-directed layout (default)
- `kamada_kawai`: Force-directed with better aesthetics
- `circular`: Nodes arranged in a circle
- `hierarchical`: Layered based on entity type

### Filtering

You can filter visualizations by node type:

```python
# Only show classes and interfaces
ontology.visualize(
    "./output.png",
    node_types=["class", "interface"]
)
```

## Export Formats

### GraphML

Standard graph format, can be imported into graph analysis tools:

```python
ontology.save_ontology("./graph.graphml", format="graphml")
```

### JSON

Node-link format for easy processing:

```python
ontology.save_ontology("./graph.json", format="json")
```

### Neo4j Cypher

Import into Neo4j graph database:

```python
ontology.export_to_neo4j_cypher("./import.cypher")
```

## Advanced Usage

### Custom Language Extractors

You can extend the parser with custom extractors:

```python
from code_intelligence.parsers.treesitter.language_extractors import BaseExtractor

class MyCustomExtractor(BaseExtractor):
    def extract_classes(self, node, content, file_path):
        # Custom extraction logic
        return []

    def extract_functions(self, node, content, file_path):
        # Custom extraction logic
        return []

    def extract_imports(self, node, content, file_path):
        # Custom extraction logic
        return []
```

### Filtering During Parsing

Exclude specific directories:

```python
# Edit the _EXCLUDED_DIRS set in tree_sitter_parser.py
_EXCLUDED_DIRS.add("my_custom_dir")
```

## Performance Tips

1. **Large Repositories**: The parser handles large codebases efficiently, but visualization can be slow. Use `node_types` filtering.

2. **Memory**: For very large repositories (>10K files), consider parsing in batches.

3. **Visualization**: For large graphs, use hierarchical layout or filter by node type.

## Integration with Existing Tools

The Tree Sitter parser integrates seamlessly with the existing code intelligence system:

```python
from code_intelligence.parsers import TreeSitterParser, OntologyGenerator
from code_intelligence.graph import GraphBuilder

# Parse with Tree Sitter
ts_parser = TreeSitterParser("./repo")
ts_results = ts_parser.parse_repository()

# Generate ontology
ontology = OntologyGenerator(ts_results)
graph = ontology.build_ontology()

# You can now use this graph with the existing GraphBuilder tools
```

## Troubleshooting

### Language Not Supported

If you get a warning about an unsupported language, make sure the language is in the `LANGUAGE_EXTENSIONS` mapping in `tree_sitter_parser.py`.

### Parsing Errors

Individual file parsing errors are logged but don't stop the overall process. Check the console output for details.

### Empty Results

Make sure the repository path is correct and contains source files in supported languages.

## Examples Directory

See `example_treesitter_usage.py` in the root directory for comprehensive examples covering all features.

## API Reference

### TreeSitterParser

```python
TreeSitterParser(repo_path: str)
```

**Methods:**

- `parse_file(file_path: Path) -> Dict`: Parse a single file
- `parse_repository() -> Dict`: Parse entire repository
- `save_results(output_path: str)`: Save parsing results to JSON

### OntologyGenerator

```python
OntologyGenerator(parsed_data: Dict)
```

**Methods:**

- `build_ontology() -> nx.MultiDiGraph`: Build the ontology graph
- `get_inheritance_tree(class_id: str) -> Dict`: Get inheritance tree
- `get_dependency_graph(entity_id: str, depth: int) -> nx.DiGraph`: Get dependency subgraph
- `visualize(output_path: str, layout: str, figsize: Tuple, node_types: List)`: Create visualization
- `save_ontology(output_path: str, format: str)`: Save graph to file
- `export_to_neo4j_cypher(output_path: str)`: Export as Neo4j Cypher
- `print_statistics()`: Print graph statistics
- `get_statistics() -> Dict`: Get graph statistics

## Contributing

To add support for a new language:

1. Add file extensions to `LANGUAGE_EXTENSIONS` in `tree_sitter_parser.py`
2. Implement extraction methods (`_extract_<language>_entities`)
3. Create a language-specific extractor in `language_extractors.py`
4. Test with sample code in that language

## License

This is part of the LocalMind code intelligence system.
