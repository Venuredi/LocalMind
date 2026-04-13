"""
Python Framework Parser (FastAPI/Flask/Django)
Extracts routes, views, services, models, and dependencies from Python web frameworks.
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Any


class PythonFrameworkParser:
    """Parse Python web framework files and extract code intelligence."""

    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.routers: List[Dict[str, Any]] = []
        self.views: List[Dict[str, Any]] = []
        self.services: List[Dict[str, Any]] = []
        self.models: List[Dict[str, Any]] = []
        self.routes: List[Dict[str, Any]] = []

    def parse(self) -> Dict[str, Any]:
        """Parse the entire Python codebase."""
        py_files = list(self.repo_path.rglob("*.py"))

        for file_path in py_files:
            # Skip venv, __pycache__, and test files
            if any(skip in str(file_path) for skip in ['venv', '__pycache__', 'test_', '_test.py']):
                continue

            self._parse_file(file_path)

        return {
            "routers": self.routers,
            "views": self.views,
            "services": self.services,
            "models": self.models,
            "routes": self.routes,
        }

    def _parse_file(self, file_path: Path):
        """Parse a single Python file."""
        try:
            content = file_path.read_text(encoding="utf-8")
            relative_path = file_path.relative_to(self.repo_path)

            # Determine framework and file type
            if "fastapi" in content.lower() or "@app.get" in content or "@router.get" in content:
                if "router" in str(file_path).lower() or "/routers/" in str(file_path):
                    self._parse_fastapi_router(content, str(relative_path), file_path)
            elif "flask" in content.lower() or "@app.route" in content or "@blueprint.route" in content:
                if "view" in str(file_path).lower() or "/views/" in str(file_path) or "routes" in str(file_path).lower():
                    self._parse_flask_routes(content, str(relative_path), file_path)
            elif "django" in content.lower() or "from django" in content:
                if "views.py" in str(file_path):
                    self._parse_django_views(content, str(relative_path), file_path)
                elif "models.py" in str(file_path):
                    self._parse_django_models(content, str(relative_path), file_path)

            # Parse service files (common across frameworks)
            if "service" in str(file_path).lower() or "/services/" in str(file_path):
                self._parse_service(content, str(relative_path), file_path)

            # Parse SQLAlchemy models (FastAPI/Flask)
            if "model" in str(file_path).lower() or "/models/" in str(file_path):
                if "Base =" in content or "declarative_base" in content:
                    self._parse_sqlalchemy_model(content, str(relative_path), file_path)

        except Exception as e:
            print(f"Error parsing {file_path}: {e}")

    def _parse_fastapi_router(self, content: str, relative_path: str, file_path: Path):
        """Parse FastAPI router file."""
        # Extract router definition
        router_match = re.search(r"router\s*=\s*APIRouter\((.*?)\)", content, re.DOTALL)

        router_prefix = ""
        router_tags = []

        if router_match:
            router_def = router_match.group(1)
            prefix_match = re.search(r'prefix=["\']([^"\']+)["\']', router_def)
            tags_match = re.search(r'tags=\[([^\]]+)\]', router_def)

            if prefix_match:
                router_prefix = prefix_match.group(1)
            if tags_match:
                router_tags = [t.strip().strip('\'"') for t in tags_match.group(1).split(',')]

        # Extract route endpoints
        routes = self._extract_fastapi_routes(content, router_prefix)

        # Extract dependency injections from function parameters
        dependencies = self._extract_fastapi_dependencies(content)

        router = {
            "id": file_path.stem,
            "name": file_path.stem,
            "type": "router",
            "layer": "backend",
            "file_path": relative_path,
            "prefix": router_prefix,
            "tags": router_tags,
            "routes": routes,
            "dependencies": dependencies,
            "tech_stack": "python-backend",
            "framework": "fastapi"
        }

        self.routers.append(router)

    def _extract_fastapi_routes(self, content: str, base_prefix: str) -> List[Dict[str, Any]]:
        """Extract FastAPI route decorators and functions."""
        routes = []

        # Pattern: @router.get("/path") or @app.post("/path", status_code=201)
        route_pattern = r'@(?:router|app)\.(get|post|put|delete|patch)\s*\(["\']([^"\']+)["\'](?:,\s*.*?)?\)\s*(?:async\s+)?def\s+(\w+)\s*\((.*?)\)(?:\s*->\s*([\w\[\]]+))?'

        matches = re.finditer(route_pattern, content, re.DOTALL)

        for match in matches:
            http_method = match.group(1).upper()
            path = match.group(2)
            function_name = match.group(3)
            params = match.group(4)
            return_type = match.group(5)

            # Build full path
            full_path = f"{base_prefix.rstrip('/')}/{path.lstrip('/')}" if base_prefix else path

            # Extract parameters
            param_list = self._extract_python_params(params)

            # Check for dependencies (Depends())
            has_auth = bool(re.search(r'Depends\(.*?auth', params, re.IGNORECASE))

            route = {
                "method": http_method,
                "path": full_path,
                "handler": function_name,
                "parameters": param_list,
                "return_type": return_type or "Any",
                "is_async": "async" in match.group(0),
                "is_protected": has_auth
            }

            routes.append(route)

        return routes

    def _extract_fastapi_dependencies(self, content: str) -> List[Dict[str, str]]:
        """Extract Depends() injections from FastAPI routes."""
        dependencies = []

        # Pattern: param: Type = Depends(get_dependency)
        dep_pattern = r'(\w+):\s*([\w\[\]]+)\s*=\s*Depends\((\w+)\)'

        matches = re.finditer(dep_pattern, content)

        for match in matches:
            param_name = match.group(1)
            param_type = match.group(2)
            dependency = match.group(3)

            dependencies.append({
                "name": param_name,
                "type": param_type,
                "dependency": dependency
            })

        return dependencies

    def _parse_flask_routes(self, content: str, relative_path: str, file_path: Path):
        """Parse Flask route definitions."""
        routes = []

        # Pattern: @app.route('/path', methods=['GET', 'POST'])
        # Pattern: @blueprint.route('/path')
        route_pattern = r'@(?:app|blueprint|bp)\.route\s*\(["\']([^"\']+)["\'](?:,\s*methods=\[([^\]]+)\])?\)\s*def\s+(\w+)\s*\((.*?)\)'

        matches = re.finditer(route_pattern, content, re.DOTALL)

        for match in matches:
            path = match.group(1)
            methods = match.group(2)
            function_name = match.group(3)
            params = match.group(4)

            # Parse methods
            http_methods = ["GET"]  # Default
            if methods:
                http_methods = [m.strip().strip('\'"') for m in methods.split(',')]

            # Extract parameters
            param_list = self._extract_python_params(params)

            for method in http_methods:
                route = {
                    "method": method,
                    "path": path,
                    "handler": function_name,
                    "parameters": param_list,
                    "framework": "flask"
                }

                routes.append(route)

        self.routes.extend(routes)

        view = {
            "id": file_path.stem,
            "name": file_path.stem,
            "type": "view",
            "layer": "backend",
            "file_path": relative_path,
            "routes": routes,
            "tech_stack": "python-backend",
            "framework": "flask"
        }

        self.views.append(view)

    def _parse_django_views(self, content: str, relative_path: str, file_path: Path):
        """Parse Django views."""
        views = []

        # Class-based views (e.g., class UserView(APIView):)
        class_pattern = r'class\s+(\w+)\s*\((.*?View.*?)\):'

        class_matches = re.finditer(class_pattern, content)

        for match in class_matches:
            class_name = match.group(1)
            parent_class = match.group(2)

            # Extract methods (get, post, put, delete, etc.)
            class_start = match.start()
            class_end = min(len(content), match.end() + 5000)
            class_content = content[class_start:class_end]

            methods = self._extract_django_view_methods(class_content)

            view = {
                "id": class_name,
                "name": class_name,
                "type": "class_based_view",
                "layer": "backend",
                "file_path": relative_path,
                "parent": parent_class,
                "methods": methods,
                "tech_stack": "python-backend",
                "framework": "django"
            }

            views.append(view)

        # Function-based views
        func_pattern = r'def\s+(\w+)\s*\(request(?:,\s*.*?)?\):'

        func_matches = re.finditer(func_pattern, content)

        for match in func_matches:
            func_name = match.group(1)

            view = {
                "id": func_name,
                "name": func_name,
                "type": "function_based_view",
                "layer": "backend",
                "file_path": relative_path,
                "tech_stack": "python-backend",
                "framework": "django"
            }

            views.append(view)

        self.views.extend(views)

    def _extract_django_view_methods(self, content: str) -> List[Dict[str, Any]]:
        """Extract HTTP methods from Django class-based view."""
        methods = []

        http_methods = ['get', 'post', 'put', 'delete', 'patch']

        for method in http_methods:
            pattern = rf'def\s+{method}\s*\(self,\s*request(?:,\s*(.*?))?\)(?:\s*->\s*([\w\[\]]+))?:'

            match = re.search(pattern, content)

            if match:
                params = match.group(1) or ""
                return_type = match.group(2)

                param_list = self._extract_python_params(params) if params else []

                method_info = {
                    "name": method,
                    "http_method": method.upper(),
                    "parameters": param_list,
                    "return_type": return_type or "HttpResponse"
                }

                methods.append(method_info)

        return methods

    def _parse_django_models(self, content: str, relative_path: str, file_path: Path):
        """Parse Django ORM models."""
        # Pattern: class ModelName(models.Model):
        model_pattern = r'class\s+(\w+)\s*\(models\.Model\):'

        matches = re.finditer(model_pattern, content)

        for match in matches:
            model_name = match.group(1)

            # Extract fields
            model_start = match.start()
            model_end = min(len(content), match.end() + 3000)
            model_content = content[model_start:model_end]

            fields = self._extract_django_fields(model_content)

            model = {
                "id": model_name,
                "name": model_name,
                "type": "model",
                "layer": "backend",
                "file_path": relative_path,
                "fields": fields,
                "orm": "django",
                "tech_stack": "python-backend"
            }

            self.models.append(model)

    def _extract_django_fields(self, content: str) -> List[Dict[str, str]]:
        """Extract Django model fields."""
        fields = []

        # Pattern: field_name = models.CharField(...)
        field_pattern = r'(\w+)\s*=\s*models\.(\w+Field)\s*\('

        matches = re.finditer(field_pattern, content)

        for match in matches:
            field_name = match.group(1)
            field_type = match.group(2)

            fields.append({"name": field_name, "type": field_type})

        return fields

    def _parse_sqlalchemy_model(self, content: str, relative_path: str, file_path: Path):
        """Parse SQLAlchemy models (FastAPI/Flask)."""
        # Pattern: class ModelName(Base):
        model_pattern = r'class\s+(\w+)\s*\(Base\):'

        matches = re.finditer(model_pattern, content)

        for match in matches:
            model_name = match.group(1)

            # Extract table name
            model_start = match.start()
            model_end = min(len(content), match.end() + 3000)
            model_content = content[model_start:model_end]

            table_match = re.search(r'__tablename__\s*=\s*["\'](\w+)["\']', model_content)
            table_name = table_match.group(1) if table_match else model_name.lower()

            # Extract columns
            fields = self._extract_sqlalchemy_columns(model_content)

            model = {
                "id": model_name,
                "name": model_name,
                "type": "model",
                "layer": "backend",
                "file_path": relative_path,
                "table": table_name,
                "fields": fields,
                "orm": "sqlalchemy",
                "tech_stack": "python-backend"
            }

            self.models.append(model)

    def _extract_sqlalchemy_columns(self, content: str) -> List[Dict[str, str]]:
        """Extract SQLAlchemy columns."""
        fields = []

        # Pattern: field_name = Column(Integer, ...)
        # Pattern: field_name: Mapped[int] = mapped_column(Integer)
        patterns = [
            r'(\w+)\s*=\s*Column\s*\((\w+)',
            r'(\w+):\s*Mapped\[(\w+)\]',
        ]

        for pattern in patterns:
            matches = re.finditer(pattern, content)

            for match in matches:
                field_name = match.group(1)
                field_type = match.group(2)

                fields.append({"name": field_name, "type": field_type})

        return fields

    def _parse_service(self, content: str, relative_path: str, file_path: Path):
        """Parse Python service class."""
        # Pattern: class ServiceName:
        class_match = re.search(r'class\s+(\w+)(?:\s*\((.*?)\))?:', content)

        if not class_match:
            return

        class_name = class_match.group(1)
        parent_class = class_match.group(2)

        # Extract __init__ dependencies
        init_match = re.search(
            r'def\s+__init__\s*\(self(?:,\s*(.*?))?\):',
            content,
            re.DOTALL
        )

        dependencies = []
        if init_match and init_match.group(1):
            params = init_match.group(1)
            param_list = self._extract_python_params(params)
            dependencies = [{"name": p["name"], "type": p.get("type", "Any")} for p in param_list]

        # Extract methods
        methods = self._extract_python_methods(content, class_name)

        service = {
            "id": class_name,
            "name": class_name,
            "type": "service",
            "layer": "backend",
            "file_path": relative_path,
            "parent": parent_class,
            "dependencies": dependencies,
            "methods": methods,
            "tech_stack": "python-backend"
        }

        self.services.append(service)

    def _extract_python_methods(self, content: str, class_name: str) -> List[Dict[str, Any]]:
        """Extract methods from Python class."""
        methods = []

        # Pattern: def method_name(self, param1: Type1, param2: Type2) -> ReturnType:
        method_pattern = r'def\s+(\w+)\s*\(self(?:,\s*(.*?))?\)(?:\s*->\s*([\w\[\]]+))?:'

        matches = re.finditer(method_pattern, content)

        for match in matches:
            method_name = match.group(1)
            params = match.group(2)
            return_type = match.group(3)

            # Skip __init__ and private methods
            if method_name.startswith('__'):
                continue

            # Extract parameters
            param_list = self._extract_python_params(params) if params else []

            method = {
                "name": method_name,
                "parameters": param_list,
                "return_type": return_type or "None"
            }

            methods.append(method)

        return methods

    def _extract_python_params(self, params: str) -> List[Dict[str, str]]:
        """Extract parameters from Python function signature."""
        if not params or not params.strip():
            return []

        param_list = []

        # Pattern: param_name: Type = default_value
        # Pattern: param_name: Type
        # Pattern: param_name
        param_pattern = r'(\w+)(?:\s*:\s*([\w\[\]]+))?(?:\s*=\s*[^,]+)?'

        matches = re.finditer(param_pattern, params)

        for match in matches:
            param_name = match.group(1)
            param_type = match.group(2)

            # Skip if it's a keyword or empty
            if param_name in ['', 'self', 'cls', 'None', 'True', 'False']:
                continue

            param_list.append({
                "name": param_name,
                "type": param_type or "Any"
            })

        return param_list
