"""
Unified Code Indexer
Combines all language-specific parsers and creates a unified intermediate representation.
"""

import json
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

import sys
sys.path.append(str(Path(__file__).parent.parent))

from parsers.nestjs.nestjs_parser import NestJSParser
from parsers.nestjs.enhanced_nestjs_parser import EnhancedNestJSParser
from parsers.react.react_parser import ReactParser
from parsers.flutter.flutter_parser import FlutterParser
from parsers.terraform.terraform_parser import TerraformParser
from parsers.argocd.argocd_parser import ArgoCDParser
from parsers.angular.angular_parser import AngularParser

# Import universal parser for ALL languages
from parsers.treesitter.tree_sitter_parser import TreeSitterParser
from parsers.treesitter.parser_adapter import ParserAdapter


class UnifiedIndexer:
    """
    Creates a unified index of the entire codebase across all layers.

    Output format: Intermediate Representation (IR) that normalizes
    different languages into a common structure.
    """

    def __init__(self, repo_path: str, progress_callback=None):
        self.repo_path = Path(repo_path)
        self.progress_callback = progress_callback
        self.index: Dict[str, Any] = {
            "metadata": {
                "repo_path": str(repo_path),
                "indexed_at": datetime.utcnow().isoformat(),
                "version": "1.0.0",
            },
            "components": [],  # Unified list of all code components
            "relationships": [],  # Cross-component relationships
            "apis": [],  # API contracts
            "infrastructure": [],  # Infra resources
        }

    def _progress(self, message: str):
        """Report progress if callback is available."""
        if self.progress_callback:
            self.progress_callback(message)

    def index_repository(self) -> Dict[str, Any]:
        """Index the entire repository across all layers."""
        self._progress("🔍 Starting repository indexing...")

        # Parse each layer
        self._progress("📱 Parsing Flutter (Mobile)...")
        flutter_data = self._parse_flutter()

        self._progress("🌐 Parsing React (Web)...")
        react_data = self._parse_react()

        self._progress("🅰️  Parsing Angular (Web)...")
        angular_data = self._parse_angular()

        self._progress("⚙️  Parsing NestJS (Backend)...")
        nestjs_data = self._parse_nestjs()

        self._progress("🏗️  Parsing Terraform (Infrastructure)...")
        terraform_data = self._parse_terraform()

        self._progress("☸️  Parsing ArgoCD/Kubernetes (Deployment)...")
        argocd_data = self._parse_argocd()

        # Parse with Tree-sitter (universal - ALL languages including C#, Java, Python, Go, etc.)
        self._progress("🌐 Parsing with Tree-sitter (universal parser - all languages)...")
        treesitter_data = self._parse_treesitter()

        # Combine into unified index
        self._progress("🔗 Building unified index...")
        self._build_unified_index(
            flutter_data, react_data, angular_data, nestjs_data, terraform_data, argocd_data, treesitter_data
        )

        # Extract relationships
        self._progress("🔗 Extracting cross-layer relationships...")
        self._extract_relationships()

        # Extract API contracts
        self._progress("📋 Extracting API contracts...")
        self._extract_api_contracts()

        self._progress("✅ Indexing complete!")
        return self.index

    def _parse_flutter(self) -> Dict[str, Any]:
        """Parse Flutter layer - auto-detect by scanning for .dart files or pubspec.yaml."""
        # Look for Flutter indicators
        flutter_indicators = list(self.repo_path.rglob("pubspec.yaml"))

        if not flutter_indicators:
            # Fallback: check if there are any .dart files
            dart_files = list(self.repo_path.rglob("*.dart"))
            if not dart_files:
                return {}

        # Parse from repository root (parser will recursively find .dart files)
        parser = FlutterParser(str(self.repo_path))
        return parser.parse()

    def _parse_react(self) -> Dict[str, Any]:
        """Parse React layer - auto-detect by scanning for .tsx/.jsx files or package.json with react."""
        # Look for React indicators
        has_react = False

        # Check for package.json with react dependency
        for pkg_json in self.repo_path.rglob("package.json"):
            try:
                import json
                content = pkg_json.read_text()
                data = json.loads(content)
                deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
                if "react" in deps:
                    has_react = True
                    break
            except:
                pass

        # Fallback: check for .tsx or .jsx files
        if not has_react:
            tsx_files = list(self.repo_path.rglob("*.tsx")) + list(self.repo_path.rglob("*.jsx"))
            if not tsx_files:
                return {}

        # Parse from repository root
        parser = ReactParser(str(self.repo_path))
        return parser.parse()

    def _parse_nestjs(self) -> Dict[str, Any]:
        """Parse NestJS layer - auto-detect by scanning for nest-cli.json or @nestjs imports."""
        # Look for NestJS indicators
        nestjs_indicators = list(self.repo_path.rglob("nest-cli.json"))

        if not nestjs_indicators:
            # Fallback: check for @nestjs imports in .ts files
            has_nestjs = False
            for ts_file in self.repo_path.rglob("*.ts"):
                try:
                    content = ts_file.read_text()
                    if "@nestjs/" in content or "@Controller" in content or "@Injectable" in content:
                        has_nestjs = True
                        break
                except:
                    pass

            if not has_nestjs:
                return {}

        # Use enhanced parser for comprehensive NestJS support
        parser = EnhancedNestJSParser(str(self.repo_path))
        return parser.parse()

    def _parse_angular(self) -> Dict[str, Any]:
        """Parse Angular layer - auto-detect by scanning for angular.json or @angular imports."""
        # Look for Angular indicators
        angular_indicators = list(self.repo_path.rglob("angular.json"))

        if not angular_indicators:
            # Fallback: check for @angular imports in .ts files
            has_angular = False
            for ts_file in self.repo_path.rglob("*.ts"):
                try:
                    content = ts_file.read_text()
                    if "@angular/" in content or "@Component" in content or "@NgModule" in content:
                        has_angular = True
                        break
                except:
                    pass

            if not has_angular:
                return {}

        # Parse from repository root
        parser = AngularParser(str(self.repo_path))
        return parser.parse()

    def _parse_terraform(self) -> Dict[str, Any]:
        """Parse Terraform layer - auto-detect by scanning for .tf files."""
        # Look for .tf files anywhere in the repository
        tf_files = list(self.repo_path.rglob("*.tf"))

        if not tf_files:
            return {}

        # Parse from repository root (parser will recursively find .tf files)
        parser = TerraformParser(str(self.repo_path))
        return parser.parse()

    def _parse_argocd(self) -> Dict[str, Any]:
        """Parse ArgoCD/Kubernetes layer - auto-detect by scanning for .yaml/.yml files with K8s manifests."""
        # Look for YAML files
        yaml_files = list(self.repo_path.rglob("*.yaml")) + list(self.repo_path.rglob("*.yml"))

        if not yaml_files:
            return {}

        # Check if any are Kubernetes manifests (have 'kind:' field)
        has_k8s = False
        for yaml_file in yaml_files[:10]:  # Check first 10 to avoid overhead
            try:
                content = yaml_file.read_text()
                if "kind:" in content and ("apiVersion:" in content or "metadata:" in content):
                    has_k8s = True
                    break
            except:
                pass

        if not has_k8s:
            return {}

        # Parse from repository root
        parser = ArgoCDParser(str(self.repo_path))
        return parser.parse()

    def _parse_treesitter(self) -> Dict[str, Any]:
        """
        Parse with Tree-sitter universal parser.

        This captures ALL languages including C#, Java, Python, Go, Rust, etc.
        Works for any language supported by Tree-sitter using generic AST patterns.
        """
        try:
            # Initialize tree-sitter parser
            ts_parser = TreeSitterParser(str(self.repo_path))

            # Parse repository - returns entities dict with classes, functions, methods, etc.
            ts_results = ts_parser.parse_repository()

            # Tree-sitter results are already in the right format with an "entities" key
            # No need to adapt - just return directly
            return ts_results.get("entities", {})

        except Exception as e:
            # If tree-sitter fails, log but continue (don't break entire indexing)
            print(f"⚠️  Tree-sitter parsing failed: {e}")
            import traceback
            traceback.print_exc()
            return {}

    def _build_unified_index(
        self,
        flutter_data: Dict,
        react_data: Dict,
        angular_data: Dict,
        nestjs_data: Dict,
        terraform_data: Dict,
        argocd_data: Dict,
        treesitter_data: Dict,
    ):
        """Build unified component index."""
        # Add Flutter components
        for screen in flutter_data.get("screens", []):
            self.index["components"].append(self._normalize_component(screen))

        for widget in flutter_data.get("widgets", []):
            self.index["components"].append(self._normalize_component(widget))

        for service in flutter_data.get("services", []):
            self.index["components"].append(self._normalize_component(service))

        # Add React components
        for page in react_data.get("pages", []):
            self.index["components"].append(self._normalize_component(page))

        for component in react_data.get("components", []):
            self.index["components"].append(self._normalize_component(component))

        for hook in react_data.get("hooks", []):
            self.index["components"].append(self._normalize_component(hook))

        for service in react_data.get("services", []):
            self.index["components"].append(self._normalize_component(service))

        # Add Angular components
        for component in angular_data.get("components", []):
            self.index["components"].append(self._normalize_component(component))

        for service in angular_data.get("services", []):
            self.index["components"].append(self._normalize_component(service))

        for ngrx_item in angular_data.get("ngrx_items", []):
            self.index["components"].append(self._normalize_component(ngrx_item))

        for module in angular_data.get("modules", []):
            self.index["components"].append(self._normalize_component(module))

        for directive in angular_data.get("directives", []):
            self.index["components"].append(self._normalize_component(directive))

        for pipe in angular_data.get("pipes", []):
            self.index["components"].append(self._normalize_component(pipe))

        for guard in angular_data.get("guards", []):
            self.index["components"].append(self._normalize_component(guard))

        for resolver in angular_data.get("resolvers", []):
            self.index["components"].append(self._normalize_component(resolver))

        for interceptor in angular_data.get("interceptors", []):
            self.index["components"].append(self._normalize_component(interceptor))

        # Add GraphQL operations as API contracts
        for gql_op in angular_data.get("graphql_operations", []):
            self.index["apis"].append({
                "endpoint": gql_op.get("name"),
                "method": gql_op.get("operation_type", "QUERY").upper(),
                "type": "graphql",
                "layer": "frontend-web",
                "gql": gql_op.get("gql", ""),
            })

        # Add NestJS components (using enhanced parser data)
        for controller in nestjs_data.get("controllers", []):
            self.index["components"].append(self._normalize_component(controller))

        for resolver in nestjs_data.get("graphql_resolvers", []):
            self.index["components"].append(self._normalize_component(resolver))

        for service in nestjs_data.get("services", []):
            self.index["components"].append(self._normalize_component(service))

        for dto in nestjs_data.get("dtos", []):
            self.index["components"].append(self._normalize_component(dto))

        for entity in nestjs_data.get("entities", []):
            self.index["components"].append(self._normalize_component(entity))

        for repository in nestjs_data.get("repositories", []):
            self.index["components"].append(self._normalize_component(repository))

        for schema in nestjs_data.get("mongo_schemas", []):
            self.index["components"].append(self._normalize_component(schema))

        for gateway in nestjs_data.get("socket_gateways", []):
            self.index["components"].append(self._normalize_component(gateway))

        for processor in nestjs_data.get("bull_processors", []):
            self.index["components"].append(self._normalize_component(processor))

        for guard in nestjs_data.get("guards", []):
            self.index["components"].append(self._normalize_component(guard))

        for interceptor in nestjs_data.get("interceptors", []):
            self.index["components"].append(self._normalize_component(interceptor))

        for middleware in nestjs_data.get("middleware", []):
            self.index["components"].append(self._normalize_component(middleware))

        for module in nestjs_data.get("modules", []):
            self.index["components"].append(self._normalize_component(module))

        # Add infrastructure components
        for resource in terraform_data.get("resources", []):
            self.index["components"].append(self._normalize_component(resource))
            self.index["infrastructure"].append(resource)

        for deployment in argocd_data.get("deployments", []):
            self.index["components"].append(self._normalize_component(deployment))
            self.index["infrastructure"].append(deployment)

        for configmap in argocd_data.get("configmaps", []):
            self.index["components"].append(self._normalize_component(configmap))
            self.index["infrastructure"].append(configmap)

        for secret in argocd_data.get("secrets", []):
            self.index["components"].append(self._normalize_component(secret))
            self.index["infrastructure"].append(secret)

        # Add Tree-sitter entities (universal - C#, Java, Python, Go, etc.)
        # These capture backend code that might be missed by framework-specific parsers
        for cls in treesitter_data.get("classes", []):
            self.index["components"].append(self._normalize_treesitter_component(cls))

        for func in treesitter_data.get("functions", []):
            self.index["components"].append(self._normalize_treesitter_component(func))

        for interface in treesitter_data.get("interfaces", []):
            self.index["components"].append(self._normalize_treesitter_component(interface))

        for enum in treesitter_data.get("enums", []):
            self.index["components"].append(self._normalize_treesitter_component(enum))

        for struct in treesitter_data.get("structs", []):
            self.index["components"].append(self._normalize_treesitter_component(struct))

        # Note: methods are contained within classes, imports are handled separately

    def _normalize_treesitter_component(self, component: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize tree-sitter entities to unified IR format.

        Tree-sitter entities include: classes, functions, interfaces, enums, structs
        from ANY language (C#, Java, Python, Go, Rust, etc.)
        """
        # Determine layer from language
        language = component.get("language", "unknown")
        layer = self._detect_layer_from_language(language, component.get("file_path", ""))

        # Build unique ID
        comp_id = component.get("id") or f"{component.get('file_path')}::{component.get('name')}"

        normalized = {
            "id": comp_id,
            "name": component.get("name", "unknown"),
            "type": component.get("type", "unknown"),
            "layer": layer,
            "file_path": component.get("file_path", ""),
            "line_start": component.get("line_start", 0),
            "description": None,  # Will be enriched later by semantic enricher
            "metadata": {
                "language": language,
                "node_type": component.get("node_type", ""),
            },
        }

        # Add type-specific metadata
        if component.get("type") == "class":
            normalized["metadata"].update({
                "methods": component.get("methods", []),
                "base_classes": component.get("base_classes", []),
                "interfaces": component.get("interfaces", []),
            })

        elif component.get("type") == "function":
            normalized["metadata"].update({
                "parameters": component.get("parameters", []),
                "return_type": component.get("return_type"),
            })

        elif component.get("type") == "interface":
            normalized["metadata"].update({
                "methods": component.get("methods", []),
            })

        return normalized

    def _detect_layer_from_language(self, language: str, file_path: str) -> str:
        """
        Detect layer from language and file path.

        This helps categorize tree-sitter entities into the correct layer.
        """
        # Map languages to typical layers
        backend_languages = {"c_sharp", "java", "python", "go", "rust", "ruby", "php"}
        frontend_languages = {"typescript", "javascript", "jsx", "tsx"}
        mobile_languages = {"dart", "swift", "kotlin"}

        # Convert file path to lowercase for case-insensitive matching
        file_path_lower = file_path.lower()

        # Check language first
        if language in backend_languages:
            # Further refine by file path
            if "test" in file_path_lower or "spec" in file_path_lower:
                return "backend-test"
            return "backend"

        elif language in frontend_languages:
            # Check if it's React, Angular, or plain web
            if "flutter" in file_path_lower or language == "dart":
                return "frontend-mobile"
            elif "react" in file_path_lower or ".tsx" in file_path_lower or ".jsx" in file_path_lower:
                return "frontend-web"
            elif "angular" in file_path_lower:
                return "frontend-web"
            else:
                return "frontend-web"

        elif language in mobile_languages:
            return "frontend-mobile"

        else:
            # Default to backend for unknown languages
            return "backend"

    def _normalize_component(self, component: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize a component into unified IR format.

        Standard fields:
        - id: unique identifier
        - name: component name
        - type: component type
        - layer: which layer (frontend-mobile, frontend-web, backend, data, infrastructure)
        - file_path: source file
        - dependencies: what it depends on
        - api_calls: API calls made
        - description: documentation
        """
        # Ensure id is always a non-empty string (required by ChromaDB & enricher)
        raw_id = component.get("id") or component.get("name")
        comp_id = str(raw_id) if raw_id else f"unknown_{component.get('file_path', '')}_{component.get('line_start', 0)}"

        normalized = {
            "id": comp_id,
            "name": component.get("name") or comp_id,
            "type": component.get("type") or "unknown",
            "layer": component.get("layer") or "unknown",
            "file_path": component.get("file_path") or "",
            "line_start": component.get("line_start", 0),
            "description": component.get("description"),  # None is allowed here; enricher handles it
            "metadata": {},
        }

        # Add type-specific metadata
        if component.get("type") in ["screen", "page"]:
            normalized["metadata"] = {
                "api_calls": component.get("api_calls", []),
                "navigation": component.get("navigation", []),
                "state": component.get("state", []),
            }

        elif component.get("type") == "controller":
            normalized["metadata"] = {
                "base_route": component.get("base_route"),
                "routes": component.get("routes", []),
                "dependencies": component.get("dependencies", []),
            }

        elif component.get("type") == "service":
            normalized["metadata"] = {
                "methods": component.get("methods", []),
                "dependencies": component.get("dependencies", []),
                "api_calls": component.get("api_calls", []),
            }

        elif component.get("type") == "hook":
            normalized["metadata"] = {
                "hooks_used": component.get("hooks_used", []),
                "api_calls": component.get("api_calls", []),
                "returns": component.get("returns", []),
            }

        elif component.get("type") in ["terraform_resource", "terraform_data"]:
            normalized["metadata"] = {
                "dependencies": [{"name": str(dep)} for dep in component.get("depends_on", [])],
                "env_vars": component.get("env_vars", []),
                "secrets": component.get("secrets", []),
                "tags": component.get("tags", {})
            }

        return normalized

    def _extract_relationships(self):
        """Extract cross-component relationships."""
        components = self.index["components"]

        for component in components:
            comp_id = component["id"]
            comp_type = component["type"]
            metadata = component.get("metadata", {})

            # Extract dependencies
            if "dependencies" in metadata:
                for dep in metadata["dependencies"]:
                    dep_name = dep.get("type") or dep.get("name")
                    self.index["relationships"].append(
                        {
                            "from": comp_id,
                            "to": dep_name,
                            "type": "depends_on",
                            "layer_crossing": self._is_layer_crossing(
                                component["layer"], None
                            ),
                        }
                    )

            # Extract API calls (frontend -> backend)
            if "api_calls" in metadata:
                for api_call in metadata["api_calls"]:
                    endpoint = api_call.get("endpoint", "")
                    method = api_call.get("method", "")

                    # Try to find matching backend endpoint
                    backend_handler = self._find_backend_handler(endpoint, method)

                    if backend_handler:
                        self.index["relationships"].append(
                            {
                                "from": comp_id,
                                "to": backend_handler,
                                "type": "api_call",
                                "endpoint": endpoint,
                                "method": method,
                                "layer_crossing": True,
                            }
                        )

            # Extract navigation (screen -> screen)
            if "navigation" in metadata:
                for nav in metadata["navigation"]:
                    target = nav.get("route") or nav.get("path")
                    if target:
                        self.index["relationships"].append(
                            {
                                "from": comp_id,
                                "to": target,
                                "type": "navigates_to",
                                "layer_crossing": False,
                            }
                        )

    def _find_backend_handler(self, endpoint: str, method: str) -> str:
        """Find the backend handler for an API endpoint."""
        for component in self.index["components"]:
            if component["type"] == "controller":
                routes = component.get("metadata", {}).get("routes", [])

                for route in routes:
                    if route.get("path") == endpoint and route.get("method") == method:
                        return f"{component['id']}.{route.get('handler')}"

        return None

    def _is_layer_crossing(self, from_layer: str, to_layer: str) -> bool:
        """Check if relationship crosses layers."""
        if not to_layer:
            return False

        return from_layer != to_layer

    def _extract_api_contracts(self):
        """Extract API contracts from controllers."""
        for component in self.index["components"]:
            if component["type"] == "controller":
                routes = component.get("metadata", {}).get("routes", [])

                for route in routes:
                    contract = {
                        "endpoint": route.get("path"),
                        "method": route.get("method"),
                        "handler": f"{component['id']}.{route.get('handler')}",
                        "controller": component["id"],
                        "dtos": route.get("dtos", []),
                        "service_calls": route.get("service_calls", []),
                        "layer": "backend",
                    }

                    self.index["apis"].append(contract)

    def save_index(self, output_path: str):
        """Save the index to a JSON file."""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(self.index, f, indent=2, ensure_ascii=False)

        print(f"\n💾 Index saved to: {output_file}")

        # Print statistics
        print("\n📊 Index Statistics:")
        print(f"   Components: {len(self.index['components'])}")
        print(f"   Relationships: {len(self.index['relationships'])}")
        print(f"   API Endpoints: {len(self.index['apis'])}")
        print(f"   Infrastructure: {len(self.index['infrastructure'])}")


def main():
    """Main entry point for indexing."""
    import argparse

    parser = argparse.ArgumentParser(description="Index a multi-stack repository")
    parser.add_argument("--repo", required=True, help="Path to repository")
    parser.add_argument(
        "--output",
        default="./data/index.json",
        help="Output path for index file",
    )

    args = parser.parse_args()

    indexer = UnifiedIndexer(args.repo)
    index = indexer.index_repository()
    indexer.save_index(args.output)


if __name__ == "__main__":
    main()
