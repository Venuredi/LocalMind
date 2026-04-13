"""
Go Framework Parser (Gin/Echo/Chi)
Extracts handlers, services, repositories, and routes from Go code.
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Any


class GoParser:
    """Parse Go backend files and extract code intelligence."""

    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.handlers: List[Dict[str, Any]] = []
        self.services: List[Dict[str, Any]] = []
        self.repositories: List[Dict[str, Any]] = []
        self.models: List[Dict[str, Any]] = []
        self.routes: List[Dict[str, Any]] = []

    def parse(self) -> Dict[str, Any]:
        """Parse the entire Go codebase."""
        go_files = list(self.repo_path.rglob("*.go"))

        for file_path in go_files:
            self._parse_file(file_path)

        return {
            "handlers": self.handlers,
            "services": self.services,
            "repositories": self.repositories,
            "models": self.models,
            "routes": self.routes,
        }

    def _parse_file(self, file_path: Path):
        """Parse a single Go file."""
        try:
            content = file_path.read_text(encoding="utf-8")
            relative_path = file_path.relative_to(self.repo_path)

            # Determine file type and parse accordingly
            if "handler" in str(file_path).lower() or "/handlers/" in str(file_path):
                self._parse_handler(content, str(relative_path), file_path)
            elif "service" in str(file_path).lower() or "/services/" in str(file_path):
                self._parse_service(content, str(relative_path), file_path)
            elif "repository" in str(file_path).lower() or "repo" in str(file_path).lower():
                self._parse_repository(content, str(relative_path), file_path)
            elif "model" in str(file_path).lower() or "/models/" in str(file_path):
                self._parse_model(content, str(relative_path), file_path)
            elif "route" in str(file_path).lower() or "router" in str(file_path).lower():
                self._parse_routes(content, str(relative_path), file_path)

        except Exception as e:
            print(f"Error parsing {file_path}: {e}")

    def _parse_handler(self, content: str, relative_path: str, file_path: Path):
        """Parse a Go handler file."""
        # Extract struct name (e.g., type UserHandler struct)
        struct_match = re.search(r"type\s+(\w+Handler)\s+struct\s*{(.*?)}", content, re.DOTALL)
        if not struct_match:
            return

        handler_name = struct_match.group(1)
        struct_fields = struct_match.group(2)

        # Extract dependencies from struct fields
        dependencies = []
        dep_matches = re.findall(r'(\w+)\s+\*?(\w+(?:Service|Repository|Logger|Client))', struct_fields)
        for dep in dep_matches:
            dependencies.append({"name": dep[0], "type": dep[1]})

        # Extract handler methods (functions with receiver)
        methods = self._extract_handler_methods(content, handler_name)

        # Try to find constructor function (NewXxxHandler)
        constructor_match = re.search(
            rf"func\s+New{handler_name}\s*\((.*?)\)\s*\*?{handler_name}",
            content,
            re.DOTALL
        )
        constructor_deps = []
        if constructor_match:
            params = constructor_match.group(1)
            dep_matches = re.findall(r'(\w+)\s+\*?(\w+)', params)
            constructor_deps = [{"name": dep[0], "type": dep[1]} for dep in dep_matches]

        handler = {
            "id": handler_name,
            "name": handler_name,
            "type": "handler",
            "layer": "backend",
            "file_path": relative_path,
            "dependencies": dependencies or constructor_deps,
            "methods": methods,
            "tech_stack": "go-backend"
        }

        self.handlers.append(handler)

    def _extract_handler_methods(self, content: str, handler_name: str) -> List[Dict[str, Any]]:
        """Extract handler methods (HTTP handlers)."""
        methods = []

        # Pattern: func (h *HandlerName) MethodName(c *gin.Context) or (c echo.Context)
        # Supports Gin, Echo, Chi frameworks
        pattern = rf"func\s+\((\w+)\s+\*?{handler_name}\)\s+(\w+)\s*\((\w+)\s+\*?(gin\.Context|echo\.Context|http\.ResponseWriter)"

        matches = re.finditer(pattern, content, re.DOTALL)

        for match in matches:
            receiver = match.group(1)
            method_name = match.group(2)
            param_name = match.group(3)
            framework = match.group(4)

            # Try to determine HTTP method from function body
            method_start = match.start()
            method_end = min(len(content), match.end() + 500)
            method_body = content[method_start:method_end]

            http_method = "UNKNOWN"
            if "GET" in method_body or ".GET(" in method_body:
                http_method = "GET"
            elif "POST" in method_body or ".POST(" in method_body:
                http_method = "POST"
            elif "PUT" in method_body or ".PUT(" in method_body:
                http_method = "PUT"
            elif "DELETE" in method_body or ".DELETE(" in method_body:
                http_method = "DELETE"
            elif "PATCH" in method_body or ".PATCH(" in method_body:
                http_method = "PATCH"

            method = {
                "name": method_name,
                "http_method": http_method,
                "framework": framework.split('.')[0],
                "receiver": receiver
            }

            methods.append(method)

        return methods

    def _parse_service(self, content: str, relative_path: str, file_path: Path):
        """Parse a Go service file."""
        # Extract struct name
        struct_match = re.search(r"type\s+(\w+Service)\s+struct\s*{(.*?)}", content, re.DOTALL)
        if not struct_match:
            return

        service_name = struct_match.group(1)
        struct_fields = struct_match.group(2)

        # Extract dependencies from struct fields
        dependencies = []
        dep_matches = re.findall(r'(\w+)\s+\*?(\w+(?:Repository|Client|Logger|Service))', struct_fields)
        for dep in dep_matches:
            dependencies.append({"name": dep[0], "type": dep[1]})

        # Extract methods
        methods = self._extract_go_methods(content, service_name)

        # Try to find constructor
        constructor_match = re.search(
            rf"func\s+New{service_name}\s*\((.*?)\)\s*\*?{service_name}",
            content,
            re.DOTALL
        )
        constructor_deps = []
        if constructor_match:
            params = constructor_match.group(1)
            dep_matches = re.findall(r'(\w+)\s+\*?(\w+)', params)
            constructor_deps = [{"name": dep[0], "type": dep[1]} for dep in dep_matches]

        service = {
            "id": service_name,
            "name": service_name,
            "type": "service",
            "layer": "backend",
            "file_path": relative_path,
            "dependencies": dependencies or constructor_deps,
            "methods": methods,
            "tech_stack": "go-backend"
        }

        self.services.append(service)

    def _parse_repository(self, content: str, relative_path: str, file_path: Path):
        """Parse a Go repository file."""
        # Extract struct name
        struct_match = re.search(r"type\s+(\w+(?:Repository|Repo))\s+struct\s*{(.*?)}", content, re.DOTALL)
        if not struct_match:
            return

        repo_name = struct_match.group(1)
        struct_fields = struct_match.group(2)

        # Extract dependencies (usually DB connection)
        dependencies = []
        dep_matches = re.findall(r'(\w+)\s+\*?(\w+(?:DB|Database|Client|Connection))', struct_fields)
        for dep in dep_matches:
            dependencies.append({"name": dep[0], "type": dep[1]})

        # Extract methods
        methods = self._extract_go_methods(content, repo_name)

        repository = {
            "id": repo_name,
            "name": repo_name,
            "type": "repository",
            "layer": "backend",
            "file_path": relative_path,
            "dependencies": dependencies,
            "methods": methods,
            "tech_stack": "go-backend"
        }

        self.repositories.append(repository)

    def _parse_model(self, content: str, relative_path: str, file_path: Path):
        """Parse a Go model/struct file."""
        # Find all struct definitions
        struct_matches = re.finditer(r"type\s+(\w+)\s+struct\s*{(.*?)}", content, re.DOTALL)

        for struct_match in struct_matches:
            model_name = struct_match.group(1)
            struct_fields = struct_match.group(2)

            # Skip if it's a handler, service, or repository
            if any(suffix in model_name for suffix in ['Handler', 'Service', 'Repository', 'Repo']):
                continue

            # Extract fields
            fields = []
            field_matches = re.findall(r'(\w+)\s+(\*?\w+(?:\.\w+)?)', struct_fields)
            for field in field_matches:
                fields.append({"name": field[0], "type": field[1]})

            model = {
                "id": model_name,
                "name": model_name,
                "type": "model",
                "layer": "backend",
                "file_path": relative_path,
                "fields": fields,
                "tech_stack": "go-backend"
            }

            self.models.append(model)

    def _parse_routes(self, content: str, relative_path: str, file_path: Path):
        """Parse Go route definitions (Gin/Echo/Chi)."""
        routes = []

        # Gin router patterns: r.GET("/path", handler)
        gin_pattern = r'(\w+)\.(?:GET|POST|PUT|DELETE|PATCH)\(["\']([^"\']+)["\'],\s*(\w+(?:\.\w+)?)'
        gin_matches = re.finditer(gin_pattern, content)

        for match in gin_matches:
            router = match.group(1)
            path = match.group(2)
            handler = match.group(3)

            # Determine HTTP method
            method_match = re.search(r'\.(GET|POST|PUT|DELETE|PATCH)\(', match.group(0))
            http_method = method_match.group(1) if method_match else "UNKNOWN"

            route = {
                "method": http_method,
                "path": path,
                "handler": handler,
                "framework": "gin"
            }

            routes.append(route)

        # Echo router patterns: e.GET("/path", handler)
        echo_pattern = r'(\w+)\.(?:GET|POST|PUT|DELETE|PATCH)\(["\']([^"\']+)["\'],\s*(\w+(?:\.\w+)?)'
        echo_matches = re.finditer(echo_pattern, content)

        for match in echo_matches:
            path = match.group(2)
            handler = match.group(3)

            method_match = re.search(r'\.(GET|POST|PUT|DELETE|PATCH)\(', match.group(0))
            http_method = method_match.group(1) if method_match else "UNKNOWN"

            route = {
                "method": http_method,
                "path": path,
                "handler": handler,
                "framework": "echo"
            }

            routes.append(route)

        self.routes.extend(routes)

    def _extract_go_methods(self, content: str, struct_name: str) -> List[Dict[str, Any]]:
        """Extract methods for a Go struct."""
        methods = []

        # Pattern: func (receiver *StructName) MethodName(params) returnType
        pattern = rf"func\s+\((\w+)\s+\*?{re.escape(struct_name)}\)\s+(\w+)\s*\((.*?)\)\s*(\(.*?\)|[\w\*\[\]\.]+)?"

        matches = re.finditer(pattern, content, re.DOTALL)

        for match in matches:
            receiver = match.group(1)
            method_name = match.group(2)
            params = match.group(3)
            return_type = match.group(4) or "void"

            # Extract parameters
            param_list = []
            if params.strip():
                param_matches = re.findall(r'(\w+)\s+([\w\*\[\]\.]+)', params)
                param_list = [{"name": p[0], "type": p[1]} for p in param_matches]

            method = {
                "name": method_name,
                "receiver": receiver,
                "parameters": param_list,
                "return_type": return_type.strip()
            }

            methods.append(method)

        return methods
