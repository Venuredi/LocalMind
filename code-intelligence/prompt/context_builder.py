"""
Ontology Context Builder

Extracts rich context from the code ontology for prompt generation.
Provides component details, dependencies, relationships, and source code.
"""

from typing import Dict, List, Any, Optional, Set
from pathlib import Path
import networkx as nx
import re


class OntologyContextBuilder:
    """
    Builds comprehensive context from the ontology for a given component.

    This context includes:
    - Component details (name, type, layer, file path)
    - Dependencies (what this component depends on)
    - Dependents (what depends on this component)
    - Related DTOs, entities, repositories
    - Dependency chain (architectural flow)
    - Source code content
    """

    def __init__(self, index_data: Dict[str, Any], graph: nx.DiGraph):
        """
        Initialize context builder.

        Args:
            index_data: Unified index data from UnifiedIndexer
            graph: Dependency graph from GraphBuilder
        """
        self.index_data = index_data
        self.graph = graph
        self.components = index_data.get('components', [])
        self.relationships = index_data.get('relationships', [])

    def build_context(self, component_name: str) -> Dict[str, Any]:
        """
        Build comprehensive context for a component.

        Args:
            component_name: Name of the component (e.g., "SurgeonsService")

        Returns:
            Dictionary with full context including:
            - component: Component details
            - dependencies: List of dependencies
            - dependents: List of dependents
            - related_dtos: DTOs used by this component
            - related_entities: Entities used
            - related_repositories: Repositories used
            - layer: Component layer
            - file_content: Source code
            - dependency_chain: Architectural dependency chain
        """
        # Find the component
        component = self._find_component(component_name)

        if not component:
            return {
                'error': f"Component '{component_name}' not found in ontology",
                'suggestions': self._find_similar_components(component_name)
            }

        # Build full context
        context = {
            'component': component,
            'layer': component.get('layer', 'unknown'),
            'file_path': component.get('file_path', ''),
            'component_type': component.get('type', 'unknown'),
        }

        # Get dependencies and dependents
        context['dependencies'] = self._get_dependencies(component['id'])
        context['dependents'] = self._get_dependents(component['id'])

        # Get related components by type
        context['related_dtos'] = self._get_related_by_type(component, 'dto')
        context['related_entities'] = self._get_related_by_type(component, 'entity')
        context['related_repositories'] = self._get_related_by_type(component, 'repository')
        context['related_controllers'] = self._get_related_by_type(component, 'controller')
        context['related_services'] = self._get_related_by_type(component, 'service')

        # Build dependency chain
        context['dependency_chain'] = self._build_dependency_chain(component)

        # Get source code
        context['file_content'] = self._get_file_content(component.get('file_path'))
        context['file_snippet'] = self._get_file_snippet(component)

        # Detect tech stack
        context['tech_stack'] = self._detect_tech_stack(component)

        # Get all related components
        context['all_related_components'] = self._get_all_related_components(component)

        return context

    def _find_component(self, component_name: str) -> Optional[Dict[str, Any]]:
        """Find a component by name."""
        # Try exact match first
        for comp in self.components:
            if comp.get('name') == component_name:
                return comp

        # Try case-insensitive match
        component_name_lower = component_name.lower()
        for comp in self.components:
            if comp.get('name', '').lower() == component_name_lower:
                return comp

        # Try partial match (ends with component name)
        for comp in self.components:
            comp_name = comp.get('name', '')
            if comp_name.endswith(component_name):
                return comp

        return None

    def _find_similar_components(self, component_name: str) -> List[str]:
        """Find similar component names for suggestions."""
        component_name_lower = component_name.lower()
        suggestions = []

        for comp in self.components:
            comp_name = comp.get('name', '')
            if component_name_lower in comp_name.lower():
                suggestions.append(comp_name)

        return suggestions[:5]  # Return top 5 suggestions

    def _get_dependencies(self, component_id: str) -> List[Dict[str, Any]]:
        """Get what this component depends on."""
        dependencies = []

        # Use graph if available
        if self.graph and component_id in self.graph:
            for successor in self.graph.successors(component_id):
                dep_comp = self._find_component_by_id(successor)
                if dep_comp:
                    dependencies.append({
                        'name': dep_comp.get('name'),
                        'type': dep_comp.get('type'),
                        'layer': dep_comp.get('layer'),
                        'file_path': dep_comp.get('file_path')
                    })

        # Also check relationships
        for rel in self.relationships:
            if rel.get('from') == component_id:
                dep_comp = self._find_component_by_id(rel.get('to'))
                if dep_comp and dep_comp not in dependencies:
                    dependencies.append({
                        'name': dep_comp.get('name'),
                        'type': dep_comp.get('type'),
                        'layer': dep_comp.get('layer'),
                        'relationship_type': rel.get('type')
                    })

        return dependencies

    def _get_dependents(self, component_id: str) -> List[Dict[str, Any]]:
        """Get what depends on this component."""
        dependents = []

        # Use graph if available
        if self.graph and component_id in self.graph:
            for predecessor in self.graph.predecessors(component_id):
                dep_comp = self._find_component_by_id(predecessor)
                if dep_comp:
                    dependents.append({
                        'name': dep_comp.get('name'),
                        'type': dep_comp.get('type'),
                        'layer': dep_comp.get('layer'),
                        'file_path': dep_comp.get('file_path')
                    })

        # Also check relationships
        for rel in self.relationships:
            if rel.get('to') == component_id:
                dep_comp = self._find_component_by_id(rel.get('from'))
                if dep_comp and dep_comp not in dependents:
                    dependents.append({
                        'name': dep_comp.get('name'),
                        'type': dep_comp.get('type'),
                        'layer': dep_comp.get('layer'),
                        'relationship_type': rel.get('type')
                    })

        return dependents

    def _find_component_by_id(self, component_id: str) -> Optional[Dict[str, Any]]:
        """Find a component by its ID."""
        for comp in self.components:
            if comp.get('id') == component_id:
                return comp
        return None

    def _get_related_by_type(self, component: Dict[str, Any], related_type: str) -> List[Dict[str, Any]]:
        """Get all related components of a specific type."""
        related = []
        component_id = component.get('id')

        # Get from dependencies
        for dep in self._get_dependencies(component_id):
            if dep.get('type') == related_type:
                related.append(dep)

        # Get from dependents
        for dep in self._get_dependents(component_id):
            if dep.get('type') == related_type:
                related.append(dep)

        # Also search in same file
        file_path = component.get('file_path')
        if file_path:
            for comp in self.components:
                if comp.get('file_path') == file_path and comp.get('type') == related_type:
                    if comp not in related:
                        related.append({
                            'name': comp.get('name'),
                            'type': comp.get('type'),
                            'layer': comp.get('layer'),
                            'file_path': comp.get('file_path')
                        })

        return related

    def _build_dependency_chain(self, component: Dict[str, Any]) -> str:
        """
        Build architectural dependency chain.

        E.g., "Controller → Service → Repository"
        """
        component_type = component.get('type', '').lower()
        layer = component.get('layer', '').lower()

        # Common NestJS/Backend patterns
        if 'backend' in layer:
            if 'controller' in component_type:
                return "Controller → Service → Repository → Database"
            elif 'service' in component_type:
                return "Service → Repository → Database"
            elif 'repository' in component_type:
                return "Repository → Database"
            elif 'dto' in component_type:
                return "Controller ← DTO → Service"
            elif 'entity' in component_type:
                return "Repository ← Entity → Database"
            else:
                return "Backend Layer"

        # Frontend patterns
        elif 'frontend' in layer:
            if 'component' in component_type or 'page' in component_type:
                return "Component → Hook/Service → API"
            elif 'hook' in component_type:
                return "Hook → API/Context"
            elif 'service' in component_type:
                return "Service → API"
            else:
                return "Frontend Layer"

        # Default
        return f"{component_type.capitalize()} Layer"

    def _get_file_content(self, file_path: str) -> Optional[str]:
        """Get the source code content of a file."""
        if not file_path:
            return None

        try:
            # Handle relative paths
            full_path = Path(file_path)
            if not full_path.is_absolute():
                # Try to resolve from index metadata
                repo_path = self.index_data.get('metadata', {}).get('repo_path')
                if repo_path:
                    full_path = Path(repo_path) / file_path

            if full_path.exists():
                return full_path.read_text(encoding='utf-8')
        except Exception as e:
            # Silently fail - return None
            pass

        return None

    def _get_file_snippet(self, component: Dict[str, Any]) -> Optional[str]:
        """Get a snippet of the file around the component definition."""
        file_content = self._get_file_content(component.get('file_path'))

        if not file_content:
            return None

        lines = file_content.split('\n')
        line_start = component.get('line_start', 0)
        line_end = component.get('line_end', line_start + 50)

        # Get lines with some context
        context_before = 5
        context_after = 20

        start_idx = max(0, line_start - context_before - 1)
        end_idx = min(len(lines), line_start + context_after)

        snippet_lines = lines[start_idx:end_idx]

        return '\n'.join(snippet_lines)

    def _detect_tech_stack(self, component: Dict[str, Any]) -> str:
        """Detect the technology stack from component metadata."""
        file_path = component.get('file_path', '').lower()
        layer = component.get('layer', '').lower()

        # Backend detection
        if '.ts' in file_path and 'backend' in layer:
            # Check for NestJS indicators
            if any(keyword in file_path for keyword in ['controller', 'service', 'module', 'dto', 'entity']):
                return "NestJS"
            return "TypeScript Backend"

        elif '.cs' in file_path:
            return "C# (.NET/ServiceStack)"

        elif '.java' in file_path:
            return "Java (Spring Boot)"

        elif '.py' in file_path and 'backend' in layer:
            return "Python (FastAPI/Django)"

        elif '.go' in file_path:
            return "Go"

        # Frontend detection
        elif '.tsx' in file_path or '.jsx' in file_path:
            return "React/TypeScript"

        elif '.vue' in file_path:
            return "Vue.js"

        elif '.dart' in file_path:
            return "Flutter/Dart"

        # Default
        return "Unknown Stack"

    def _get_all_related_components(self, component: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get all components related to this one (dependencies + dependents)."""
        component_id = component.get('id')

        related = []
        seen_ids = set()

        # Add dependencies
        for dep in self._get_dependencies(component_id):
            dep_id = dep.get('name')  # Use name as fallback ID
            if dep_id and dep_id not in seen_ids:
                related.append(dep)
                seen_ids.add(dep_id)

        # Add dependents
        for dep in self._get_dependents(component_id):
            dep_id = dep.get('name')
            if dep_id and dep_id not in seen_ids:
                related.append(dep)
                seen_ids.add(dep_id)

        return related

    def merge_contexts(self, context1: Dict[str, Any], context2: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge two contexts together.

        Used when multiple components are selected for prompt generation.
        """
        merged = context1.copy()

        # Merge lists
        for key in ['dependencies', 'dependents', 'related_dtos', 'related_entities',
                    'related_repositories', 'related_controllers', 'related_services',
                    'all_related_components']:
            if key in context2:
                if key not in merged:
                    merged[key] = []

                # Avoid duplicates
                existing_names = {item.get('name') for item in merged[key] if isinstance(item, dict)}
                for item in context2[key]:
                    if isinstance(item, dict) and item.get('name') not in existing_names:
                        merged[key].append(item)

        # Merge file content (concatenate with separator)
        if 'file_content' in context2:
            if 'file_content' in merged:
                merged['file_content'] += f"\n\n{'='*70}\n\n{context2['file_content']}"
            else:
                merged['file_content'] = context2['file_content']

        return merged

    # =========================================================================
    # STRICT MODE ENHANCEMENTS - Constructor Parsing & Validation
    # =========================================================================

    def extract_constructor_dependencies(self, code: str) -> List[str]:
        """
        Extract dependencies from TypeScript/JavaScript constructor.

        Parses patterns like:
        constructor(private readonly repo: RepoService, private service: MyService)

        Returns:
            List of dependency class names (e.g., ['RepoService', 'MyService'])
        """
        if not code:
            return []

        # Find constructor
        pattern = r'constructor\s*\((.*?)\)'
        match = re.search(pattern, code, re.DOTALL)

        if not match:
            return []

        params_block = match.group(1)

        # Extract type annotations (what comes after ':')
        deps = re.findall(r':\s*([A-Za-z0-9_]+)', params_block)

        # Deduplicate and sort
        return sorted(list(set(deps)))

    def detect_stack_strict(self, file_path: str) -> str:
        """
        Detect technology stack from file path with strict categorization.

        Returns:
            'nestjs-backend', 'react-frontend', 'flutter-mobile', or 'unknown'
        """
        file_path_lower = file_path.lower()

        # Backend detection
        if any(keyword in file_path_lower for keyword in [
            'backend', 'backend-service', 'api', 'server', '/services/', '/repositories/'
        ]):
            return 'nestjs-backend'

        # Frontend web detection
        if any(keyword in file_path_lower for keyword in [
            'frontend', 'web', 'react', '/components/', '/pages/', '/hooks/'
        ]):
            return 'react-frontend'

        # Mobile detection
        if any(keyword in file_path_lower for keyword in [
            'mobile', 'flutter', 'dart', '/lib/', '/screens/'
        ]):
            return 'flutter-mobile'

        return 'unknown'

    def categorize_dependencies(self, dependencies: List[Dict[str, Any]]) -> Dict[str, List[Dict]]:
        """
        Categorize dependencies by type (repositories, services, controllers, etc.).

        Args:
            dependencies: List of dependency component dictionaries

        Returns:
            Dict with categorized dependencies:
            {
                'repositories': [...],
                'services': [...],
                'controllers': [...],
                'dtos': [...],
                'entities': [...]
            }
        """
        categorized = {
            'repositories': [],
            'services': [],
            'controllers': [],
            'dtos': [],
            'entities': [],
            'others': []
        }

        for dep in dependencies:
            dep_type = dep.get('type', '').lower()
            dep_name = dep.get('name', '')

            if 'repository' in dep_type or 'Repository' in dep_name:
                categorized['repositories'].append(dep)
            elif 'service' in dep_type or 'Service' in dep_name:
                categorized['services'].append(dep)
            elif 'controller' in dep_type or 'Controller' in dep_name:
                categorized['controllers'].append(dep)
            elif 'dto' in dep_type or 'DTO' in dep_name or 'Dto' in dep_name:
                categorized['dtos'].append(dep)
            elif 'entity' in dep_type or 'Entity' in dep_name:
                categorized['entities'].append(dep)
            else:
                categorized['others'].append(dep)

        # Deduplicate each category
        for category in categorized:
            categorized[category] = self._deduplicate_components(categorized[category])

        return categorized

    def categorize_constructor_dependencies(self, constructor_deps: List[str]) -> Dict[str, List[str]]:
        """
        Categorize constructor dependencies by type based on naming convention.

        Args:
            constructor_deps: List of dependency class names from constructor

        Returns:
            Dict with categorized dependency names:
            {
                'repositories': ['UserRepository', ...],
                'services': ['EmailService', ...],
                ...
            }
        """
        categorized = {
            'repositories': [],
            'services': [],
            'controllers': [],
            'dtos': [],
            'entities': [],
            'others': []
        }

        for dep_name in constructor_deps:
            if 'Repository' in dep_name:
                categorized['repositories'].append(dep_name)
            elif 'Service' in dep_name:
                categorized['services'].append(dep_name)
            elif 'Controller' in dep_name:
                categorized['controllers'].append(dep_name)
            elif 'DTO' in dep_name or 'Dto' in dep_name:
                categorized['dtos'].append(dep_name)
            elif 'Entity' in dep_name:
                categorized['entities'].append(dep_name)
            else:
                categorized['others'].append(dep_name)

        return categorized

    def _deduplicate_components(self, components: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate components based on name."""
        seen_names: Set[str] = set()
        unique_components = []

        for comp in components:
            name = comp.get('name', '')
            if name and name not in seen_names:
                seen_names.add(name)
                unique_components.append(comp)

        return sorted(unique_components, key=lambda x: x.get('name', ''))

    def validate_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and enrich context with strict checks.

        Adds validation errors and warnings to the context.

        Args:
            context: Context dictionary from build_context

        Returns:
            Enhanced context with validation results
        """
        validation = {
            'valid': True,
            'errors': [],
            'warnings': []
        }

        # Check stack detection
        stack = context.get('tech_stack', 'unknown')
        if stack == 'unknown':
            validation['errors'].append(
                "Stack detection failed - cannot determine if backend/frontend"
            )
            validation['valid'] = False

        # Check dependencies
        dependencies = context.get('dependencies', [])
        if not dependencies:
            validation['warnings'].append(
                "No dependencies found - verify constructor parsing or component isolation"
            )

        # Check for duplicates in dependencies
        dep_names = [d.get('name') for d in dependencies]
        if len(dep_names) != len(set(dep_names)):
            validation['errors'].append(
                "Duplicate dependencies detected"
            )
            validation['valid'] = False

        # Check source code availability
        if not context.get('file_content'):
            validation['warnings'].append(
                "Source code not available - prompt may lack implementation details"
            )

        context['validation'] = validation
        return context

    def build_context_strict(self, component_name: str) -> Dict[str, Any]:
        """
        Build context with strict validation and categorization.

        Enhanced version of build_context that:
        - Parses constructor dependencies
        - Strictly detects stack
        - Categorizes dependencies by type
        - Validates context completeness
        - Deduplicates all components

        Args:
            component_name: Name of the component

        Returns:
            Validated and categorized context dictionary
        """
        # Get base context
        context = self.build_context(component_name)

        if 'error' in context:
            return context

        # Extract constructor dependencies from source code
        file_content = context.get('file_content', '')
        constructor_deps = self.extract_constructor_dependencies(file_content)
        context['constructor_dependencies'] = constructor_deps

        # Categorize constructor dependencies for explicit listing
        context['constructor_dependencies_categorized'] = self.categorize_constructor_dependencies(constructor_deps)

        # Strict stack detection
        file_path = context.get('file_path', '')
        context['tech_stack'] = self.detect_stack_strict(file_path)

        # Categorize dependencies
        dependencies = context.get('dependencies', [])
        context['categorized_dependencies'] = self.categorize_dependencies(dependencies)

        # Deduplicate all component lists
        for key in ['dependencies', 'dependents', 'related_dtos', 'related_entities',
                    'related_repositories', 'related_controllers', 'related_services']:
            if key in context:
                context[key] = self._deduplicate_components(context[key])

        # Validate context
        context = self.validate_context(context)

        return context
