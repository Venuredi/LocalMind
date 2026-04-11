"""
Context Assembler
Assembles relevant code context based on queries, using the graph and semantic search.
This is what powers AI-assisted coding tools like Cursor.
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
import re

import sys
sys.path.append(str(Path(__file__).parent.parent))

from graph.graph_builder import GraphBuilder


class ContextAssembler:
    """
    Assembles intelligent context for AI coding tools.

    Given a query like "Fix login issue", it:
    1. Identifies relevant components (LoginScreen, AuthController, etc.)
    2. Traverses the dependency graph
    3. Retrieves source code for relevant components
    4. Organizes by layer
    5. Returns structured context
    """

    def __init__(
        self,
        index_path: str,
        repo_path: str,
        graph_builder: Optional[GraphBuilder] = None,
    ):
        self.repo_path = Path(repo_path)

        # Load index
        with open(index_path, "r") as f:
            self.index_data = json.load(f)

        # Build or use provided graph
        if graph_builder:
            self.graph_builder = graph_builder
        else:
            self.graph_builder = GraphBuilder(self.index_data)
            self.graph_builder.build_graph()

        self.components = {
            comp["id"]: comp for comp in self.index_data.get("components", [])
        }

    def assemble_context(
        self,
        query: str,
        include_tests: bool = False,
        max_components: int = 20,
        target_files: Optional[List[str]] = None,
        intent: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Assemble context for a query.

        Args:
            query: Natural language query (e.g., "Fix login issue")
            include_tests: Whether to include test files
            max_components: Maximum number of components to return
            target_files: Explicit file names to force-include (highest priority)
            intent: Classified intent (feature, bugfix, refactor, enhance, analyse, meta)

        Returns:
            Structured context with relevant code
        """
        print(f"🔍 Assembling context for: '{query}' | intent={intent} | targets={target_files}")

        file_targeted = bool(target_files)

        # Per-request synthetic components — never mutate self.components directly
        session_components: Dict[str, Any] = {}

        # Step 1a: Force-pin explicitly named files
        pinned_components = []
        if file_targeted:
            pinned_components = self._find_target_file_components(
                target_files, session_components
            )
            print(f"   Pinned {len(pinned_components)} target file component(s)")

        # Step 1b: Keyword-relevance search (with layer restriction if file-targeted)
        target_layer = None
        if file_targeted and pinned_components:
            # Infer layer from the pinned file so we can restrict expansion
            pinned_comp = session_components.get(
                pinned_components[0]
            ) or self.components.get(pinned_components[0], {})
            target_layer = pinned_comp.get("layer")

        effective_max = min(max_components, 5) if file_targeted else max_components
        relevant_components = self._identify_relevant_components(
            query,
            file_targeted=file_targeted,
            target_layer=target_layer,
            session_components=session_components,
        )
        print(f"   Found {len(relevant_components)} relevant components")

        # Merge: pinned files first, then keyword-relevant (deduped)
        all_seed = list(dict.fromkeys(pinned_components + relevant_components))

        # Step 2: Expand to include dependencies
        expand_depth = 1 if file_targeted else 2
        expanded_components = self._expand_with_dependencies(
            all_seed, max_depth=expand_depth
        )
        # Apply layer restriction when a target file was specified
        if file_targeted and target_layer:
            _LAYER_GROUPS = {
                "frontend-web": {"frontend-web"},
                "frontend-mobile": {"frontend-mobile"},
                "backend": {"backend", "data"},
                "data": {"backend", "data"},
            }
            allowed_layers = _LAYER_GROUPS.get(target_layer, {target_layer})
            expanded_components = [
                c for c in expanded_components
                if (session_components.get(c) or self.components.get(c, {})).get("layer") in allowed_layers
                or c in pinned_components  # always keep pinned
            ]

        # Cap total components
        # Pinned files are always kept; the rest are capped
        non_pinned = [c for c in expanded_components if c not in pinned_components]
        expanded_components = pinned_components + non_pinned[: max(0, effective_max - len(pinned_components))]

        print(
            f"   Expanded to {len(expanded_components)} components (with dependencies)"
        )

        # Step 3: Retrieve source code
        context = self._build_context_structure(
            expanded_components, query,
            target_files=target_files,
            session_components=session_components,
        )
        context["intent"] = intent
        context["target_files"] = target_files or []

        # Step 4: Add infrastructure context — only for deploy-related queries
        _INFRA_INTENTS = {"feature", "bugfix"}
        _INFRA_KEYWORDS = {"deploy", "env", "k8s", "config", "secret", "kubernetes"}
        query_words = set(query.lower().split())
        if intent in _INFRA_INTENTS and query_words & _INFRA_KEYWORDS:
            self._add_infrastructure_context(context, expanded_components)

        # Step 5: Add API contracts — only for feature and bugfix intents
        if intent in {"feature", "bugfix"}:
            self._add_api_contracts(context, expanded_components)

        print(f"✅ Context assembled successfully")

        return context

    def _find_target_file_components(
        self, target_files: List[str], session_components: Dict[str, Any]
    ) -> List[str]:
        """
        Force-find components for explicitly named files.
        Searches the index by file_path match; if not found, reads the file
        directly from disk and creates a synthetic entry scoped to this request.

        Synthetic components are stored in ``session_components`` (not in
        ``self.components``) so they never bleed into subsequent requests.
        """
        pinned = []
        for target_name in target_files:
            target_lower = target_name.lower()
            matched = [
                comp_id for comp_id, comp in self.components.items()
                if target_lower in comp.get("file_path", "").lower()
            ]
            if matched:
                pinned.extend(matched)
            else:
                # Disk fallback: search repo for the file
                try:
                    found_path = None
                    for candidate in self.repo_path.rglob(target_name):
                        found_path = candidate
                        break
                    if found_path and found_path.exists():
                        synthetic_id = f"__disk__{target_name}"
                        with open(found_path, "r", encoding="utf-8") as fh:
                            source = fh.read()
                        # Store in per-request dict — never mutate self.components
                        session_components[synthetic_id] = {
                            "id": synthetic_id,
                            "name": target_name,
                            "type": "component",
                            "layer": "frontend-web",
                            "file_path": str(found_path.relative_to(self.repo_path)),
                            "line_start": 0,
                            "description": f"Target file: {target_name}",
                            "_source_override": source,
                        }
                        pinned.append(synthetic_id)
                        print(f"   📂 Disk fallback: found {target_name} at {found_path}")
                    else:
                        print(f"   ⚠️  Target file not found in index or on disk: {target_name}")
                except Exception as e:
                    print(f"   ⚠️  Error searching disk for {target_name}: {e}")
        return list(dict.fromkeys(pinned))  # dedupe, preserve order

    def _identify_relevant_components(
        self,
        query: str,
        file_targeted: bool = False,
        target_layer: Optional[str] = None,
        session_components: Optional[Dict[str, Any]] = None,
    ) -> List[str]:
        """
        Identify components relevant to the query.
        Uses keyword matching + exact-name boosting.
        When file_targeted=True applies a stricter min-score gate.
        """
        relevant = []

        # Extract keywords from query
        keywords = self._extract_keywords(query)

        # Paths that indicate a library/vendor file — skip them even if indexed
        _VENDOR_MARKERS = (
            "node_modules", ".pnpm", ".npm",
            "dist/", "/dist/", "build/",
            ".dart_tool", ".pub-cache",
        )

        # Layer restriction: when a specific frontend/backend file is targeted,
        # ignore components from irrelevant layers during keyword search.
        _LAYER_RESTRICTIONS: Dict[str, set] = {
            "frontend-web": {"frontend-web"},
            "frontend-mobile": {"frontend-mobile"},
            "backend": {"backend", "data"},
            "data": {"backend", "data"},
        }
        allowed_layers = _LAYER_RESTRICTIONS.get(target_layer) if target_layer else None

        # Search through components (index + any request-scoped synthetic entries)
        all_components = {**self.components, **(session_components or {})}
        for comp_id, component in all_components.items():
            file_path = component.get("file_path", "")

            # Hard-skip anything that looks like a library file
            if any(marker in file_path for marker in _VENDOR_MARKERS):
                continue

            # Skip components from restricted layers when file is targeted
            if allowed_layers and component.get("layer") not in allowed_layers:
                continue

            score = self._calculate_relevance_score(component, keywords, query)

            if score > 0:
                relevant.append((comp_id, score))

        # Sort by relevance
        relevant.sort(key=lambda x: x[1], reverse=True)

        # Apply minimum-score gate: stricter when a specific file is targeted
        min_score = 15 if file_targeted else 1
        top_n = 5 if file_targeted else 10
        qualified = [(c, s) for c, s in relevant if s >= min_score]

        return [comp_id for comp_id, _ in qualified[:top_n]]

    def _extract_keywords(self, query: str) -> List[str]:
        """Extract keywords from query."""
        # Convert to lowercase
        query_lower = query.lower()

        # Common domain keywords
        domain_keywords = {
            "login": ["login", "auth", "signin", "authentication"],
            "register": ["register", "signup", "registration"],
            "profile": ["profile", "user", "account"],
            "logout": ["logout", "signout"],
            "password": ["password", "credential"],
            "token": ["token", "jwt", "refresh"],
        }

        keywords = []

        # Extract direct keywords
        for word in query_lower.split():
            cleaned = re.sub(r"[^\w]", "", word)
            if len(cleaned) > 2:
                keywords.append(cleaned)

        # Add related keywords
        for key, related in domain_keywords.items():
            if key in query_lower:
                keywords.extend(related)

        return list(set(keywords))

    def _calculate_relevance_score(
        self, component: Dict, keywords: List[str], query: str
    ) -> int:
        """Calculate relevance score for a component."""
        score = 0

        component_name = component.get("name") or ""
        component_name_lower = component_name.lower()
        query_lower = query.lower()
        file_path = component.get("file_path", "").lower()

        # ── Exact / near-exact name match (highest priority) ──────────────────
        # e.g. query contains "casescontroller" and name is "CasesController"
        for keyword in keywords:
            kw = keyword.lower()
            if kw == component_name_lower:
                score += 100          # perfect name match
            elif kw in component_name_lower:
                score += 20           # partial name match

        # ── CamelCase word splitting bonus ────────────────────────────────────
        # Allows "cases" to match "CasesController"
        import re as _re
        name_words = [w.lower() for w in _re.findall(r'[A-Z][a-z]+|[a-z]+', component_name)]
        for keyword in keywords:
            kw = keyword.lower()
            if kw in name_words:
                score += 15

        # ── Description match ─────────────────────────────────────────────────
        description = (component.get("description") or "").lower()
        for keyword in keywords:
            if keyword.lower() in description:
                score += 5

        # ── File path match ───────────────────────────────────────────────────
        for keyword in keywords:
            if keyword.lower() in file_path:
                score += 8

        # ── Type boosting ─────────────────────────────────────────────────────
        # Prefer real project entry points over utilities
        if component.get("type") in ["controller", "screen", "page"]:
            score += 5
        elif component.get("type") in ["service", "resolver"]:
            score += 3

        return score

    def _expand_with_dependencies(
        self, component_ids: List[str], max_depth: int = 2
    ) -> List[str]:
        """
        Expand component list to include dependencies.

        Args:
            component_ids: Initial list of component IDs
            max_depth: How deep to traverse dependencies

        Returns:
            Expanded list including dependencies
        """
        expanded = set(component_ids)

        for comp_id in component_ids:
            # Get dependencies
            deps = self.graph_builder.find_dependencies(comp_id, depth=max_depth)
            expanded.update(deps)

        return list(expanded)

    def _build_context_structure(
        self,
        component_ids: List[str],
        query: str,
        target_files: Optional[List[str]] = None,
        session_components: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Build structured context with source code.

        Organizes by layer for easy understanding.
        """
        context = {
            "query": query,
            "summary": self._generate_summary(component_ids),
            "layers": {
                "frontend-mobile": [],
                "frontend-web": [],
                "backend": [],
                "data": [],
            },
            "infrastructure": [],
            "api_contracts": [],
            "impact_analysis": {},
        }

        # Merge index components with request-scoped synthetic components
        all_components = {**self.components, **(session_components or {})}

        # Group components by layer
        for comp_id in component_ids:
            if comp_id not in all_components:
                continue

            component = all_components[comp_id]
            layer = component.get("layer")

            # Use pre-loaded source for disk-fallback synthetic components
            if "_source_override" in component:
                source_code = component["_source_override"]
            else:
                file_path_lower = (component.get("file_path") or "").lower()
                is_targeted = any(t.lower() in file_path_lower for t in (target_files or []))

                source_code = self._read_source_code(
                    component["file_path"], 
                    0 if is_targeted else component.get("line_start", 0)
                )

            # Build component context
            comp_context = {
                "name": component["name"],
                "type": component["type"],
                "file_path": component["file_path"],
                "line_start": component.get("line_start", 0),
                "description": component.get("description"),
                "source_code": source_code,
            }

            # Add to appropriate layer
            if layer in context["layers"]:
                context["layers"][layer].append(comp_context)

        return context

    def _read_source_code(
        self, file_path: str, line_start: int, context_lines: int = 50
    ) -> Optional[str]:
        """Read source code for a component."""
        try:
            # Find file in repo
            full_path = None

            # Try direct path first (most common case)
            candidate = self.repo_path / file_path
            if candidate.exists():
                full_path = candidate
            else:
                # Try different base paths for compatibility with different repo structures
                possible_bases = [
                    self.repo_path,
                    self.repo_path / "mobile" / "flutter_app",
                    self.repo_path / "web" / "react_app",
                    self.repo_path / "backend" / "nestjs_api",
                    self.repo_path / "infra",
                ]

                for base in possible_bases:
                    candidate = base / file_path
                    if candidate.exists():
                        full_path = candidate
                        break

            if not full_path or not full_path.exists():
                return None

            # Read file
            with open(full_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            # For target files (line_start=0) return the full file content
            if line_start == 0:
                return "".join(lines)

            # Extract relevant section
            start = max(0, line_start - 1)
            end = min(len(lines), line_start + context_lines)

            code_section = "".join(lines[start:end])

            return code_section

        except Exception as e:
            print(f"   Error reading {file_path}: {e}")
            return None

    def _add_infrastructure_context(
        self, context: Dict, component_ids: List[str]
    ):
        """Add infrastructure context (env vars, secrets, deployments)."""
        infrastructure = self.index_data.get("infrastructure", [])

        for infra in infrastructure:
            infra_type = infra.get("type")

            # Add relevant infrastructure
            if infra_type in ["k8s_deployment", "k8s_configmap", "k8s_secret"]:
                context["infrastructure"].append(
                    {
                        "name": infra["name"],
                        "type": infra_type,
                        "file_path": infra.get("file_path"),
                        "namespace": infra.get("namespace"),
                        "data": infra.get("data", {}),
                    }
                )

    def _add_api_contracts(self, context: Dict, component_ids: List[str]):
        """Add API contracts for relevant endpoints."""
        apis = self.index_data.get("apis", [])

        for api in apis:
            handler = api.get("handler", "")

            # Check if any component in our context is related to this API
            for comp_id in component_ids:
                if comp_id in handler:
                    context["api_contracts"].append(api)
                    break

    def _generate_summary(self, component_ids: List[str]) -> str:
        """Generate a human-readable summary of the context."""
        layer_counts = {}

        for comp_id in component_ids:
            if comp_id not in self.components:
                continue

            component = self.components[comp_id]
            layer = component.get("layer", "unknown")

            layer_counts[layer] = layer_counts.get(layer, 0) + 1

        summary_parts = []

        if layer_counts.get("frontend-mobile"):
            summary_parts.append(
                f"{layer_counts['frontend-mobile']} mobile component(s)"
            )

        if layer_counts.get("frontend-web"):
            summary_parts.append(
                f"{layer_counts['frontend-web']} web component(s)"
            )

        if layer_counts.get("backend"):
            summary_parts.append(
                f"{layer_counts['backend']} backend component(s)"
            )

        if layer_counts.get("data"):
            summary_parts.append(f"{layer_counts['data']} data component(s)")

        return (
            "Context includes: " + ", ".join(summary_parts) if summary_parts else ""
        )

    def get_flow_context(self, entry_point: str) -> Dict[str, Any]:
        """
        Get full flow context from an entry point.

        Example: LoginScreen → API → Controller → Service → Repository

        Args:
            entry_point: Component ID of entry point (usually a screen/page)

        Returns:
            Flow-based context
        """
        print(f"🔄 Getting flow context from: {entry_point}")

        # Get layer flow
        flow = self.graph_builder.get_layer_flow(entry_point)

        # Build context for each layer
        flow_context = {
            "entry_point": entry_point,
            "flow": {},
        }

        for layer, components in flow.items():
            if not components:
                continue

            flow_context["flow"][layer] = []

            for component in components:
                comp_context = {
                    "name": component["name"],
                    "type": component["type"],
                    "file_path": component["file_path"],
                    "line_start": component.get("line_start", 0),
                }

                flow_context["flow"][layer].append(comp_context)

        return flow_context

    def format_for_ai(self, context: Dict[str, Any]) -> str:
        """
        Format context for AI consumption (Cursor, Copilot, etc.).

        Returns a well-structured text representation.
        """
        output = []

        output.append(f"# Context for: {context['query']}")
        output.append(f"\n{context['summary']}\n")

        # Frontend Mobile
        if context["layers"]["frontend-mobile"]:
            output.append("\n## 📱 Flutter (Mobile Layer)\n")
            for comp in context["layers"]["frontend-mobile"]:
                output.append(f"### {comp['name']} ({comp['type']})")
                output.append(f"File: `{comp['file_path']}:{comp['line_start']}`")

                if comp.get("description"):
                    output.append(f"Description: {comp['description']}")

                if comp.get("source_code"):
                    output.append(f"\n```dart\n{comp['source_code']}\n```\n")

        # Frontend Web
        if context["layers"]["frontend-web"]:
            output.append("\n## 🌐 React (Web Layer)\n")
            for comp in context["layers"]["frontend-web"]:
                output.append(f"### {comp['name']} ({comp['type']})")
                output.append(f"File: `{comp['file_path']}:{comp['line_start']}`")

                if comp.get("description"):
                    output.append(f"Description: {comp['description']}")

                if comp.get("source_code"):
                    output.append(
                        f"\n```typescript\n{comp['source_code']}\n```\n"
                    )

        # Backend
        if context["layers"]["backend"]:
            output.append("\n## ⚙️ NestJS (Backend Layer)\n")
            for comp in context["layers"]["backend"]:
                output.append(f"### {comp['name']} ({comp['type']})")
                output.append(f"File: `{comp['file_path']}:{comp['line_start']}`")

                if comp.get("description"):
                    output.append(f"Description: {comp['description']}")

                if comp.get("source_code"):
                    output.append(
                        f"\n```typescript\n{comp['source_code']}\n```\n"
                    )

        # Data Layer
        if context["layers"]["data"]:
            output.append("\n## 🗄️ Data Layer\n")
            for comp in context["layers"]["data"]:
                output.append(f"### {comp['name']} ({comp['type']})")
                output.append(f"File: `{comp['file_path']}:{comp['line_start']}`")

                if comp.get("source_code"):
                    output.append(
                        f"\n```typescript\n{comp['source_code']}\n```\n"
                    )

        # Infrastructure
        if context["infrastructure"]:
            output.append("\n## ☸️ Infrastructure\n")
            for infra in context["infrastructure"]:
                output.append(f"### {infra['name']} ({infra['type']})")
                output.append(f"File: `{infra['file_path']}`")

                if infra.get("namespace"):
                    output.append(f"Namespace: {infra['namespace']}")

        # API Contracts
        if context["api_contracts"]:
            output.append("\n## 📋 API Contracts\n")
            for api in context["api_contracts"]:
                output.append(
                    f"- **{api['method']} {api['endpoint']}** → `{api['handler']}`"
                )

        return "\n".join(output)


def main():
    """Main entry point for context assembly."""
    import argparse

    parser = argparse.ArgumentParser(description="Assemble code context")
    parser.add_argument(
        "--index", required=True, help="Path to index JSON file"
    )
    parser.add_argument("--repo", required=True, help="Path to repository")
    parser.add_argument(
        "--query", required=True, help="Query string (e.g., 'Fix login issue')"
    )
    parser.add_argument(
        "--output", default="./data/context.txt", help="Output file"
    )

    args = parser.parse_args()

    # Create assembler
    assembler = ContextAssembler(args.index, args.repo)

    # Assemble context
    context = assembler.assemble_context(args.query)

    # Format for AI
    formatted = assembler.format_for_ai(context)

    # Save
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(formatted)

    print(f"\n💾 Context saved to: {output_path}")

    # Also save JSON
    json_output = output_path.with_suffix(".json")
    with open(json_output, "w", encoding="utf-8") as f:
        json.dump(context, f, indent=2, ensure_ascii=False)

    print(f"💾 JSON context saved to: {json_output}")


if __name__ == "__main__":
    main()
