"""
Angular Parser
Extracts components, services, NgRx state management, GraphQL operations, and integrations from Angular TypeScript code.
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Any

_EXCLUDED_DIRS = {
    "node_modules", ".pnpm", ".npm",
    "dist", "build", ".next", "out",
    ".git", ".svn",
    "vendor", "__pycache__",
    ".venv", "venv",
    "coverage", ".nyc_output",
    ".turbo", ".cache",
}


def _is_excluded(file_path: Path) -> bool:
    return any(part in _EXCLUDED_DIRS for part in file_path.parts)


class AngularParser:
    """Parse Angular TypeScript files and extract code intelligence."""

    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.components: List[Dict[str, Any]] = []
        self.services: List[Dict[str, Any]] = []
        self.ngrx_items: List[Dict[str, Any]] = []
        self.graphql_operations: List[Dict[str, Any]] = []
        self.modules: List[Dict[str, Any]] = []
        self.directives: List[Dict[str, Any]] = []
        self.pipes: List[Dict[str, Any]] = []
        self.guards: List[Dict[str, Any]] = []
        self.resolvers: List[Dict[str, Any]] = []
        self.interceptors: List[Dict[str, Any]] = []

    def parse(self) -> Dict[str, Any]:
        """Parse the entire Angular codebase."""
        # Find all TypeScript files, excluding dependency/build directories
        ts_files = [f for f in self.repo_path.rglob("*.ts") if not _is_excluded(f)]

        for file_path in ts_files:
            self._parse_file(file_path)

        return {
            "components": self.components,
            "services": self.services,
            "ngrx_items": self.ngrx_items,
            "graphql_operations": self.graphql_operations,
            "modules": self.modules,
            "directives": self.directives,
            "pipes": self.pipes,
            "guards": self.guards,
            "resolvers": self.resolvers,
            "interceptors": self.interceptors,
        }

    def _parse_file(self, file_path: Path):
        """Parse a single Angular TypeScript file."""
        try:
            content = file_path.read_text(encoding="utf-8")
            relative_path = file_path.relative_to(self.repo_path)

            # Skip test files
            if ".spec.ts" in file_path.name or ".test.ts" in file_path.name:
                return

            # Determine file type based on patterns
            if ".component.ts" in file_path.name:
                self._parse_component(content, str(relative_path), file_path)
            elif ".service.ts" in file_path.name:
                self._parse_service(content, str(relative_path), file_path)
            elif ".module.ts" in file_path.name:
                self._parse_module(content, str(relative_path), file_path)
            elif ".directive.ts" in file_path.name:
                self._parse_directive(content, str(relative_path), file_path)
            elif ".pipe.ts" in file_path.name:
                self._parse_pipe(content, str(relative_path), file_path)
            elif ".guard.ts" in file_path.name:
                self._parse_guard(content, str(relative_path), file_path)
            elif ".resolver.ts" in file_path.name:
                self._parse_resolver(content, str(relative_path), file_path)
            elif "interceptor" in file_path.name.lower():
                self._parse_interceptor(content, str(relative_path), file_path)
            elif any(pattern in content for pattern in ["createAction", "createReducer", "createSelector", "createFeature"]):
                self._parse_ngrx(content, str(relative_path), file_path)
            elif any(pattern in content for pattern in ["gql`", "graphql", "Apollo"]):
                self._parse_graphql(content, str(relative_path), file_path)

        except Exception as e:
            print(f"Error parsing {file_path}: {e}")

    def _parse_component(self, content: str, relative_path: str, file_path: Path):
        """Parse an Angular component."""
        # Extract component class name
        class_match = re.search(r"export\s+class\s+(\w+)\s", content)
        if not class_match:
            return

        class_name = class_match.group(1)

        # Extract @Component decorator
        component_decorator = re.search(
            r"@Component\(\s*\{([^}]*)\}\s*\)", content, re.DOTALL
        )
        
        metadata = {}
        if component_decorator:
            decorator_content = component_decorator.group(1)
            
            # Extract selector
            selector_match = re.search(r"selector:\s*['\"]([^'\"]+)['\"]", decorator_content)
            metadata["selector"] = selector_match.group(1) if selector_match else None
            
            # Extract templateUrl or template
            template_url_match = re.search(r"templateUrl:\s*['\"]([^'\"]+)['\"]", decorator_content)
            metadata["template_url"] = template_url_match.group(1) if template_url_match else None
            
            # Extract styleUrls
            style_urls_match = re.search(r"styleUrls:\s*\[([^\]]+)\]", decorator_content)
            if style_urls_match:
                metadata["style_urls"] = [url.strip().strip("'\"") for url in style_urls_match.group(1).split(",")]

        # Extract constructor dependencies
        dependencies = self._extract_constructor_dependencies(content)

        # Extract Angular Material usage
        material_components = self._extract_material_usage(content)

        # Extract NgRx usage
        ngrx_usage = self._extract_ngrx_in_component(content)

        # Extract GraphQL/Apollo usage
        graphql_usage = self._extract_graphql_in_component(content)

        # Extract Socket.io usage
        socket_usage = self._extract_socket_usage(content)

        # Extract third-party integrations
        integrations = self._extract_integrations(content)

        # Extract lifecycle hooks
        lifecycle_hooks = self._extract_lifecycle_hooks(content)

        # Extract @Input and @Output
        inputs = self._extract_inputs(content)
        outputs = self._extract_outputs(content)

        line_number = self._get_class_line_number(content, class_name)
        doc_comment = self._extract_doc_comment(content, line_number)

        component = {
            "id": class_name,
            "name": class_name,
            "type": "component",
            "layer": "frontend-web",
            "file_path": relative_path,
            "selector": metadata.get("selector"),
            "template_url": metadata.get("template_url"),
            "style_urls": metadata.get("style_urls", []),
            "dependencies": dependencies,
            "material_components": material_components,
            "ngrx": ngrx_usage,
            "graphql": graphql_usage,
            "socket_io": socket_usage,
            "integrations": integrations,
            "lifecycle_hooks": lifecycle_hooks,
            "inputs": inputs,
            "outputs": outputs,
            "line_start": line_number,
            "description": doc_comment,
        }

        self.components.append(component)

    def _parse_service(self, content: str, relative_path: str, file_path: Path):
        """Parse an Angular service."""
        class_match = re.search(r"export\s+class\s+(\w+)\s", content)
        if not class_match:
            return

        class_name = class_match.group(1)

        # Check if it's actually a service (has @Injectable)
        if "@Injectable" not in content:
            return

        # Extract constructor dependencies
        dependencies = self._extract_constructor_dependencies(content)

        # Extract HTTP methods
        http_methods = self._extract_http_methods(content)

        # Extract Apollo/GraphQL operations
        graphql_operations = self._extract_graphql_operations(content)

        # Extract Socket.io usage
        socket_usage = self._extract_socket_usage(content)

        # Extract third-party integrations
        integrations = self._extract_service_integrations(content)

        # Extract methods
        methods = self._extract_service_methods(content)

        line_number = self._get_class_line_number(content, class_name)
        doc_comment = self._extract_doc_comment(content, line_number)

        service = {
            "id": class_name,
            "name": class_name,
            "type": "service",
            "layer": "frontend-web",
            "file_path": relative_path,
            "dependencies": dependencies,
            "http_methods": http_methods,
            "graphql_operations": graphql_operations,
            "socket_io": socket_usage,
            "integrations": integrations,
            "methods": methods,
            "line_start": line_number,
            "description": doc_comment,
        }

        self.services.append(service)

    def _parse_ngrx(self, content: str, relative_path: str, file_path: Path):
        """Parse NgRx store files (actions, reducers, selectors, effects)."""
        file_name = file_path.name

        if "action" in file_name.lower():
            self._parse_ngrx_actions(content, relative_path, file_path)
        elif "reducer" in file_name.lower():
            self._parse_ngrx_reducer(content, relative_path, file_path)
        elif "selector" in file_name.lower():
            self._parse_ngrx_selectors(content, relative_path, file_path)
        elif "effect" in file_name.lower():
            self._parse_ngrx_effects(content, relative_path, file_path)
        elif "state" in file_name.lower() or "feature" in file_name.lower():
            self._parse_ngrx_feature(content, relative_path, file_path)

    def _parse_ngrx_actions(self, content: str, relative_path: str, file_path: Path):
        """Parse NgRx actions."""
        # Extract createAction calls
        action_pattern = r"export\s+const\s+(\w+)\s*=\s*createAction\s*\(\s*['\"]([^'\"]+)['\"]"
        matches = re.finditer(action_pattern, content)

        for match in matches:
            action_name = match.group(1)
            action_type = match.group(2)
            line_number = content[:match.start()].count("\n") + 1

            self.ngrx_items.append({
                "id": action_name,
                "name": action_name,
                "type": "ngrx_action",
                "layer": "frontend-web",
                "file_path": relative_path,
                "action_type": action_type,
                "line_start": line_number,
            })

    def _parse_ngrx_reducer(self, content: str, relative_path: str, file_path: Path):
        """Parse NgRx reducer."""
        # Extract createReducer
        reducer_match = re.search(
            r"export\s+const\s+(\w+)\s*=\s*createReducer\(([^)]+)", content, re.DOTALL
        )
        
        if reducer_match:
            reducer_name = reducer_match.group(1)
            line_number = content[:reducer_match.start()].count("\n") + 1

            # Extract on() handlers
            on_handlers = re.findall(
                r"on\(\s*(\w+)\s*,\s*\([^)]*\)\s*=>\s*\{([^}]+)\}", content
            )

            self.ngrx_items.append({
                "id": reducer_name,
                "name": reducer_name,
                "type": "ngrx_reducer",
                "layer": "frontend-web",
                "file_path": relative_path,
                "handlers": [handler[0] for handler in on_handlers],
                "line_start": line_number,
            })

    def _parse_ngrx_selectors(self, content: str, relative_path: str, file_path: Path):
        """Parse NgRx selectors."""
        # Extract createSelector and createFeatureSelector
        selector_pattern = r"export\s+const\s+(\w+)\s*=\s*create(?:Feature)?Selector"
        matches = re.finditer(selector_pattern, content)

        for match in matches:
            selector_name = match.group(1)
            line_number = content[:match.start()].count("\n") + 1

            self.ngrx_items.append({
                "id": selector_name,
                "name": selector_name,
                "type": "ngrx_selector",
                "layer": "frontend-web",
                "file_path": relative_path,
                "line_start": line_number,
            })

    def _parse_ngrx_effects(self, content: str, relative_path: str, file_path: Path):
        """Parse NgRx effects."""
        # Extract @Injectable effects class
        class_match = re.search(r"export\s+class\s+(\w+)\s", content)
        if not class_match:
            return

        class_name = class_match.group(1)
        line_number = content[:class_match.start()].count("\n") + 1

        # Extract createEffect calls
        effect_pattern = r"(\w+)\s*=\s*createEffect\(\s*\(\)\s*=>"
        effects = re.findall(effect_pattern, content)

        self.ngrx_items.append({
            "id": class_name,
            "name": class_name,
            "type": "ngrx_effects",
            "layer": "frontend-web",
            "file_path": relative_path,
            "effects": effects,
            "line_start": line_number,
        })

    def _parse_ngrx_feature(self, content: str, relative_path: str, file_path: Path):
        """Parse NgRx feature state."""
        # Extract createFeature
        feature_match = re.search(
            r"export\s+const\s+(\w+)\s*=\s*createFeature\(", content
        )
        
        if feature_match:
            feature_name = feature_match.group(1)
            line_number = content[:feature_match.start()].count("\n") + 1

            self.ngrx_items.append({
                "id": feature_name,
                "name": feature_name,
                "type": "ngrx_feature",
                "layer": "frontend-web",
                "file_path": relative_path,
                "line_start": line_number,
            })

    def _parse_graphql(self, content: str, relative_path: str, file_path: Path):
        """Parse GraphQL operations (queries, mutations, subscriptions)."""
        # Extract gql tagged template literals
        gql_pattern = r"(export\s+)?const\s+(\w+)\s*=\s*gql`([^`]+)`"
        matches = re.finditer(gql_pattern, content, re.DOTALL)

        for match in matches:
            operation_name = match.group(2)
            gql_content = match.group(3)
            line_number = content[:match.start()].count("\n") + 1

            # Determine operation type
            operation_type = "query"
            if "mutation" in gql_content.lower():
                operation_type = "mutation"
            elif "subscription" in gql_content.lower():
                operation_type = "subscription"

            self.graphql_operations.append({
                "id": operation_name,
                "name": operation_name,
                "type": "graphql_operation",
                "layer": "frontend-web",
                "file_path": relative_path,
                "operation_type": operation_type,
                "gql": gql_content.strip(),
                "line_start": line_number,
            })

    def _parse_module(self, content: str, relative_path: str, file_path: Path):
        """Parse an Angular module."""
        class_match = re.search(r"export\s+class\s+(\w+)\s", content)
        if not class_match:
            return

        class_name = class_match.group(1)

        # Check if it's actually a module (has @NgModule)
        if "@NgModule" not in content:
            return

        # Extract @NgModule metadata
        ngmodule_match = re.search(r"@NgModule\(\s*\{([^}]*)\}\s*\)", content, re.DOTALL)
        metadata = {}
        
        if ngmodule_match:
            decorator_content = ngmodule_match.group(1)
            
            # Extract declarations
            declarations_match = re.search(r"declarations:\s*\[([^\]]+)\]", decorator_content)
            if declarations_match:
                metadata["declarations"] = [d.strip() for d in declarations_match.group(1).split(",")]
            
            # Extract imports
            imports_match = re.search(r"imports:\s*\[([^\]]+)\]", decorator_content)
            if imports_match:
                metadata["imports"] = [i.strip() for i in imports_match.group(1).split(",")]
            
            # Extract providers
            providers_match = re.search(r"providers:\s*\[([^\]]+)\]", decorator_content)
            if providers_match:
                metadata["providers"] = [p.strip() for p in providers_match.group(1).split(",")]
            
            # Extract exports
            exports_match = re.search(r"exports:\s*\[([^\]]+)\]", decorator_content)
            if exports_match:
                metadata["exports"] = [e.strip() for e in exports_match.group(1).split(",")]

        line_number = self._get_class_line_number(content, class_name)

        module = {
            "id": class_name,
            "name": class_name,
            "type": "module",
            "layer": "frontend-web",
            "file_path": relative_path,
            "declarations": metadata.get("declarations", []),
            "imports": metadata.get("imports", []),
            "providers": metadata.get("providers", []),
            "exports": metadata.get("exports", []),
            "line_start": line_number,
        }

        self.modules.append(module)

    def _parse_directive(self, content: str, relative_path: str, file_path: Path):
        """Parse an Angular directive."""
        class_match = re.search(r"export\s+class\s+(\w+)\s", content)
        if not class_match or "@Directive" not in content:
            return

        class_name = class_match.group(1)
        line_number = self._get_class_line_number(content, class_name)

        # Extract selector
        selector_match = re.search(r"selector:\s*['\"]([^'\"]+)['\"]", content)
        selector = selector_match.group(1) if selector_match else None

        self.directives.append({
            "id": class_name,
            "name": class_name,
            "type": "directive",
            "layer": "frontend-web",
            "file_path": relative_path,
            "selector": selector,
            "line_start": line_number,
        })

    def _parse_pipe(self, content: str, relative_path: str, file_path: Path):
        """Parse an Angular pipe."""
        class_match = re.search(r"export\s+class\s+(\w+)\s", content)
        if not class_match or "@Pipe" not in content:
            return

        class_name = class_match.group(1)
        line_number = self._get_class_line_number(content, class_name)

        # Extract pipe name
        name_match = re.search(r"name:\s*['\"]([^'\"]+)['\"]", content)
        pipe_name = name_match.group(1) if name_match else None

        self.pipes.append({
            "id": class_name,
            "name": class_name,
            "type": "pipe",
            "layer": "frontend-web",
            "file_path": relative_path,
            "pipe_name": pipe_name,
            "line_start": line_number,
        })

    def _parse_guard(self, content: str, relative_path: str, file_path: Path):
        """Parse an Angular route guard."""
        class_match = re.search(r"export\s+class\s+(\w+)\s", content)
        if not class_match:
            return

        class_name = class_match.group(1)
        line_number = self._get_class_line_number(content, class_name)

        # Check if it implements CanActivate, CanDeactivate, etc.
        guard_types = []
        if "CanActivate" in content:
            guard_types.append("CanActivate")
        if "CanDeactivate" in content:
            guard_types.append("CanDeactivate")
        if "CanLoad" in content:
            guard_types.append("CanLoad")
        if "CanActivateChild" in content:
            guard_types.append("CanActivateChild")

        self.guards.append({
            "id": class_name,
            "name": class_name,
            "type": "guard",
            "layer": "frontend-web",
            "file_path": relative_path,
            "guard_types": guard_types,
            "line_start": line_number,
        })

    def _parse_resolver(self, content: str, relative_path: str, file_path: Path):
        """Parse an Angular route resolver."""
        class_match = re.search(r"export\s+class\s+(\w+)\s", content)
        if not class_match or "Resolve<" not in content:
            return

        class_name = class_match.group(1)
        line_number = self._get_class_line_number(content, class_name)

        self.resolvers.append({
            "id": class_name,
            "name": class_name,
            "type": "resolver",
            "layer": "frontend-web",
            "file_path": relative_path,
            "line_start": line_number,
        })

    def _parse_interceptor(self, content: str, relative_path: str, file_path: Path):
        """Parse an HTTP interceptor."""
        class_match = re.search(r"export\s+class\s+(\w+)\s", content)
        if not class_match:
            return

        class_name = class_match.group(1)
        
        # Check if it implements HttpInterceptor
        if "HttpInterceptor" not in content:
            return

        line_number = self._get_class_line_number(content, class_name)

        self.interceptors.append({
            "id": class_name,
            "name": class_name,
            "type": "interceptor",
            "layer": "frontend-web",
            "file_path": relative_path,
            "line_start": line_number,
        })

    def _extract_constructor_dependencies(self, content: str) -> List[Dict[str, Any]]:
        """Extract constructor dependencies."""
        dependencies = []
        
        constructor_match = re.search(
            r"constructor\((.*?)\)\s*\{", content, re.DOTALL
        )
        
        if constructor_match:
            params = constructor_match.group(1)
            # Match patterns like: private service: ServiceName
            dep_matches = re.findall(
                r"(?:private|public|protected)\s+(\w+):\s+(\w+)",
                params,
            )
            dependencies = [
                {"name": dep[0], "type": dep[1]} for dep in dep_matches
            ]

        return dependencies

    def _extract_material_usage(self, content: str) -> List[str]:
        """Extract Angular Material components used."""
        material_components = []
        
        # Common Material component selectors
        material_patterns = [
            "mat-button", "mat-raised-button", "mat-icon-button",
            "mat-card", "mat-form-field", "mat-input",
            "mat-select", "mat-option", "mat-checkbox",
            "mat-radio", "mat-slide-toggle", "mat-slider",
            "mat-datepicker", "mat-table", "mat-paginator",
            "mat-sort", "mat-dialog", "mat-snack-bar",
            "mat-toolbar", "mat-sidenav", "mat-list",
            "mat-grid-list", "mat-tab", "mat-expansion-panel",
            "mat-menu", "mat-autocomplete", "mat-chip",
            "mat-progress-bar", "mat-spinner", "mat-icon",
        ]
        
        for pattern in material_patterns:
            if pattern in content.lower():
                material_components.append(pattern)

        return material_components

    def _extract_ngrx_in_component(self, content: str) -> Dict[str, Any]:
        """Extract NgRx usage in a component."""
        usage = {
            "store_injected": "store" in content and "Store" in content,
            "dispatches": re.findall(r"this\.store\.dispatch\((\w+)", content),
            "selects": re.findall(r"this\.store\.select\((\w+)\)", content),
        }
        return usage

    def _extract_graphql_in_component(self, content: str) -> List[str]:
        """Extract GraphQL operations in component."""
        operations = []
        
        # Apollo query/mutation/subscription patterns
        if "apollo.watchQuery" in content or "this.apollo.query" in content:
            operations.append("query")
        if "apollo.mutate" in content or "this.apollo.mutate" in content:
            operations.append("mutation")
        if "apollo.subscribe" in content or "this.apollo.subscribe" in content:
            operations.append("subscription")

        return operations

    def _extract_graphql_operations(self, content: str) -> List[Dict[str, Any]]:
        """Extract GraphQL operations from a service."""
        operations = []
        
        # Look for methods that use Apollo
        method_pattern = r"(\w+)\s*\([^)]*\)[^{]*\{[^}]*apollo\.(query|mutate|subscribe)"
        matches = re.finditer(method_pattern, content, re.DOTALL)
        
        for match in matches:
            method_name = match.group(1)
            operation_type = match.group(2)
            operations.append({
                "method": method_name,
                "type": operation_type,
            })

        return operations

    def _extract_socket_usage(self, content: str) -> Dict[str, Any]:
        """Extract Socket.io usage."""
        usage = {
            "socket_injected": "Socket" in content or "socket" in content,
            "emits": re.findall(r"socket\.emit\(['\"]([^'\"]+)['\"]", content),
            "listeners": re.findall(r"socket\.on\(['\"]([^'\"]+)['\"]", content),
        }
        return usage

    def _extract_integrations(self, content: str) -> Dict[str, Any]:
        """Extract third-party integration usage in components."""
        integrations = {}

        # Google Maps
        if "GoogleMap" in content or "@angular/google-maps" in content:
            integrations["google_maps"] = True

        # Stripe
        if "Stripe" in content or "ngx-stripe" in content:
            integrations["stripe"] = True

        # Twilio
        if "Twilio" in content:
            integrations["twilio"] = True

        # Plaid
        if "Plaid" in content or "ngx-plaid-link" in content:
            integrations["plaid"] = True

        # Highcharts
        if "Highcharts" in content or "highcharts-angular" in content:
            integrations["highcharts"] = True

        # Rich text (Quill)
        if "Quill" in content or "ngx-quill" in content:
            integrations["quill"] = True

        # Color picker
        if "ColorPicker" in content or "ngx-color-picker" in content:
            integrations["color_picker"] = True

        # Date range picker
        if "Daterangepicker" in content or "ngx-daterangepicker" in content:
            integrations["date_picker"] = True

        return integrations

    def _extract_service_integrations(self, content: str) -> Dict[str, Any]:
        """Extract third-party integrations from services."""
        integrations = {}

        # Check imports and usage
        if "@stripe/stripe-js" in content or "stripe" in content.lower():
            integrations["stripe"] = True

        if "@googlemaps" in content or "google.maps" in content:
            integrations["google_maps"] = True

        if "twilio" in content.lower():
            integrations["twilio"] = True

        if "plaid" in content.lower():
            integrations["plaid"] = True

        if "highcharts" in content.lower():
            integrations["highcharts"] = True

        return integrations

    def _extract_lifecycle_hooks(self, content: str) -> List[str]:
        """Extract Angular lifecycle hooks implemented."""
        hooks = []
        lifecycle_methods = [
            "ngOnInit", "ngOnChanges", "ngDoCheck", "ngAfterContentInit",
            "ngAfterContentChecked", "ngAfterViewInit", "ngAfterViewChecked",
            "ngOnDestroy"
        ]
        
        for hook in lifecycle_methods:
            if hook in content:
                hooks.append(hook)

        return hooks

    def _extract_inputs(self, content: str) -> List[Dict[str, Any]]:
        """Extract @Input properties."""
        inputs = []
        
        # Pattern: @Input() propName: type
        input_pattern = r"@Input\(\)[^\w]*(\w+)\s*:\s*(\w+)"
        matches = re.finditer(input_pattern, content)
        
        for match in matches:
            inputs.append({
                "name": match.group(1),
                "type": match.group(2),
            })

        return inputs

    def _extract_outputs(self, content: str) -> List[Dict[str, Any]]:
        """Extract @Output properties."""
        outputs = []
        
        # Pattern: @Output() eventName = new EventEmitter<type>()
        output_pattern = r"@Output\(\)[^\w]*(\w+)\s*="
        matches = re.finditer(output_pattern, content)
        
        for match in matches:
            outputs.append({
                "name": match.group(1),
            })

        return outputs

    def _extract_http_methods(self, content: str) -> List[Dict[str, Any]]:
        """Extract HTTP methods from HttpClient."""
        methods = []
        
        http_pattern = r"this\.http\.(get|post|put|delete|patch)\s*\(\s*['\"]([^'\"]+)['\"]"
        matches = re.finditer(http_pattern, content)
        
        for match in matches:
            methods.append({
                "method": match.group(1).upper(),
                "url": match.group(2),
            })

        return methods

    def _extract_service_methods(self, content: str) -> List[Dict[str, Any]]:
        """Extract public methods from a service."""
        methods = []
        
        # Pattern for public methods
        method_pattern = r"(?:async\s+)?(\w+)\s*\([^)]*\)\s*:\s*(?:Observable|Promise)?[<\w\[\]]*\s*\{"
        matches = re.finditer(method_pattern, content)
        
        for match in matches:
            method_name = match.group(1)
            if method_name not in ["constructor"]:
                line_number = content[:match.start()].count("\n") + 1
                methods.append({
                    "name": method_name,
                    "line_number": line_number,
                })

        return methods

    def _get_class_line_number(self, content: str, class_name: str) -> int:
        """Get line number where class is defined."""
        pattern = rf"export\s+class\s+{class_name}"
        match = re.search(pattern, content)
        if match:
            return content[:match.start()].count("\n") + 1
        return 0

    def _extract_doc_comment(self, content: str, line_number: int) -> Optional[str]:
        """Extract documentation comment above a line."""
        if line_number < 2:
            return None

        lines = content.split("\n")
        comment_lines = []

        for i in range(line_number - 2, -1, -1):
            line = lines[i].strip()
            if line.startswith("/**") or line.startswith("*") or line.startswith("//"):
                comment_lines.insert(0, line)
            else:
                break

        if comment_lines:
            cleaned = "\n".join(comment_lines)
            cleaned = re.sub(r"\/\*\*|\*\/|\*|\/\/", "", cleaned).strip()
            return cleaned

        return None
