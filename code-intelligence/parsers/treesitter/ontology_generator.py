"""
Ontology Generator
Converts parsed AST entities into ontology/graph structures using NetworkX.
"""

import networkx as nx
from typing import Dict, List, Any, Set, Tuple, Optional
from pathlib import Path
import json
import matplotlib.pyplot as plt


class OntologyGenerator:
    """
    Generates code ontology and knowledge graphs from parsed entities.

    The ontology includes:
    - Nodes: Code entities (classes, functions, methods, etc.)
    - Edges: Relationships (inheritance, imports, calls, contains, etc.)

    Graph types supported:
    - Inheritance graphs (class hierarchies)
    - Dependency graphs (import/usage relationships)
    - Call graphs (function/method calls)
    - Module structure graphs
    """

    def __init__(self, parsed_data: Dict[str, Any]):
        """
        Initialize the ontology generator.

        Args:
            parsed_data: Output from TreeSitterParser.parse_repository()
        """
        self.parsed_data = parsed_data
        self.entities = parsed_data.get("entities", {})
        self.graph = nx.MultiDiGraph()  # Directed graph with multiple edges
        self.entity_lookup = {}  # Quick lookup by ID

    def build_ontology(self) -> nx.MultiDiGraph:
        """
        Build the complete code ontology graph.

        Returns:
            NetworkX MultiDiGraph representing the code ontology
        """
        print("🔨 Building code ontology...")

        # Step 1: Add all entities as nodes
        self._add_entity_nodes()

        # Step 2: Add structural relationships
        self._add_inheritance_edges()
        self._add_import_edges()
        self._add_containment_edges()
        self._add_implementation_edges()

        # Step 3: Add execution relationships (API/Service layer)
        self._add_api_endpoint_edges()
        self._add_service_call_edges()
        self._add_dto_usage_edges()
        self._add_repository_edges()
        self._add_module_relationship_edges()

        print(f"   Nodes: {self.graph.number_of_nodes()}")
        print(f"   Edges: {self.graph.number_of_edges()}")

        return self.graph

    def _add_entity_nodes(self):
        """Add all code entities as nodes in the graph."""
        print("   Adding entity nodes...")

        for entity_type, entity_list in self.entities.items():
            for entity in entity_list:
                entity_id = entity.get("id")
                if not entity_id:
                    continue

                # Store in lookup
                self.entity_lookup[entity_id] = entity

                # Add node with attributes
                self.graph.add_node(
                    entity_id,
                    name=entity.get("name"),
                    type=entity.get("type"),
                    entity_category=entity_type,
                    layer=entity.get("layer"),
                    language=entity.get("language"),
                    file_path=entity.get("file_path"),
                    line_start=entity.get("line_start"),
                    line_end=entity.get("line_end"),
                    docstring=entity.get("docstring"),
                    description=entity.get("description"),
                )

    def _add_inheritance_edges(self):
        """Add inheritance relationships (extends, implements)."""
        print("   Adding inheritance edges...")

        # Process classes
        for cls in self.entities.get("classes", []):
            class_id = cls.get("id")

            # Python: bases
            for base in cls.get("bases", []):
                base_id = self._find_entity_id(base, cls.get("file_path"))
                if base_id:
                    self.graph.add_edge(
                        class_id,
                        base_id,
                        relationship="inherits",
                        type="inheritance",
                    )

            # Java: extends and implements
            for parent in cls.get("extends", []):
                parent_id = self._find_entity_id(parent, cls.get("file_path"))
                if parent_id:
                    self.graph.add_edge(
                        class_id,
                        parent_id,
                        relationship="extends",
                        type="inheritance",
                    )

            for interface in cls.get("implements", []):
                interface_id = self._find_entity_id(interface, cls.get("file_path"))
                if interface_id:
                    self.graph.add_edge(
                        class_id,
                        interface_id,
                        relationship="implements",
                        type="implementation",
                    )

            # JS/TS: heritage (extends, implements)
            for heritage_type in cls.get("heritage", []):
                heritage_id = self._find_entity_id(heritage_type, cls.get("file_path"))
                if heritage_id:
                    self.graph.add_edge(
                        class_id,
                        heritage_id,
                        relationship="inherits",
                        type="inheritance",
                    )

    def _add_import_edges(self):
        """Add import/dependency relationships."""
        print("   Adding import edges...")

        for import_stmt in self.entities.get("imports", []):
            file_path = import_stmt.get("file_path")
            module = import_stmt.get("module", "")
            names = import_stmt.get("names", [])

            # Create a module node if it doesn't exist
            module_id = f"module::{module}"

            if module_id not in self.graph:
                self.graph.add_node(
                    module_id,
                    name=module,
                    type="module",
                    entity_category="module",
                )

            # Connect all entities in this file to the imported module
            file_entities = [
                e for entity_list in self.entities.values()
                for e in entity_list
                if e.get("file_path") == file_path and e.get("id")
            ]

            for entity in file_entities:
                entity_id = entity.get("id")
                self.graph.add_edge(
                    entity_id,
                    module_id,
                    relationship="imports",
                    type="dependency",
                    imported_names=names,
                )

    def _add_containment_edges(self):
        """Add containment relationships (file contains class, class contains method)."""
        print("   Adding containment edges...")

        # Group entities by file
        file_groups = {}
        for entity_type, entity_list in self.entities.items():
            for entity in entity_list:
                file_path = entity.get("file_path")
                if file_path:
                    if file_path not in file_groups:
                        file_groups[file_path] = []
                    file_groups[file_path].append(entity)

        # Add file nodes and containment edges
        for file_path, entities_in_file in file_groups.items():
            file_id = f"file::{file_path}"

            # Add file node
            if file_id not in self.graph:
                self.graph.add_node(
                    file_id,
                    name=Path(file_path).name,
                    type="file",
                    entity_category="file",
                    file_path=file_path,
                )

            # Connect file to entities
            for entity in entities_in_file:
                entity_id = entity.get("id")
                if entity_id:
                    self.graph.add_edge(
                        file_id,
                        entity_id,
                        relationship="contains",
                        type="containment",
                    )

    def _add_implementation_edges(self):
        """Add implementation relationships (Go methods to receivers, Rust impls)."""
        print("   Adding implementation edges...")

        # Go: method receivers
        for method in self.entities.get("methods", []):
            if method.get("language") == "go" and method.get("receiver"):
                receiver_type = method.get("receiver")
                method_id = method.get("id")

                # Find the struct/type
                receiver_id = self._find_entity_id(receiver_type, method.get("file_path"))
                if receiver_id:
                    self.graph.add_edge(
                        receiver_id,
                        method_id,
                        relationship="has_method",
                        type="implementation",
                    )

        # Rust: impl blocks
        for method in self.entities.get("methods", []):
            if method.get("language") == "rust" and method.get("impl_for"):
                impl_type = method.get("impl_for")
                method_id = method.get("id")

                # Find the struct/enum
                impl_id = self._find_entity_id(impl_type, method.get("file_path"))
                if impl_id:
                    self.graph.add_edge(
                        impl_id,
                        method_id,
                        relationship="implements_method",
                        type="implementation",
                    )

    def _find_entity_id(self, entity_name: str, context_file: str) -> Optional[str]:
        """
        Find entity ID by name, prioritizing entities in the same file.

        Args:
            entity_name: Name of the entity to find
            context_file: File path for context

        Returns:
            Entity ID or None if not found
        """
        # First, try exact match in the same file
        for entity_id, entity in self.entity_lookup.items():
            if entity.get("name") == entity_name and entity.get("file_path") == context_file:
                return entity_id

        # Then, try exact match in any file
        for entity_id, entity in self.entity_lookup.items():
            if entity.get("name") == entity_name:
                return entity_id

        # Finally, try partial match
        for entity_id, entity in self.entity_lookup.items():
            if entity_name in entity.get("name", ""):
                return entity_id

        return None

    def _add_api_endpoint_edges(self):
        """Add API endpoint relationships."""
        print("   Adding API endpoint edges...")

        for endpoint in self.entities.get("api_endpoints", []):
            endpoint_id = endpoint.get("id")
            controller_id = endpoint.get("controller")

            # Link controller → endpoint
            if controller_id and endpoint_id:
                if controller_id in self.graph and endpoint_id in self.graph:
                    self.graph.add_edge(
                        controller_id,
                        endpoint_id,
                        relationship="exposes_endpoint",
                        type="api",
                        http_method=endpoint.get("http_method"),
                        path=endpoint.get("path"),
                    )

    def _add_service_call_edges(self):
        """Add controller → service call relationships."""
        print("   Adding service call edges...")

        for endpoint in self.entities.get("api_endpoints", []):
            endpoint_id = endpoint.get("id")

            for service_call in endpoint.get("service_calls", []):
                # Parse "authService.validateUser"
                if "." in service_call:
                    service_name, method_name = service_call.split(".", 1)

                    # Find service ID
                    service_id = self._find_entity_by_pattern(
                        service_name,
                        entity_types=["service"]
                    )

                    if service_id and endpoint_id in self.graph:
                        self.graph.add_edge(
                            endpoint_id,
                            service_id,
                            relationship="calls_service",
                            type="execution",
                            method=method_name,
                        )

    def _add_dto_usage_edges(self):
        """Add DTO usage relationships."""
        print("   Adding DTO usage edges...")

        for endpoint in self.entities.get("api_endpoints", []):
            endpoint_id = endpoint.get("id")

            for dto_name in endpoint.get("dtos", []):
                dto_id = self._find_entity_by_name(dto_name)

                if dto_id and endpoint_id in self.graph:
                    self.graph.add_edge(
                        endpoint_id,
                        dto_id,
                        relationship="uses_dto",
                        type="data_flow",
                    )

    def _add_repository_edges(self):
        """Add service → repository relationships."""
        print("   Adding repository edges...")

        # Link services to repositories via dependencies
        for service in self.entities.get("classes", []):
            if service.get("type") != "service":
                continue

            service_id = service.get("id")

            # Check dependencies for repositories
            for dep in service.get("dependencies", []):
                dep_type = dep.get("type", "")
                if "Repository" in dep_type or "repository" in dep_type.lower():
                    repo_id = self._find_entity_by_name(dep_type)

                    if repo_id and service_id in self.graph:
                        self.graph.add_edge(
                            service_id,
                            repo_id,
                            relationship="uses_repository",
                            type="data_access",
                        )

        # Link repositories to entities
        for repo in self.entities.get("repositories", []):
            repo_id = repo.get("id")
            entity_name = repo.get("entity")

            if entity_name:
                entity_id = self._find_entity_by_name(entity_name)

                if entity_id and repo_id in self.graph:
                    self.graph.add_edge(
                        repo_id,
                        entity_id,
                        relationship="manages_entity",
                        type="data_access",
                    )

    def _add_module_relationship_edges(self):
        """Add NestJS module relationships."""
        print("   Adding module relationship edges...")

        for module in self.entities.get("modules", []):
            module_id = module.get("id")

            # Link module to controllers
            for controller_name in module.get("controllers", []):
                controller_id = self._find_entity_by_name(controller_name)
                if controller_id and module_id in self.graph:
                    self.graph.add_edge(
                        module_id,
                        controller_id,
                        relationship="provides_controller",
                        type="module_structure",
                    )

            # Link module to providers (services)
            for provider_name in module.get("providers", []):
                provider_id = self._find_entity_by_name(provider_name)
                if provider_id and module_id in self.graph:
                    self.graph.add_edge(
                        module_id,
                        provider_id,
                        relationship="provides_service",
                        type="module_structure",
                    )

            # Link module to imports
            for import_name in module.get("imports", []):
                import_id = self._find_entity_by_name(import_name)
                if import_id and module_id in self.graph:
                    self.graph.add_edge(
                        module_id,
                        import_id,
                        relationship="imports_module",
                        type="module_structure",
                    )

    def _find_entity_by_pattern(self, pattern: str, entity_types: List[str]) -> Optional[str]:
        """
        Find entity by name pattern and type.

        Args:
            pattern: Name pattern to search for
            entity_types: List of entity types to filter by

        Returns:
            Entity ID or None if not found
        """
        # First try exact match
        for entity_id, entity in self.entity_lookup.items():
            if (entity.get("type") in entity_types and
                entity.get("name") == pattern):
                return entity_id

        # Then try case-insensitive match
        for entity_id, entity in self.entity_lookup.items():
            if (entity.get("type") in entity_types and
                pattern.lower() in entity.get("name", "").lower()):
                return entity_id

        return None

    def _find_entity_by_name(self, name: str) -> Optional[str]:
        """
        Enhanced entity search by name.

        Args:
            name: Name to search for

        Returns:
            Entity ID or None if not found
        """
        if not name:
            return None

        # Exact match
        for entity_id, entity in self.entity_lookup.items():
            if entity.get("name") == name:
                return entity_id

        # Fuzzy match (contains)
        for entity_id, entity in self.entity_lookup.items():
            if name.lower() in entity.get("name", "").lower():
                return entity_id

        # Try matching by ID
        for entity_id, entity in self.entity_lookup.items():
            if name.lower() in entity_id.lower():
                return entity_id

        return None

    def get_inheritance_tree(self, class_id: str, max_depth: int = 10) -> Dict[str, Any]:
        """
        Get the inheritance tree for a class.

        Args:
            class_id: ID of the class
            max_depth: Maximum depth to traverse

        Returns:
            Dictionary representing the inheritance tree
        """
        if class_id not in self.graph:
            return {}

        tree = {"id": class_id, "children": []}

        # BFS to build tree
        visited = {class_id}
        queue = [(class_id, tree, 0)]

        while queue:
            current_id, current_node, depth = queue.pop(0)

            if depth >= max_depth:
                continue

            # Get all classes this one inherits from
            for successor in self.graph.successors(current_id):
                edge_data = self.graph.get_edge_data(current_id, successor)
                if edge_data and any(
                    e.get("type") in ["inheritance", "implementation"]
                    for e in edge_data.values()
                ):
                    if successor not in visited:
                        visited.add(successor)
                        child_node = {"id": successor, "children": []}
                        current_node["children"].append(child_node)
                        queue.append((successor, child_node, depth + 1))

        return tree

    def get_dependency_graph(self, entity_id: str, depth: int = 2) -> nx.DiGraph:
        """
        Get a subgraph showing dependencies for an entity.

        Args:
            entity_id: ID of the entity
            depth: How many levels of dependencies to include

        Returns:
            NetworkX DiGraph of dependencies
        """
        if entity_id not in self.graph:
            return nx.DiGraph()

        # BFS to collect nodes
        nodes_to_include = {entity_id}
        queue = [(entity_id, 0)]
        visited = {entity_id}

        while queue:
            current, current_depth = queue.pop(0)

            if current_depth >= depth:
                continue

            # Get all dependencies
            for successor in self.graph.successors(current):
                edge_data = self.graph.get_edge_data(current, successor)
                if edge_data and any(
                    e.get("type") == "dependency"
                    for e in edge_data.values()
                ):
                    if successor not in visited:
                        visited.add(successor)
                        nodes_to_include.add(successor)
                        queue.append((successor, current_depth + 1))

        # Create subgraph
        return self.graph.subgraph(nodes_to_include).copy()

    def get_call_graph(self) -> nx.DiGraph:
        """
        Get a call graph showing execution paths from API endpoints through services to data layer.

        This traces the complete execution flow:
        API Endpoint → Controller → Service → Repository → Entity

        Returns:
            NetworkX DiGraph of execution calls
        """
        call_graph = nx.DiGraph()

        # Start from all API endpoints as entry points
        for endpoint in self.entities.get("api_endpoints", []):
            endpoint_id = endpoint.get("id")
            if endpoint_id in self.graph:
                # Trace execution path from this endpoint
                self._trace_execution_path(
                    endpoint_id,
                    call_graph,
                    visited=set()
                )

        # If no API endpoints, try from controllers
        if call_graph.number_of_nodes() == 0:
            for cls in self.entities.get("classes", []):
                if cls.get("type") == "controller":
                    self._trace_execution_path(
                        cls.get("id"),
                        call_graph,
                        visited=set()
                    )

        return call_graph

    def _trace_execution_path(
        self,
        node_id: str,
        graph: nx.DiGraph,
        visited: Set[str]
    ):
        """
        Recursively trace execution path from a starting node.

        Args:
            node_id: Starting node ID
            graph: Graph to populate
            visited: Set of visited nodes to avoid cycles
        """
        if node_id in visited or node_id not in self.graph:
            return

        visited.add(node_id)

        # Add current node to call graph
        node_attrs = self.graph.nodes[node_id]
        graph.add_node(node_id, **node_attrs)

        # Get all outgoing execution edges
        for successor in self.graph.successors(node_id):
            edge_data = self.graph.get_edge_data(node_id, successor)

            # Check if any edge is an execution-related edge
            for edge_key, edge_attrs in edge_data.items():
                edge_type = edge_attrs.get("type", "")
                relationship = edge_attrs.get("relationship", "")

                # Include execution, API, and data access edges
                if edge_type in ["execution", "api", "data_access", "module_structure"]:
                    # Add successor node
                    successor_attrs = self.graph.nodes[successor]
                    graph.add_node(successor, **successor_attrs)

                    # Add edge
                    graph.add_edge(node_id, successor, **edge_attrs)

                    # Continue tracing
                    self._trace_execution_path(successor, graph, visited)

                # Also include dto usage for completeness
                elif relationship in ["uses_dto", "manages_entity"]:
                    successor_attrs = self.graph.nodes[successor]
                    graph.add_node(successor, **successor_attrs)
                    graph.add_edge(node_id, successor, **edge_attrs)

    def visualize(
        self,
        output_path: str,
        layout: str = "spring",
        figsize: Tuple[int, int] = (20, 15),
        node_types: Optional[List[str]] = None,
    ):
        """
        Visualize the ontology graph.

        Args:
            output_path: Path to save the visualization
            layout: Layout algorithm (spring, kamada_kawai, circular, hierarchical)
            figsize: Figure size (width, height)
            node_types: Optional filter for node types to include
        """
        print(f"🎨 Visualizing ontology (layout: {layout})...")

        # Filter graph if node_types specified
        if node_types:
            nodes_to_include = [
                n for n, d in self.graph.nodes(data=True)
                if d.get("type") in node_types
            ]
            graph_to_viz = self.graph.subgraph(nodes_to_include)
        else:
            graph_to_viz = self.graph

        plt.figure(figsize=figsize)

        # Choose layout
        if layout == "spring":
            pos = nx.spring_layout(graph_to_viz, k=0.5, iterations=50, seed=42)
        elif layout == "kamada_kawai":
            pos = nx.kamada_kawai_layout(graph_to_viz)
        elif layout == "circular":
            pos = nx.circular_layout(graph_to_viz)
        elif layout == "hierarchical":
            pos = self._hierarchical_layout(graph_to_viz)
        else:
            pos = nx.spring_layout(graph_to_viz, seed=42)

        # Color nodes by type
        type_colors = {
            "class": "#FF6B6B",  # Red
            "function": "#4ECDC4",  # Teal
            "method": "#45B7D1",  # Blue
            "interface": "#96CEB4",  # Green
            "struct": "#FFEAA7",  # Yellow
            "enum": "#DFE6E9",  # Gray
            "module": "#A29BFE",  # Purple
            "file": "#FDCB6E",  # Orange
        }

        node_colors = []
        for node in graph_to_viz.nodes():
            node_type = graph_to_viz.nodes[node].get("type", "unknown")
            node_colors.append(type_colors.get(node_type, "#CCCCCC"))

        # Draw graph
        nx.draw(
            graph_to_viz,
            pos,
            node_color=node_colors,
            with_labels=True,
            node_size=800,
            font_size=7,
            font_weight="bold",
            arrows=True,
            edge_color="#CCCCCC",
            alpha=0.8,
            arrowsize=10,
        )

        # Add legend
        import matplotlib.patches as mpatches

        legend_handles = [
            mpatches.Patch(color=color, label=node_type)
            for node_type, color in type_colors.items()
        ]
        plt.legend(handles=legend_handles, loc="upper left", fontsize=10)

        plt.title("Code Ontology Graph", fontsize=18, fontweight="bold")
        plt.axis("off")
        plt.tight_layout()

        # Save
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_file, dpi=150, bbox_inches="tight")

        print(f"   Saved to: {output_file}")
        plt.close()

    def _hierarchical_layout(self, graph: nx.Graph) -> Dict:
        """Create a hierarchical layout based on node types."""
        layers = {
            "file": 0,
            "module": 1,
            "class": 2,
            "interface": 2,
            "struct": 2,
            "function": 3,
            "method": 3,
        }

        pos = {}
        layer_counts = {}

        for node in graph.nodes():
            node_type = graph.nodes[node].get("type", "unknown")
            layer = layers.get(node_type, 4)

            if layer not in layer_counts:
                layer_counts[layer] = 0

            x = layer_counts[layer]
            y = -layer
            pos[node] = (x, y)

            layer_counts[layer] += 1

        return pos

    def save_ontology(self, output_path: str, format: str = "graphml"):
        """
        Save the ontology graph to disk.

        Args:
            output_path: Path to save the graph
            format: Format to save (graphml, gexf, json)
        """
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        if format == "graphml":
            nx.write_graphml(self.graph, output_file)
        elif format == "gexf":
            nx.write_gexf(self.graph, output_file)
        elif format == "json":
            # Convert to JSON-serializable format
            data = nx.node_link_data(self.graph)
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)

        print(f"💾 Ontology saved to: {output_file}")

    def load_ontology(self, input_path: str, format: str = "graphml"):
        """
        Load an ontology graph from disk.

        Args:
            input_path: Path to load the graph from
            format: Format of the saved graph
        """
        if format == "graphml":
            self.graph = nx.read_graphml(input_path)
        elif format == "gexf":
            self.graph = nx.read_gexf(input_path)
        elif format == "json":
            with open(input_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.graph = nx.node_link_graph(data)

        print(f"📂 Ontology loaded from: {input_path}")

    def export_to_neo4j_cypher(self, output_path: str):
        """
        Export the ontology as Neo4j Cypher statements.

        Args:
            output_path: Path to save the Cypher file
        """
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, "w", encoding="utf-8") as f:
            # Create nodes
            for node_id, attrs in self.graph.nodes(data=True):
                node_type = attrs.get("type", "Entity")
                properties = ", ".join(
                    f'{k}: "{v}"' if isinstance(v, str) else f"{k}: {v}"
                    for k, v in attrs.items()
                    if v is not None and k != "type"
                )
                f.write(f'CREATE (:{node_type} {{id: "{node_id}", {properties}}});\n')

            f.write("\n")

            # Create relationships
            for source, target, attrs in self.graph.edges(data=True):
                rel_type = attrs.get("relationship", "RELATED_TO").upper()
                properties = ", ".join(
                    f'{k}: "{v}"' if isinstance(v, str) else f"{k}: {v}"
                    for k, v in attrs.items()
                    if v is not None and k != "relationship"
                )
                f.write(
                    f'MATCH (a {{id: "{source}"}}), (b {{id: "{target}"}}) '
                    f"CREATE (a)-[:{rel_type} {{{properties}}}]->(b);\n"
                )

        print(f"💾 Neo4j Cypher export saved to: {output_file}")

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the ontology.

        Returns:
            Dictionary with various statistics
        """
        stats = {
            "total_nodes": self.graph.number_of_nodes(),
            "total_edges": self.graph.number_of_edges(),
            "node_types": {},
            "edge_types": {},
            "languages": set(),
            "files": set(),
        }

        # Count node types
        for node, attrs in self.graph.nodes(data=True):
            node_type = attrs.get("type", "unknown")
            stats["node_types"][node_type] = stats["node_types"].get(node_type, 0) + 1

            lang = attrs.get("language")
            if lang:
                stats["languages"].add(lang)

            file_path = attrs.get("file_path")
            if file_path:
                stats["files"].add(file_path)

        # Count edge types
        for _, _, attrs in self.graph.edges(data=True):
            edge_type = attrs.get("relationship", "unknown")
            stats["edge_types"][edge_type] = stats["edge_types"].get(edge_type, 0) + 1

        stats["languages"] = list(stats["languages"])
        stats["total_files"] = len(stats["files"])
        del stats["files"]  # Remove the set from output

        return stats

    def print_statistics(self):
        """Print ontology statistics in a readable format."""
        stats = self.get_statistics()

        print("\n📊 Ontology Statistics:")
        print(f"   Total Nodes: {stats['total_nodes']}")
        print(f"   Total Edges: {stats['total_edges']}")
        print(f"   Languages: {', '.join(stats['languages'])}")
        print(f"   Files: {stats['total_files']}")

        print("\n   Node Types:")
        for node_type, count in sorted(stats['node_types'].items(), key=lambda x: -x[1]):
            print(f"      {node_type}: {count}")

        print("\n   Relationship Types:")
        for edge_type, count in sorted(stats['edge_types'].items(), key=lambda x: -x[1]):
            print(f"      {edge_type}: {count}")
