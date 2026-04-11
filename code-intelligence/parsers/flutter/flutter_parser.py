"""
Flutter/Dart Parser
Extracts widgets, screens, services, API calls, and navigation from Flutter Dart code.
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Any

_EXCLUDED_DIRS = {
    "node_modules", ".pnpm",
    "dist", "build",
    ".git", ".svn",
    "vendor", "__pycache__",
    ".dart_tool", ".pub-cache", ".pub",
    ".venv", "venv",
    ".turbo", ".cache",
}


def _is_excluded(file_path: Path) -> bool:
    return any(part in _EXCLUDED_DIRS for part in file_path.parts)


class FlutterParser:
    """Parse Flutter/Dart files and extract code intelligence."""

    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.widgets: List[Dict[str, Any]] = []
        self.screens: List[Dict[str, Any]] = []
        self.services: List[Dict[str, Any]] = []
        self.models: List[Dict[str, Any]] = []

    def parse(self) -> Dict[str, Any]:
        """Parse the entire Flutter codebase."""
        # Find all Dart files, excluding dependency/build directories
        dart_files = [f for f in self.repo_path.rglob("*.dart") if not _is_excluded(f)]

        for file_path in dart_files:
            self._parse_file(file_path)

        return {
            "widgets": self.widgets,
            "screens": self.screens,
            "services": self.services,
            "models": self.models,
        }

    def _parse_file(self, file_path: Path):
        """Parse a single Dart file."""
        try:
            content = file_path.read_text(encoding="utf-8")
            relative_path = file_path.relative_to(self.repo_path)

            # Determine file type
            if "/screens/" in str(relative_path) or "_screen.dart" in file_path.name:
                self._parse_screen(content, str(relative_path), file_path)
            elif "/services/" in str(relative_path) or "_service.dart" in file_path.name:
                self._parse_service(content, str(relative_path), file_path)
            elif "/models/" in str(relative_path) or file_path.name.endswith("_request.dart") or file_path.name.endswith("_response.dart"):
                self._parse_model(content, str(relative_path), file_path)
            elif "/widgets/" in str(relative_path) or content.find("extends StatelessWidget") != -1 or content.find("extends StatefulWidget") != -1:
                self._parse_widget(content, str(relative_path), file_path)

        except Exception as e:
            print(f"Error parsing {file_path}: {e}")

    def _parse_widget(self, content: str, relative_path: str, file_path: Path):
        """Parse a Flutter widget."""
        # Extract class name
        class_match = re.search(
            r"class\s+(\w+)\s+extends\s+(StatelessWidget|StatefulWidget)", content
        )

        if not class_match:
            return

        class_name = class_match.group(1)
        widget_type = class_match.group(2)

        # Extract imports
        imports = self._extract_imports(content)

        # Extract build method
        build_method = self._extract_build_method(content)

        # Extract state variables (if StatefulWidget)
        state_vars = []
        if widget_type == "StatefulWidget":
            state_vars = self._extract_state_variables(content)

        # Extract API calls
        api_calls = self._extract_api_calls(content)

        # Extract navigation
        navigation = self._extract_navigation(content)

        # Find line number
        line_number = content[: class_match.start()].count("\n") + 1
        doc_comment = self._extract_doc_comment(content, line_number)

        widget = {
            "id": class_name,
            "name": class_name,
            "type": "widget",
            "widget_type": widget_type,
            "layer": "frontend-mobile",
            "file_path": relative_path,
            "imports": imports,
            "state": state_vars,
            "api_calls": api_calls,
            "navigation": navigation,
            "line_start": line_number,
            "description": doc_comment,
        }

        self.widgets.append(widget)

    def _parse_screen(self, content: str, relative_path: str, file_path: Path):
        """Parse a Flutter screen (special type of widget)."""
        class_match = re.search(
            r"class\s+(\w+)\s+extends\s+(StatelessWidget|StatefulWidget)", content
        )

        if not class_match:
            return

        class_name = class_match.group(1)
        widget_type = class_match.group(2)

        # Extract imports
        imports = self._extract_imports(content)

        # Extract state variables
        state_vars = []
        if widget_type == "StatefulWidget":
            state_vars = self._extract_state_variables(content)

        # Extract API calls
        api_calls = self._extract_api_calls(content)

        # Extract navigation
        navigation = self._extract_navigation(content)

        # Extract event handlers
        event_handlers = self._extract_event_handlers(content)

        # Extract services used
        services_used = self._extract_services_used(content)

        # Find line number
        line_number = content[: class_match.start()].count("\n") + 1
        doc_comment = self._extract_doc_comment(content, line_number)

        screen = {
            "id": class_name,
            "name": class_name,
            "type": "screen",
            "widget_type": widget_type,
            "layer": "frontend-mobile",
            "file_path": relative_path,
            "imports": imports,
            "state": state_vars,
            "api_calls": api_calls,
            "navigation": navigation,
            "event_handlers": event_handlers,
            "services": services_used,
            "line_start": line_number,
            "description": doc_comment,
        }

        self.screens.append(screen)

    def _parse_service(self, content: str, relative_path: str, file_path: Path):
        """Parse a service class."""
        class_match = re.search(r"class\s+(\w+)\s+{", content)

        if not class_match:
            return

        class_name = class_match.group(1)

        # Extract constructor dependencies
        dependencies = self._extract_constructor_dependencies(content, class_name)

        # Extract methods
        methods = self._extract_methods(content)

        # Extract API calls
        api_calls = self._extract_api_calls(content)

        # Find line number
        line_number = content[: class_match.start()].count("\n") + 1
        doc_comment = self._extract_doc_comment(content, line_number)

        service = {
            "id": class_name,
            "name": class_name,
            "type": "service",
            "layer": "frontend-mobile",
            "file_path": relative_path,
            "dependencies": dependencies,
            "methods": methods,
            "api_calls": api_calls,
            "line_start": line_number,
            "description": doc_comment,
        }

        self.services.append(service)

    def _parse_model(self, content: str, relative_path: str, file_path: Path):
        """Parse a model/data class."""
        class_match = re.search(r"class\s+(\w+)\s+{", content)

        if not class_match:
            return

        class_name = class_match.group(1)

        # Extract properties
        properties = self._extract_class_properties(content)

        # Check for JSON serialization methods
        has_from_json = "fromJson" in content
        has_to_json = "toJson" in content

        # Find line number
        line_number = content[: class_match.start()].count("\n") + 1
        doc_comment = self._extract_doc_comment(content, line_number)

        model = {
            "id": class_name,
            "name": class_name,
            "type": "model",
            "layer": "frontend-mobile",
            "file_path": relative_path,
            "properties": properties,
            "serializable": has_from_json and has_to_json,
            "line_start": line_number,
            "description": doc_comment,
        }

        self.models.append(model)

    def _extract_imports(self, content: str) -> List[Dict[str, str]]:
        """Extract import statements."""
        imports = []

        # Pattern: import 'package:...';
        import_pattern = r"import\s+['\"]([^'\"]+)['\"](?:\s+as\s+(\w+))?;"
        matches = re.finditer(import_pattern, content)

        for match in matches:
            import_path = match.group(1)
            alias = match.group(2)

            imports.append({"path": import_path, "alias": alias})

        return imports

    def _extract_build_method(self, content: str) -> Optional[str]:
        """Extract the build method content."""
        pattern = r"Widget\s+build\s*\([^)]*\)\s*{"
        match = re.search(pattern, content)

        if not match:
            return None

        start = match.end()
        brace_count = 1
        i = start

        while i < len(content) and brace_count > 0:
            if content[i] == "{":
                brace_count += 1
            elif content[i] == "}":
                brace_count -= 1
            i += 1

        return content[start : i - 1]

    def _extract_state_variables(self, content: str) -> List[Dict[str, Any]]:
        """Extract state variables from StatefulWidget state class."""
        state_vars = []

        # Find the State class
        state_class_pattern = r"class\s+_\w+State\s+extends\s+State<\w+>\s*{"
        state_match = re.search(state_class_pattern, content)

        if not state_match:
            return state_vars

        # Find all field declarations in the State class
        # Pattern: Type variableName; or Type? variableName;
        var_pattern = r"(\w+\??)\s+(\w+)\s*(?:=|;)"
        matches = re.finditer(var_pattern, content[state_match.end() :])

        for match in matches:
            var_type = match.group(1)
            var_name = match.group(2)
            line_number = content[: state_match.end() + match.start()].count("\n") + 1

            # Filter out method names (basic heuristic)
            if not var_name.startswith("_") or var_name.endswith("Controller"):
                state_vars.append(
                    {
                        "name": var_name,
                        "type": var_type,
                        "line_number": line_number,
                    }
                )

        return state_vars

    def _extract_api_calls(self, content: str) -> List[Dict[str, Any]]:
        """Extract API calls."""
        api_calls = []

        # Pattern: client.get('/path') or client.post('/path')
        client_pattern = r"(\w+)\.(get|post|put|delete)\(['\"]([^'\"]+)['\"]"
        matches = re.finditer(client_pattern, content)

        for match in matches:
            client = match.group(1)
            method = match.group(2).upper()
            endpoint = match.group(3)
            line_number = content[: match.start()].count("\n") + 1

            api_calls.append(
                {
                    "client": client,
                    "method": method,
                    "endpoint": endpoint,
                    "line_number": line_number,
                }
            )

        return api_calls

    def _extract_navigation(self, content: str) -> List[Dict[str, Any]]:
        """Extract navigation calls."""
        navigation = []

        # Pattern: Navigator.of(context).push...
        # Pattern: Navigator.pushNamed(context, '/route')
        nav_patterns = [
            r"Navigator\.(?:of\([^)]+\)\.)?push(?:Named)?\([^,]+,\s*(?:MaterialPageRoute\([^)]*builder:[^)]*=>|['\"]([^'\"]+)['\"])",
            r"Navigator\.(?:of\([^)]+\)\.)?pushReplacement(?:Named)?\([^,]+,\s*(?:MaterialPageRoute\([^)]*builder:[^)]*=>|['\"]([^'\"]+)['\"])",
        ]

        for pattern in nav_patterns:
            matches = re.finditer(pattern, content)

            for match in matches:
                route = match.group(1) if match.group(1) else "MaterialPageRoute"
                line_number = content[: match.start()].count("\n") + 1

                # Try to extract widget type from MaterialPageRoute
                widget_match = re.search(r"builder:[^)]*=>\s*(\w+)\(", match.group(0))
                if widget_match:
                    route = widget_match.group(1)

                navigation.append({"route": route, "line_number": line_number})

        return navigation

    def _extract_event_handlers(self, content: str) -> List[Dict[str, Any]]:
        """Extract event handler methods."""
        handlers = []

        # Pattern: Future<void> _handleSomething() async {
        # Pattern: void _onSomething() {
        handler_pattern = r"(?:Future<void>|void)\s+(_handle\w+|_on\w+)\s*\([^)]*\)"
        matches = re.finditer(handler_pattern, content)

        for match in matches:
            handler_name = match.group(1)
            line_number = content[: match.start()].count("\n") + 1

            # Extract method body to find what it calls
            method_body = self._extract_method_body(content, handler_name)
            calls = self._extract_method_calls(method_body)

            handlers.append(
                {
                    "name": handler_name,
                    "calls": calls,
                    "line_number": line_number,
                }
            )

        return handlers

    def _extract_services_used(self, content: str) -> List[str]:
        """Extract services used via Provider or dependency injection."""
        services = []

        # Pattern: Provider.of<ServiceName>(context)
        provider_pattern = r"Provider\.of<(\w+)>\(context"
        matches = re.findall(provider_pattern, content)
        services.extend(matches)

        return list(set(services))

    def _extract_constructor_dependencies(
        self, content: str, class_name: str
    ) -> List[Dict[str, str]]:
        """Extract constructor parameters."""
        dependencies = []

        # Pattern: ClassName(this.dependency1, this.dependency2)
        constructor_pattern = (
            rf"{class_name}\s*\(\s*{{([^}}]+)}}\s*\)|{class_name}\s*\(([^)]+)\)"
        )
        match = re.search(constructor_pattern, content)

        if not match:
            return dependencies

        params = match.group(1) or match.group(2)

        # Extract named parameters
        param_pattern = r"(?:required\s+)?(?:this\.)?(\w+)"
        param_matches = re.findall(param_pattern, params)

        for param in param_matches:
            if param and param != "required":
                dependencies.append({"name": param})

        return dependencies

    def _extract_methods(self, content: str) -> List[Dict[str, Any]]:
        """Extract method declarations."""
        methods = []

        # Pattern: Future<Type> methodName(...) async {
        # Pattern: Type methodName(...) {
        method_pattern = r"(?:Future<\w+>|\w+)\s+(\w+)\s*\([^)]*\)"
        matches = re.finditer(method_pattern, content)

        for match in matches:
            method_name = match.group(1)

            # Skip constructors and common keywords
            if method_name in ["class", "if", "for", "while", "return"]:
                continue

            line_number = content[: match.start()].count("\n") + 1

            # Extract method body
            method_body = self._extract_method_body(content, method_name)
            calls = self._extract_method_calls(method_body)

            methods.append(
                {
                    "name": method_name,
                    "calls": calls,
                    "line_number": line_number,
                }
            )

        return methods

    def _extract_class_properties(self, content: str) -> List[Dict[str, Any]]:
        """Extract class properties."""
        properties = []

        # Pattern: final Type propertyName;
        prop_pattern = r"(?:final|const)?\s+(\w+\??)\s+(\w+)\s*;"
        matches = re.finditer(prop_pattern, content)

        for match in matches:
            prop_type = match.group(1)
            prop_name = match.group(2)
            line_number = content[: match.start()].count("\n") + 1

            properties.append(
                {
                    "name": prop_name,
                    "type": prop_type,
                    "line_number": line_number,
                }
            )

        return properties

    def _extract_method_body(self, content: str, method_name: str) -> str:
        """Extract method body."""
        pattern = rf"\b{method_name}\s*\([^)]*\)[^{{]*{{"
        match = re.search(pattern, content)

        if not match:
            return ""

        start = match.end()
        brace_count = 1
        i = start

        while i < len(content) and brace_count > 0:
            if content[i] == "{":
                brace_count += 1
            elif content[i] == "}":
                brace_count -= 1
            i += 1

        return content[start : i - 1]

    def _extract_method_calls(self, method_body: str) -> List[str]:
        """Extract method calls from a method body."""
        # Pattern: serviceName.methodName( or await serviceName.methodName(
        call_pattern = r"(?:await\s+)?(\w+)\.(\w+)\("
        matches = re.findall(call_pattern, method_body)

        return [f"{service}.{method}" for service, method in matches]

    def _extract_doc_comment(self, content: str, line_number: int) -> Optional[str]:
        """Extract documentation comment above a line."""
        if line_number < 2:
            return None

        lines = content.split("\n")
        comment_lines = []

        for i in range(line_number - 2, -1, -1):
            line = lines[i].strip()
            if line.startswith("///") or line.startswith("//"):
                comment_lines.insert(0, line)
            else:
                break

        if comment_lines:
            cleaned = "\n".join(comment_lines)
            cleaned = re.sub(r"///|//", "", cleaned).strip()
            return cleaned

        return None
