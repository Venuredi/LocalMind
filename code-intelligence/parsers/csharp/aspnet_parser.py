"""
ASP.NET Core Parser
Extracts controllers, services, repositories, DTOs, and routes from ASP.NET Core C# code.
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Any


class AspNetCoreParser:
    """Parse ASP.NET Core C# files and extract code intelligence."""

    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.controllers: List[Dict[str, Any]] = []
        self.services: List[Dict[str, Any]] = []
        self.repositories: List[Dict[str, Any]] = []
        self.dtos: List[Dict[str, Any]] = []
        self.entities: List[Dict[str, Any]] = []

    def parse(self) -> Dict[str, Any]:
        """Parse the entire ASP.NET Core codebase."""
        cs_files = list(self.repo_path.rglob("*.cs"))

        for file_path in cs_files:
            self._parse_file(file_path)

        return {
            "controllers": self.controllers,
            "services": self.services,
            "repositories": self.repositories,
            "dtos": self.dtos,
            "entities": self.entities,
        }

    def _parse_file(self, file_path: Path):
        """Parse a single C# file."""
        try:
            content = file_path.read_text(encoding="utf-8")
            relative_path = file_path.relative_to(self.repo_path)

            # Determine file type and parse accordingly
            if "Controller.cs" in file_path.name or "/Controllers/" in str(file_path):
                self._parse_controller(content, str(relative_path), file_path)
            elif "Service.cs" in file_path.name or "/Services/" in str(file_path):
                self._parse_service(content, str(relative_path), file_path)
            elif "Repository.cs" in file_path.name or "/Repositories/" in str(file_path):
                self._parse_repository(content, str(relative_path), file_path)
            elif "Dto.cs" in file_path.name or "/Dtos/" in str(file_path) or "/DTOs/" in str(file_path):
                self._parse_dto(content, str(relative_path), file_path)
            elif "Entity.cs" in file_path.name or "/Entities/" in str(file_path) or "/Models/" in str(file_path):
                self._parse_entity(content, str(relative_path), file_path)

        except Exception as e:
            print(f"Error parsing {file_path}: {e}")

    def _parse_controller(self, content: str, relative_path: str, file_path: Path):
        """Parse an ASP.NET Core controller file."""
        # Extract class name
        class_match = re.search(r"public\s+class\s+(\w+)\s*:\s*(?:Controller|ControllerBase)", content)
        if not class_match:
            return

        class_name = class_match.group(1)

        # Extract [Route] decorator from controller
        route_decorator = re.search(r'\[Route\(["\']([^"\']*)["\']', content)
        base_route = route_decorator.group(1) if route_decorator else ""

        # Extract [ApiController] attribute
        has_api_controller = bool(re.search(r'\[ApiController\]', content))

        # Extract constructor dependencies
        constructor_match = re.search(
            r"public\s+" + re.escape(class_name) + r"\s*\((.*?)\)",
            content,
            re.DOTALL
        )
        dependencies = []
        if constructor_match:
            params = constructor_match.group(1)
            # Extract injected dependencies (e.g., IUserRepository userRepo, ILogger<Controller> logger)
            dep_matches = re.findall(
                r'(I[A-Z]\w+|[A-Z]\w+(?:Service|Repository|Logger|Factory|Provider|Client))\s+(\w+)',
                params
            )
            dependencies = [
                {"name": dep[1], "type": dep[0]} for dep in dep_matches
            ]

        # Extract routes (action methods with HTTP decorators)
        routes = self._extract_routes_csharp(content, base_route)

        controller = {
            "id": class_name,
            "name": class_name,
            "type": "controller",
            "layer": "backend",
            "file_path": relative_path,
            "base_route": base_route,
            "is_api_controller": has_api_controller,
            "dependencies": dependencies,
            "routes": routes,
            "tech_stack": "aspnet-core"
        }

        self.controllers.append(controller)

    def _extract_routes_csharp(self, content: str, base_route: str) -> List[Dict[str, Any]]:
        """Extract HTTP routes from C# controller methods."""
        routes = []

        # Find all action methods with HTTP verb decorators
        # Pattern: [HttpGet], [HttpPost("route")], [HttpPut("{id}")], etc.
        http_verbs = ['HttpGet', 'HttpPost', 'HttpPut', 'HttpDelete', 'HttpPatch']

        for verb in http_verbs:
            # Match patterns like [HttpGet], [HttpGet("users")], [HttpGet("{id}")]
            pattern = rf'\[{verb}(?:\(["\']([^"\']*)["\']|\("([^"]*)"\)|\({{([^}}]*)}}\))?\]\s*(?:\[.*?\]\s*)*public\s+(?:async\s+)?(?:Task<)?(\w+)(?:>)?\s+(\w+)\s*\((.*?)\)'

            matches = re.finditer(pattern, content, re.DOTALL)

            for match in matches:
                route_param = match.group(1) or match.group(2) or match.group(3) or ""
                return_type = match.group(4)
                method_name = match.group(5)
                params = match.group(6)

                # Build full route
                full_route = f"/{base_route.strip('/')}/{route_param.strip('/')}" if route_param else f"/{base_route.strip('/')}"
                full_route = full_route.replace('//', '/')

                # Extract parameters
                param_list = []
                if params.strip():
                    param_matches = re.findall(r'(\w+)\s+(\w+)', params)
                    param_list = [{"name": p[1], "type": p[0]} for p in param_matches]

                # Check for [Authorize] attribute
                method_start = match.start()
                method_content = content[max(0, method_start - 200):method_start]
                is_protected = bool(re.search(r'\[Authorize', method_content))

                route = {
                    "method": verb.replace('Http', '').upper(),
                    "path": full_route,
                    "handler": method_name,
                    "return_type": return_type,
                    "parameters": param_list,
                    "is_protected": is_protected
                }

                routes.append(route)

        return routes

    def _parse_service(self, content: str, relative_path: str, file_path: Path):
        """Parse an ASP.NET Core service file."""
        # Extract class name
        class_match = re.search(r"public\s+class\s+(\w+)(?:\s*:\s*I\w+)?", content)
        if not class_match:
            return

        class_name = class_match.group(1)

        # Extract interface name if it implements one
        interface_match = re.search(rf"public\s+class\s+{re.escape(class_name)}\s*:\s*(I\w+)", content)
        interface_name = interface_match.group(1) if interface_match else None

        # Extract constructor dependencies
        constructor_match = re.search(
            r"public\s+" + re.escape(class_name) + r"\s*\((.*?)\)",
            content,
            re.DOTALL
        )
        dependencies = []
        if constructor_match:
            params = constructor_match.group(1)
            dep_matches = re.findall(
                r'(I[A-Z]\w+|[A-Z]\w+(?:Service|Repository|Logger|Factory|Provider|Client|Context))\s+(\w+)',
                params
            )
            dependencies = [
                {"name": dep[1], "type": dep[0]} for dep in dep_matches
            ]

        # Extract public methods
        methods = self._extract_methods_csharp(content)

        service = {
            "id": class_name,
            "name": class_name,
            "type": "service",
            "layer": "backend",
            "file_path": relative_path,
            "interface": interface_name,
            "dependencies": dependencies,
            "methods": methods,
            "tech_stack": "aspnet-core"
        }

        self.services.append(service)

    def _parse_repository(self, content: str, relative_path: str, file_path: Path):
        """Parse an ASP.NET Core repository file."""
        # Extract class name
        class_match = re.search(r"public\s+class\s+(\w+)(?:\s*:\s*I\w+)?", content)
        if not class_match:
            return

        class_name = class_match.group(1)

        # Extract interface name
        interface_match = re.search(rf"public\s+class\s+{re.escape(class_name)}\s*:\s*(I\w+)", content)
        interface_name = interface_match.group(1) if interface_match else None

        # Extract constructor dependencies (usually DbContext)
        constructor_match = re.search(
            r"public\s+" + re.escape(class_name) + r"\s*\((.*?)\)",
            content,
            re.DOTALL
        )
        dependencies = []
        if constructor_match:
            params = constructor_match.group(1)
            dep_matches = re.findall(
                r'([A-Z]\w+(?:Context|DbContext))\s+(\w+)',
                params
            )
            dependencies = [
                {"name": dep[1], "type": dep[0]} for dep in dep_matches
            ]

        # Extract public methods
        methods = self._extract_methods_csharp(content)

        repository = {
            "id": class_name,
            "name": class_name,
            "type": "repository",
            "layer": "backend",
            "file_path": relative_path,
            "interface": interface_name,
            "dependencies": dependencies,
            "methods": methods,
            "tech_stack": "aspnet-core"
        }

        self.repositories.append(repository)

    def _parse_dto(self, content: str, relative_path: str, file_path: Path):
        """Parse a DTO file."""
        # Extract class name
        class_match = re.search(r"public\s+class\s+(\w+)", content)
        if not class_match:
            return

        class_name = class_match.group(1)

        # Extract properties
        properties = []
        prop_pattern = r'public\s+(\w+(?:<\w+>)?)\s+(\w+)\s*{\s*get;\s*(?:set;)?\s*}'
        prop_matches = re.finditer(prop_pattern, content)

        for match in prop_matches:
            prop_type = match.group(1)
            prop_name = match.group(2)
            properties.append({"name": prop_name, "type": prop_type})

        dto = {
            "id": class_name,
            "name": class_name,
            "type": "dto",
            "layer": "backend",
            "file_path": relative_path,
            "properties": properties,
            "tech_stack": "aspnet-core"
        }

        self.dtos.append(dto)

    def _parse_entity(self, content: str, relative_path: str, file_path: Path):
        """Parse an entity/model file."""
        # Extract class name
        class_match = re.search(r"public\s+class\s+(\w+)", content)
        if not class_match:
            return

        class_name = class_match.group(1)

        # Extract properties
        properties = []
        prop_pattern = r'public\s+(\w+(?:<\w+>)?)\s+(\w+)\s*{\s*get;\s*(?:set;)?\s*}'
        prop_matches = re.finditer(prop_pattern, content)

        for match in prop_matches:
            prop_type = match.group(1)
            prop_name = match.group(2)
            properties.append({"name": prop_name, "type": prop_type})

        entity = {
            "id": class_name,
            "name": class_name,
            "type": "entity",
            "layer": "backend",
            "file_path": relative_path,
            "properties": properties,
            "tech_stack": "aspnet-core"
        }

        self.entities.append(entity)

    def _extract_methods_csharp(self, content: str) -> List[Dict[str, Any]]:
        """Extract public methods from C# class."""
        methods = []

        # Pattern: public async Task<ReturnType> MethodName(params)
        # or: public ReturnType MethodName(params)
        method_pattern = r'public\s+(?:async\s+)?(?:Task<)?(\w+)(?:>)?\s+(\w+)\s*\((.*?)\)'

        matches = re.finditer(method_pattern, content, re.DOTALL)

        for match in matches:
            return_type = match.group(1)
            method_name = match.group(2)
            params = match.group(3)

            # Skip constructors and property getters/setters
            if method_name in ['get', 'set'] or return_type == 'class':
                continue

            # Extract parameters
            param_list = []
            if params.strip():
                param_matches = re.findall(r'(\w+(?:<\w+>)?)\s+(\w+)', params)
                param_list = [{"name": p[1], "type": p[0]} for p in param_matches]

            method = {
                "name": method_name,
                "return_type": return_type,
                "parameters": param_list,
                "is_async": "async" in match.group(0)
            }

            methods.append(method)

        return methods
