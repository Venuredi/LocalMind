"""
Cross-Layer Dependency Graph Builder
Creates a NetworkX graph from the unified code index showing relationships across all layers.
"""

import json
import networkx as nx
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
import matplotlib.pyplot as plt


class GraphBuilder:
    """
    Builds a dependency graph from the unified code index.

    Graph Structure:
    - Nodes: Code components (screens, controllers, services, etc.)
    - Edges: Relationships (API calls, dependencies, navigation, etc.)
    """

    def __init__(self, index_data: Dict[str, Any]):
        self.index_data = index_data
        self.graph = nx.MultiDiGraph()  # Directed graph with multiple edges
        self.components = {}  # Quick lookup by ID

    def build_graph(self) -> nx.MultiDiGraph:
        """Build the dependency graph from the index."""
        print("📊 Building dependency graph...")

        # Add all components as nodes
        self._add_component_nodes()

        # Add relationships as edges
        self._add_relationship_edges()

        # Add infrastructure connections
        self._add_infrastructure_edges()

        print(f"   Nodes: {self.graph.number_of_nodes()}")
        print(f"   Edges: {self.graph.number_of_edges()}")

        return self.graph

    def _add_component_nodes(self):
        """Add all components as nodes in the graph."""
        components = self.index_data.get("components", [])

        for component in components:
            comp_id = component["id"]
            self.components[comp_id] = component

            # Add node with attributes
            self.graph.add_node(
                comp_id,
                name=component["name"],
                type=component["type"],
                layer=component["layer"],
                file_path=component["file_path"],
                description=component.get("description"),
            )

    def _add_relationship_edges(self):
        """Add relationship edges between components."""
        relationships = self.index_data.get("relationships", [])

        for rel in relationships:
            from_id = rel["from"]
            to_id = rel["to"]
            rel_type = rel["type"]

            # Only add edges if the target node exists to avoid phantom nodes,
            # unless it's a specific type like api_call where destination might not be fully indexed
            if to_id not in self.components and rel_type not in ["api_call"]:
                continue

            # Add edge with relationship metadata
            self.graph.add_edge(
                from_id,
                to_id,
                type=rel_type,
                layer_crossing=rel.get("layer_crossing", False),
                endpoint=rel.get("endpoint"),
                method=rel.get("method"),
            )

    def _add_infrastructure_edges(self):
        """Add infrastructure-related edges."""
        infrastructure = self.index_data.get("infrastructure", [])

        for infra in infrastructure:
            infra_id = infra["id"]
            infra_type = infra["type"]

            # Add infrastructure as a node
            self.graph.add_node(
                infra_id,
                name=infra["name"],
                type=infra_type,
                layer=infra["layer"],
            )

            # Connect deployments to services they deploy
            if infra_type == "k8s_deployment":
                # Link to backend services based on labels
                labels = infra.get("labels", {})
                if "app" in labels:
                    app_name = labels["app"]

                    # Find matching controller/service
                    for comp_id, comp in self.components.items():
                        if app_name.lower() in comp["name"].lower():
                            self.graph.add_edge(
                                infra_id,
                                comp_id,
                                type="deploys",
                                layer_crossing=True,
                            )

            # Connect configmaps/secrets to components that use them
            if infra_type in ["k8s_configmap", "k8s_secret"]:
                # Find deployments that reference this config/secret
                for other_infra in infrastructure:
                    if other_infra["type"] == "k8s_deployment":
                        # Check env vars
                        env_vars = other_infra.get("env_vars", [])
                        secrets_used = other_infra.get("secrets", [])

                        if infra["name"] in secrets_used:
                            self.graph.add_edge(
                                other_infra["id"],
                                infra_id,
                                type="uses_secret",
                                layer_crossing=False,
                            )

    def find_path(
        self, from_component: str, to_component: str
    ) -> Optional[List[str]]:
        """Find the shortest path between two components."""
        try:
            path = nx.shortest_path(self.graph, from_component, to_component)
            return path
        except nx.NetworkXNoPath:
            return None

    def find_dependencies(
        self, component_id: str, depth: int = 1
    ) -> Set[str]:
        """
        Find all dependencies of a component up to a certain depth.

        Args:
            component_id: The component to find dependencies for
            depth: How many levels deep to search (1 = direct deps only)

        Returns:
            Set of component IDs that this component depends on
        """
        if component_id not in self.graph:
            return set()

        dependencies = set()

        # BFS to find dependencies
        queue = [(component_id, 0)]
        visited = {component_id}

        while queue:
            current, current_depth = queue.pop(0)

            if current_depth >= depth:
                continue

            # Get all outgoing edges (things this component depends on)
            for successor in self.graph.successors(current):
                if successor not in visited:
                    dependencies.add(successor)
                    visited.add(successor)
                    queue.append((successor, current_depth + 1))

        return dependencies

    def find_dependents(
        self, component_id: str, depth: int = 1
    ) -> Set[str]:
        """
        Find all components that depend on this component.

        Args:
            component_id: The component to find dependents for
            depth: How many levels deep to search

        Returns:
            Set of component IDs that depend on this component
        """
        if component_id not in self.graph:
            return set()

        dependents = set()

        # BFS to find dependents
        queue = [(component_id, 0)]
        visited = {component_id}

        while queue:
            current, current_depth = queue.pop(0)

            if current_depth >= depth:
                continue

            # Get all incoming edges (things that depend on this)
            for predecessor in self.graph.predecessors(current):
                if predecessor not in visited:
                    dependents.add(predecessor)
                    visited.add(predecessor)
                    queue.append((predecessor, current_depth + 1))

        return dependents

    def get_component_context(
        self, component_id: str, include_deps: bool = True
    ) -> Dict[str, Any]:
        """
        Get full context for a component including its dependencies.

        Args:
            component_id: Component to get context for
            include_deps: Whether to include dependency information

        Returns:
            Dictionary with component info and related context
        """
        if component_id not in self.components:
            return {}

        component = self.components[component_id]
        context = {
            "component": component,
            "dependencies": [],
            "dependents": [],
            "related_apis": [],
        }

        if include_deps:
            # Get direct dependencies
            dep_ids = self.find_dependencies(component_id, depth=1)
            context["dependencies"] = [
                self.components.get(dep_id)
                for dep_id in dep_ids
                if dep_id in self.components
            ]

            # Get direct dependents
            dependent_ids = self.find_dependents(component_id, depth=1)
            context["dependents"] = [
                self.components.get(dep_id)
                for dep_id in dependent_ids
                if dep_id in self.components
            ]

            # Get related API endpoints
            for api in self.index_data.get("apis", []):
                if component_id in api.get("handler", ""):
                    context["related_apis"].append(api)

        return context

    def get_layer_flow(
        self, starting_component: str
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get the full flow from a starting component through all layers.

        Example: LoginScreen → POST /auth/login → AuthController → AuthService → UserRepository

        Args:
            starting_component: Component ID to start from (usually a screen/page)

        Returns:
            Dictionary mapping layers to components in the flow
        """
        flow = {
            "frontend-mobile": [],
            "frontend-web": [],
            "backend": [],
            "data": [],
            "infrastructure": [],
        }

        # BFS through the graph
        queue = [starting_component]
        visited = {starting_component}

        while queue:
            current = queue.pop(0)

            if current not in self.graph:
                continue

            # Get component info
            component = self.components.get(current)

            if component:
                layer = component["layer"]
                if layer in flow:
                    flow[layer].append(component)

            # Add successors to queue
            for successor in self.graph.successors(current):
                if successor not in visited:
                    visited.add(successor)
                    queue.append(successor)

        return flow

    def visualize(
        self, output_path: str, layout: str = "spring", figsize=(20, 15)
    ):
        """
        Visualize the dependency graph.

        Args:
            output_path: Path to save the visualization
            layout: Layout algorithm (spring, kamada_kawai, circular)
            figsize: Figure size (width, height)
        """
        print(f"🎨 Visualizing graph (layout: {layout})...")

        plt.figure(figsize=figsize)

        # Choose layout
        if layout == "spring":
            pos = nx.spring_layout(self.graph, k=0.5, iterations=50)
        elif layout == "kamada_kawai":
            pos = nx.kamada_kawai_layout(self.graph)
        elif layout == "circular":
            pos = nx.circular_layout(self.graph)
        else:
            pos = nx.spring_layout(self.graph)

        # Color nodes by layer
        layer_colors = {
            "frontend-mobile": "#FF6B6B",  # Red
            "frontend-web": "#4ECDC4",  # Teal
            "backend": "#45B7D1",  # Blue
            "data": "#96CEB4",  # Green
            "infrastructure": "#FFEAA7",  # Yellow
            "deployment": "#DFE6E9",  # Gray
        }

        node_colors = []
        for node in self.graph.nodes():
            layer = self.graph.nodes[node].get("layer", "unknown")
            node_colors.append(layer_colors.get(layer, "#CCCCCC"))

        # Draw graph
        nx.draw(
            self.graph,
            pos,
            node_color=node_colors,
            with_labels=True,
            node_size=1000,
            font_size=8,
            font_weight="bold",
            arrows=True,
            edge_color="#CCCCCC",
            alpha=0.7,
        )

        # Add legend
        import matplotlib.patches as mpatches

        legend_handles = [
            mpatches.Patch(color=color, label=layer)
            for layer, color in layer_colors.items()
        ]
        plt.legend(handles=legend_handles, loc="upper left")

        plt.title("Cross-Layer Dependency Graph", fontsize=16, fontweight="bold")
        plt.axis("off")
        plt.tight_layout()

        # Save
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_file, dpi=150, bbox_inches="tight")

        print(f"   Saved to: {output_file}")

    def save_graph(self, output_path: str):
        """Save graph to disk (GraphML format)."""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        nx.write_graphml(self.graph, output_file)
        print(f"💾 Graph saved to: {output_file}")

    def load_graph(self, input_path: str):
        """Load graph from disk."""
        self.graph = nx.read_graphml(input_path)
        print(f"📂 Graph loaded from: {input_path}")


def main():
    """Main entry point for graph building."""
    import argparse

    parser = argparse.ArgumentParser(description="Build dependency graph from index")
    parser.add_argument(
        "--index", required=True, help="Path to index JSON file"
    )
    parser.add_argument(
        "--output-graph",
        default="./data/graph.graphml",
        help="Output path for graph file",
    )
    parser.add_argument(
        "--output-viz",
        default="./data/graph.png",
        help="Output path for visualization",
    )
    parser.add_argument(
        "--viz-layout",
        default="spring",
        choices=["spring", "kamada_kawai", "circular"],
        help="Visualization layout algorithm",
    )

    args = parser.parse_args()

    # Load index
    with open(args.index, "r") as f:
        index_data = json.load(f)

    # Build graph
    builder = GraphBuilder(index_data)
    graph = builder.build_graph()

    # Save graph
    builder.save_graph(args.output_graph)

    # Visualize
    builder.visualize(args.output_viz, layout=args.viz_layout)


if __name__ == "__main__":
    main()
