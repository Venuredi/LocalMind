"""
Laravel Parser
Extracts controllers, services, repositories, models, and routes from Laravel PHP code.
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Any


class LaravelParser:
    """Parse Laravel PHP files and extract code intelligence."""

    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.controllers: List[Dict[str, Any]] = []
        self.services: List[Dict[str, Any]] = []
        self.repositories: List[Dict[str, Any]] = []
        self.models: List[Dict[str, Any]] = []
        self.routes: List[Dict[str, Any]] = []

    def parse(self) -> Dict[str, Any]:
        """Parse the entire Laravel codebase."""
        php_files = list(self.repo_path.rglob("*.php"))

        for file_path in php_files:
            self._parse_file(file_path)

        return {
            "controllers": self.controllers,
            "services": self.services,
            "repositories": self.repositories,
            "models": self.models,
            "routes": self.routes,
        }

    def _parse_file(self, file_path: Path):
        """Parse a single PHP file."""
        try:
            content = file_path.read_text(encoding="utf-8")
            relative_path = file_path.relative_to(self.repo_path)

            # Determine file type and parse accordingly
            if "Controller.php" in file_path.name or "/Controllers/" in str(file_path):
                self._parse_controller(content, str(relative_path), file_path)
            elif "Service.php" in file_path.name or "/Services/" in str(file_path):
                self._parse_service(content, str(relative_path), file_path)
            elif "Repository.php" in file_path.name or "/Repositories/" in str(file_path):
                self._parse_repository(content, str(relative_path), file_path)
            elif "/Models/" in str(file_path) and file_path.name != "Model.php":
                self._parse_model(content, str(relative_path), file_path)
            elif "routes" in str(file_path).lower() and file_path.suffix == ".php":
                self._parse_routes(content, str(relative_path), file_path)

        except Exception as e:
            print(f"Error parsing {file_path}: {e}")

    def _parse_controller(self, content: str, relative_path: str, file_path: Path):
        """Parse a Laravel controller file."""
        # Extract class name
        class_match = re.search(r"class\s+(\w+)\s+extends\s+(?:Controller|BaseController)", content)
        if not class_match:
            return

        class_name = class_match.group(1)

        # Extract namespace
        namespace_match = re.search(r"namespace\s+([\w\\]+);", content)
        namespace = namespace_match.group(1) if namespace_match else ""

        # Extract constructor dependencies
        constructor_match = re.search(
            r"public\s+function\s+__construct\s*\((.*?)\)",
            content,
            re.DOTALL
        )
        dependencies = []
        if constructor_match:
            params = constructor_match.group(1)
            # Extract type-hinted dependencies
            dep_matches = re.findall(r'([A-Z]\w+)\s+\$(\w+)', params)
            dependencies = [
                {"name": dep[1], "type": dep[0]} for dep in dep_matches
            ]

        # Extract public methods (controller actions)
        methods = self._extract_php_methods(content, class_name)

        controller = {
            "id": class_name,
            "name": class_name,
            "type": "controller",
            "layer": "backend",
            "file_path": relative_path,
            "namespace": namespace,
            "dependencies": dependencies,
            "methods": methods,
            "tech_stack": "laravel-backend"
        }

        self.controllers.append(controller)

    def _parse_service(self, content: str, relative_path: str, file_path: Path):
        """Parse a Laravel service file."""
        # Extract class name
        class_match = re.search(r"class\s+(\w+)", content)
        if not class_match:
            return

        class_name = class_match.group(1)

        # Extract namespace
        namespace_match = re.search(r"namespace\s+([\w\\]+);", content)
        namespace = namespace_match.group(1) if namespace_match else ""

        # Extract constructor dependencies
        constructor_match = re.search(
            r"public\s+function\s+__construct\s*\((.*?)\)",
            content,
            re.DOTALL
        )
        dependencies = []
        if constructor_match:
            params = constructor_match.group(1)
            dep_matches = re.findall(r'([A-Z]\w+)\s+\$(\w+)', params)
            dependencies = [
                {"name": dep[1], "type": dep[0]} for dep in dep_matches
            ]

        # Extract public methods
        methods = self._extract_php_methods(content, class_name)

        service = {
            "id": class_name,
            "name": class_name,
            "type": "service",
            "layer": "backend",
            "file_path": relative_path,
            "namespace": namespace,
            "dependencies": dependencies,
            "methods": methods,
            "tech_stack": "laravel-backend"
        }

        self.services.append(service)

    def _parse_repository(self, content: str, relative_path: str, file_path: Path):
        """Parse a Laravel repository file."""
        # Extract class name
        class_match = re.search(r"class\s+(\w+)", content)
        if not class_match:
            return

        class_name = class_match.group(1)

        # Extract namespace
        namespace_match = re.search(r"namespace\s+([\w\\]+);", content)
        namespace = namespace_match.group(1) if namespace_match else ""

        # Extract constructor dependencies
        constructor_match = re.search(
            r"public\s+function\s+__construct\s*\((.*?)\)",
            content,
            re.DOTALL
        )
        dependencies = []
        if constructor_match:
            params = constructor_match.group(1)
            dep_matches = re.findall(r'([A-Z]\w+)\s+\$(\w+)', params)
            dependencies = [
                {"name": dep[1], "type": dep[0]} for dep in dep_matches
            ]

        # Extract public methods
        methods = self._extract_php_methods(content, class_name)

        repository = {
            "id": class_name,
            "name": class_name,
            "type": "repository",
            "layer": "backend",
            "file_path": relative_path,
            "namespace": namespace,
            "dependencies": dependencies,
            "methods": methods,
            "tech_stack": "laravel-backend"
        }

        self.repositories.append(repository)

    def _parse_model(self, content: str, relative_path: str, file_path: Path):
        """Parse a Laravel Eloquent model file."""
        # Extract class name
        class_match = re.search(r"class\s+(\w+)\s+extends\s+Model", content)
        if not class_match:
            return

        class_name = class_match.group(1)

        # Extract namespace
        namespace_match = re.search(r"namespace\s+([\w\\]+);", content)
        namespace = namespace_match.group(1) if namespace_match else ""

        # Extract table name
        table_match = re.search(r"\$table\s*=\s*['\"](\w+)['\"]", content)
        table_name = table_match.group(1) if table_match else class_name.lower() + 's'

        # Extract fillable fields
        fillable_match = re.search(r"\$fillable\s*=\s*\[(.*?)\]", content, re.DOTALL)
        fillable = []
        if fillable_match:
            fields = fillable_match.group(1)
            fillable = [f.strip().strip('\'"') for f in fields.split(',')]

        # Extract relationships
        relationships = self._extract_relationships(content)

        model = {
            "id": class_name,
            "name": class_name,
            "type": "model",
            "layer": "backend",
            "file_path": relative_path,
            "namespace": namespace,
            "table": table_name,
            "fillable": fillable,
            "relationships": relationships,
            "tech_stack": "laravel-backend"
        }

        self.models.append(model)

    def _parse_routes(self, content: str, relative_path: str, file_path: Path):
        """Parse Laravel route definitions."""
        routes = []

        # Pattern: Route::get('/path', [Controller::class, 'method'])
        # Pattern: Route::post('/path', 'Controller@method')
        route_patterns = [
            r"Route::(get|post|put|delete|patch)\(['\"]([^'\"]+)['\"],\s*\[(\w+)::class,\s*['\"](\w+)['\"]\]",
            r"Route::(get|post|put|delete|patch)\(['\"]([^'\"]+)['\"],\s*['\"](\w+)@(\w+)['\"]",
        ]

        for pattern in route_patterns:
            matches = re.finditer(pattern, content)

            for match in matches:
                http_method = match.group(1).upper()
                path = match.group(2)
                controller = match.group(3)
                action = match.group(4)

                # Check for middleware
                route_start = match.start()
                route_end = min(len(content), match.end() + 200)
                route_context = content[route_start:route_end]

                middleware = []
                middleware_match = re.search(r"->middleware\(['\"](\w+)['\"]\)", route_context)
                if middleware_match:
                    middleware.append(middleware_match.group(1))

                route = {
                    "method": http_method,
                    "path": path,
                    "controller": controller,
                    "action": action,
                    "middleware": middleware,
                    "file_path": relative_path
                }

                routes.append(route)

        # Pattern: Route::resource('/path', Controller::class)
        resource_pattern = r"Route::resource\(['\"]([^'\"]+)['\"],\s*(\w+)::class"
        resource_matches = re.finditer(resource_pattern, content)

        for match in resource_matches:
            path = match.group(1)
            controller = match.group(2)

            # Resource routes create standard CRUD endpoints
            resource_methods = [
                {"method": "GET", "action": "index"},
                {"method": "GET", "action": "create"},
                {"method": "POST", "action": "store"},
                {"method": "GET", "action": "show"},
                {"method": "GET", "action": "edit"},
                {"method": "PUT", "action": "update"},
                {"method": "DELETE", "action": "destroy"},
            ]

            for rm in resource_methods:
                route = {
                    "method": rm["method"],
                    "path": path,
                    "controller": controller,
                    "action": rm["action"],
                    "middleware": [],
                    "file_path": relative_path,
                    "is_resource": True
                }
                routes.append(route)

        self.routes.extend(routes)

    def _extract_php_methods(self, content: str, class_name: str) -> List[Dict[str, Any]]:
        """Extract public methods from PHP class."""
        methods = []

        # Pattern: public function methodName($param1, Type $param2): ReturnType
        method_pattern = r'public\s+function\s+(\w+)\s*\((.*?)\)(?:\s*:\s*(\w+))?'

        matches = re.finditer(method_pattern, content, re.DOTALL)

        for match in matches:
            method_name = match.group(1)
            params = match.group(2)
            return_type = match.group(3)

            # Skip constructor
            if method_name == '__construct':
                continue

            # Extract parameters
            param_list = []
            if params.strip():
                # Match type-hinted parameters: Type $name or $name
                param_matches = re.findall(r'(?:(\w+)\s+)?\$(\w+)', params)
                param_list = [
                    {"name": p[1], "type": p[0] or "mixed"} for p in param_matches
                ]

            method = {
                "name": method_name,
                "parameters": param_list,
                "return_type": return_type or "void"
            }

            methods.append(method)

        return methods

    def _extract_relationships(self, content: str) -> List[Dict[str, str]]:
        """Extract Eloquent relationships from model."""
        relationships = []

        # Patterns for common relationships
        relationship_patterns = [
            (r"public\s+function\s+(\w+)\s*\(\)\s*{\s*return\s+\$this->hasOne\((\w+)::class", "hasOne"),
            (r"public\s+function\s+(\w+)\s*\(\)\s*{\s*return\s+\$this->hasMany\((\w+)::class", "hasMany"),
            (r"public\s+function\s+(\w+)\s*\(\)\s*{\s*return\s+\$this->belongsTo\((\w+)::class", "belongsTo"),
            (r"public\s+function\s+(\w+)\s*\(\)\s*{\s*return\s+\$this->belongsToMany\((\w+)::class", "belongsToMany"),
        ]

        for pattern, rel_type in relationship_patterns:
            matches = re.finditer(pattern, content, re.DOTALL)

            for match in matches:
                method_name = match.group(1)
                related_model = match.group(2)

                relationship = {
                    "name": method_name,
                    "type": rel_type,
                    "model": related_model
                }

                relationships.append(relationship)

        return relationships
