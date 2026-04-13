"""
Express.js Parser (JavaScript/TypeScript)
Extracts routes, controllers, services, and middleware from Express applications.
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Any


class ExpressParser:
    """Parse Express.js files and extract code intelligence."""

    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.controllers: List[Dict[str, Any]] = []
        self.services: List[Dict[str, Any]] = []
        self.routes: List[Dict[str, Any]] = []
        self.middleware: List[Dict[str, Any]] = []
        self.models: List[Dict[str, Any]] = []

    def parse(self) -> Dict[str, Any]:
        """Parse the entire Express codebase."""
        # Find all JavaScript and TypeScript files
        js_files = list(self.repo_path.rglob("*.js")) + list(self.repo_path.rglob("*.ts"))

        for file_path in js_files:
            # Skip node_modules and test files
            if "node_modules" in str(file_path) or ".test." in str(file_path):
                continue

            self._parse_file(file_path)

        return {
            "controllers": self.controllers,
            "services": self.services,
            "routes": self.routes,
            "middleware": self.middleware,
            "models": self.models,
        }

    def _parse_file(self, file_path: Path):
        """Parse a single JavaScript/TypeScript file."""
        try:
            content = file_path.read_text(encoding="utf-8")
            relative_path = file_path.relative_to(self.repo_path)

            # Determine file type and parse accordingly
            if "controller" in str(file_path).lower() or "/controllers/" in str(file_path):
                self._parse_controller(content, str(relative_path), file_path)
            elif "service" in str(file_path).lower() or "/services/" in str(file_path):
                self._parse_service(content, str(relative_path), file_path)
            elif "route" in str(file_path).lower() or "/routes/" in str(file_path):
                self._parse_routes(content, str(relative_path), file_path)
            elif "middleware" in str(file_path).lower() or "/middleware/" in str(file_path):
                self._parse_middleware(content, str(relative_path), file_path)
            elif "model" in str(file_path).lower() or "/models/" in str(file_path):
                self._parse_model(content, str(relative_path), file_path)

        except Exception as e:
            print(f"Error parsing {file_path}: {e}")

    def _parse_controller(self, content: str, relative_path: str, file_path: Path):
        """Parse an Express controller file."""
        # Extract class-based or object-based controller

        # Class-based controller (TypeScript)
        class_match = re.search(r"(?:export\s+)?class\s+(\w+)(?:\s+extends\s+\w+)?", content)

        if class_match:
            class_name = class_match.group(1)

            # Extract constructor dependencies
            constructor_match = re.search(
                r"constructor\s*\((.*?)\)",
                content,
                re.DOTALL
            )
            dependencies = []
            if constructor_match:
                params = constructor_match.group(1)
                # Extract type-hinted dependencies
                dep_matches = re.findall(
                    r"(?:private|public|protected)\s+(?:readonly\s+)?(\w+):\s*(\w+)",
                    params
                )
                dependencies = [
                    {"name": dep[0], "type": dep[1]} for dep in dep_matches
                ]

            # Extract methods
            methods = self._extract_controller_methods(content)

            controller = {
                "id": class_name,
                "name": class_name,
                "type": "controller",
                "layer": "backend",
                "file_path": relative_path,
                "dependencies": dependencies,
                "methods": methods,
                "tech_stack": "express-backend"
            }

            self.controllers.append(controller)

        # Function-based controller exports
        else:
            # Extract exported functions (e.g., exports.getUser = async (req, res) => {})
            export_pattern = r'(?:exports?\.(\w+)|export\s+(?:const|async\s+function)\s+(\w+))\s*=?\s*(?:async\s+)?\(.*?(?:req|request).*?(?:res|response)'

            matches = re.finditer(export_pattern, content)

            for match in matches:
                func_name = match.group(1) or match.group(2)

                controller = {
                    "id": func_name,
                    "name": func_name,
                    "type": "controller_function",
                    "layer": "backend",
                    "file_path": relative_path,
                    "dependencies": [],
                    "methods": [{"name": func_name, "is_async": "async" in match.group(0)}],
                    "tech_stack": "express-backend"
                }

                self.controllers.append(controller)

    def _extract_controller_methods(self, content: str) -> List[Dict[str, Any]]:
        """Extract methods from controller class."""
        methods = []

        # Pattern for TypeScript/JavaScript methods
        # async methodName(req: Request, res: Response): Promise<void>
        # or: methodName = async (req, res) => {}

        patterns = [
            r'(?:async\s+)?(\w+)\s*\(.*?(?:req|request).*?(?:res|response).*?\)',
            r'(\w+)\s*=\s*async\s*\(.*?(?:req|request).*?(?:res|response).*?\)',
        ]

        for pattern in patterns:
            matches = re.finditer(pattern, content)

            for match in matches:
                method_name = match.group(1)

                # Skip constructor
                if method_name == 'constructor':
                    continue

                method = {
                    "name": method_name,
                    "is_async": "async" in match.group(0),
                    "is_handler": True
                }

                methods.append(method)

        return methods

    def _parse_service(self, content: str, relative_path: str, file_path: Path):
        """Parse an Express service file."""
        # Class-based service
        class_match = re.search(r"(?:export\s+)?class\s+(\w+)(?:\s+extends\s+\w+)?", content)

        if class_match:
            class_name = class_match.group(1)

            # Extract constructor dependencies
            constructor_match = re.search(
                r"constructor\s*\((.*?)\)",
                content,
                re.DOTALL
            )
            dependencies = []
            if constructor_match:
                params = constructor_match.group(1)
                dep_matches = re.findall(
                    r"(?:private|public|protected)\s+(?:readonly\s+)?(\w+):\s*(\w+)",
                    params
                )
                dependencies = [
                    {"name": dep[0], "type": dep[1]} for dep in dep_matches
                ]

            # Extract methods
            methods = self._extract_service_methods(content)

            service = {
                "id": class_name,
                "name": class_name,
                "type": "service",
                "layer": "backend",
                "file_path": relative_path,
                "dependencies": dependencies,
                "methods": methods,
                "tech_stack": "express-backend"
            }

            self.services.append(service)

    def _extract_service_methods(self, content: str) -> List[Dict[str, Any]]:
        """Extract methods from service class."""
        methods = []

        # Pattern: async methodName(param1, param2): ReturnType
        method_pattern = r'(?:async\s+)?(\w+)\s*\((.*?)\)(?:\s*:\s*[\w<>[\]]+)?'

        matches = re.finditer(method_pattern, content)

        for match in matches:
            method_name = match.group(1)
            params = match.group(2)

            # Skip constructor and common non-method names
            if method_name in ['constructor', 'class', 'export', 'import', 'const', 'let', 'var', 'function']:
                continue

            # Extract parameters
            param_list = []
            if params.strip():
                param_matches = re.findall(r'(\w+)(?:\s*:\s*([\w<>[\]]+))?', params)
                param_list = [
                    {"name": p[0], "type": p[1] or "any"} for p in param_matches if p[0] not in ['', 'this']
                ]

            method = {
                "name": method_name,
                "parameters": param_list,
                "is_async": "async" in match.group(0)
            }

            methods.append(method)

        return methods

    def _parse_routes(self, content: str, relative_path: str, file_path: Path):
        """Parse Express route definitions."""
        routes = []

        # Pattern: router.get('/path', controller.method)
        # Pattern: app.post('/path', middleware, controller)
        route_patterns = [
            r'(?:router|app)\.(get|post|put|delete|patch)\s*\(["\']([^"\']+)["\'](?:,\s*(\w+(?:\.\w+)?))(?:,\s*(\w+(?:\.\w+)?))?\)',
        ]

        for pattern in route_patterns:
            matches = re.finditer(pattern, content)

            for match in matches:
                http_method = match.group(1).upper()
                path = match.group(2)
                handler = match.group(3) or match.group(4)

                route = {
                    "method": http_method,
                    "path": path,
                    "handler": handler,
                    "file_path": relative_path
                }

                routes.append(route)

        self.routes.extend(routes)

    def _parse_middleware(self, content: str, relative_path: str, file_path: Path):
        """Parse Express middleware."""
        # Extract middleware functions
        # Pattern: export const authMiddleware = (req, res, next) => {}
        # Pattern: function authMiddleware(req, res, next) {}

        middleware_patterns = [
            r'export\s+(?:const|function)\s+(\w+)\s*=?\s*(?:async\s+)?\(.*?req.*?res.*?next',
            r'(?:exports?\.(\w+))\s*=\s*(?:async\s+)?\(.*?req.*?res.*?next',
        ]

        for pattern in middleware_patterns:
            matches = re.finditer(pattern, content)

            for match in matches:
                middleware_name = match.group(1)

                middleware = {
                    "id": middleware_name,
                    "name": middleware_name,
                    "type": "middleware",
                    "layer": "backend",
                    "file_path": relative_path,
                    "is_async": "async" in match.group(0),
                    "tech_stack": "express-backend"
                }

                self.middleware.append(middleware)

    def _parse_model(self, content: str, relative_path: str, file_path: Path):
        """Parse model definitions (Mongoose, Sequelize, TypeORM, etc.)."""
        # Mongoose schema pattern
        mongoose_match = re.search(r"const\s+(\w+)Schema\s*=\s*new\s+(?:mongoose\.)?Schema", content)

        if mongoose_match:
            model_name = mongoose_match.group(1)

            # Extract schema fields
            schema_match = re.search(
                rf"const\s+{model_name}Schema\s*=\s*new\s+(?:mongoose\.)?Schema\s*\((.*?)\)",
                content,
                re.DOTALL
            )

            fields = []
            if schema_match:
                schema_def = schema_match.group(1)
                # Extract field definitions
                field_matches = re.findall(r'(\w+)\s*:\s*({.*?}|String|Number|Date|Boolean|ObjectId)', schema_def)
                fields = [{"name": f[0], "type": f[1]} for f in field_matches]

            model = {
                "id": model_name,
                "name": model_name,
                "type": "model",
                "layer": "backend",
                "file_path": relative_path,
                "fields": fields,
                "orm": "mongoose",
                "tech_stack": "express-backend"
            }

            self.models.append(model)

        # TypeORM entity pattern
        entity_match = re.search(r"@Entity\(['\"]?(\w+)?['\"]?\)\s*(?:export\s+)?class\s+(\w+)", content)

        if entity_match:
            table_name = entity_match.group(1) or entity_match.group(2).lower()
            class_name = entity_match.group(2)

            # Extract columns
            column_matches = re.finditer(r'@Column\((.*?)\)\s+(\w+):\s*([\w<>[\]]+)', content, re.DOTALL)

            fields = []
            for cm in column_matches:
                field_name = cm.group(2)
                field_type = cm.group(3)
                fields.append({"name": field_name, "type": field_type})

            model = {
                "id": class_name,
                "name": class_name,
                "type": "model",
                "layer": "backend",
                "file_path": relative_path,
                "table": table_name,
                "fields": fields,
                "orm": "typeorm",
                "tech_stack": "express-backend"
            }

            self.models.append(model)
