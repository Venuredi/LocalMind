"""
NestJS Parser
Extracts controllers, services, DTOs, routes, and dependencies from NestJS TypeScript code.
"""

import re
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
import ast
import libcst as cst


class NestJSParser:
    """Parse NestJS TypeScript files and extract code intelligence."""

    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.controllers: List[Dict[str, Any]] = []
        self.services: List[Dict[str, Any]] = []
        self.dtos: List[Dict[str, Any]] = []
        self.entities: List[Dict[str, Any]] = []
        self.repositories: List[Dict[str, Any]] = []

    def parse(self) -> Dict[str, Any]:
        """Parse the entire NestJS codebase."""
        # Find all TypeScript files
        ts_files = list(self.repo_path.rglob("*.ts"))

        for file_path in ts_files:
            self._parse_file(file_path)

        return {
            "controllers": self.controllers,
            "services": self.services,
            "dtos": self.dtos,
            "entities": self.entities,
            "repositories": self.repositories,
        }

    def _parse_file(self, file_path: Path):
        """Parse a single TypeScript file."""
        try:
            content = file_path.read_text(encoding="utf-8")
            relative_path = file_path.relative_to(self.repo_path)

            # Determine file type and parse accordingly
            if ".controller.ts" in file_path.name:
                self._parse_controller(content, str(relative_path), file_path)
            elif ".service.ts" in file_path.name:
                self._parse_service(content, str(relative_path), file_path)
            elif ".dto.ts" in file_path.name:
                self._parse_dto(content, str(relative_path), file_path)
            elif ".entity.ts" in file_path.name:
                self._parse_entity(content, str(relative_path), file_path)
            elif ".repository.ts" in file_path.name:
                self._parse_repository(content, str(relative_path), file_path)

        except Exception as e:
            print(f"Error parsing {file_path}: {e}")

    def _parse_controller(self, content: str, relative_path: str, file_path: Path):
        """Parse a NestJS controller file."""
        # Extract class name
        class_match = re.search(r"export\s+class\s+(\w+)\s+", content)
        if not class_match:
            return

        class_name = class_match.group(1)

        # Extract @Controller decorator
        controller_decorator = re.search(
            r"@Controller\(['\"]([^'\"]*)['\"]", content
        )
        base_route = controller_decorator.group(1) if controller_decorator else ""

        # Extract constructor dependencies
        constructor_match = re.search(
            r"constructor\((.*?)\)\s*{", content, re.DOTALL
        )
        dependencies = []
        if constructor_match:
            params = constructor_match.group(1)
            # Extract injected services
            dep_matches = re.findall(
                r"(?:private|public|protected)\s+(?:readonly\s+)?(\w+):\s+(\w+)",
                params,
            )
            dependencies = [
                {"name": dep[0], "type": dep[1]} for dep in dep_matches
            ]

        # Extract routes (methods with decorators)
        routes = self._extract_routes(content, base_route)

        controller = {
            "id": f"{class_name}",
            "name": class_name,
            "type": "controller",
            "layer": "backend",
            "file_path": relative_path,
            "base_route": f"/{base_route}" if base_route else "/",
            "routes": routes,
            "dependencies": dependencies,
            "calls": [dep["type"] for dep in dependencies],
            "line_start": self._get_class_line_number(content, class_name),
        }

        self.controllers.append(controller)

    def _extract_routes(self, content: str, base_route: str) -> List[Dict[str, Any]]:
        """Extract route methods from controller."""
        routes = []

        # Pattern for route decorators
        route_pattern = r"@(Get|Post|Put|Delete|Patch)\(['\"]?([^'\")\s]*)?['\"]?\)\s+(?:async\s+)?(\w+)\s*\([^)]*\)"

        matches = re.finditer(route_pattern, content, re.MULTILINE)

        for match in matches:
            http_method = match.group(1).upper()
            route_path = match.group(2) or ""
            method_name = match.group(3)

            # Build full route
            full_route = f"/{base_route}"
            if route_path:
                full_route = f"{full_route}/{route_path}".replace("//", "/")

            # Extract method body to find service calls
            method_body = self._extract_method_body(content, method_name)
            service_calls = self._extract_service_calls(method_body)

            # Extract DTOs from parameters
            dtos_used = self._extract_dtos_from_method(content, method_name)

            # Find line number
            line_number = content[: match.start()].count("\n") + 1

            routes.append(
                {
                    "method": http_method,
                    "path": full_route,
                    "handler": method_name,
                    "service_calls": service_calls,
                    "dtos": dtos_used,
                    "line_number": line_number,
                }
            )

        return routes

    def _parse_service(self, content: str, relative_path: str, file_path: Path):
        """Parse a NestJS service file."""
        class_match = re.search(r"export\s+class\s+(\w+)\s+", content)
        if not class_match:
            return

        class_name = class_match.group(1)

        # Extract constructor dependencies
        constructor_match = re.search(
            r"constructor\((.*?)\)\s*{", content, re.DOTALL
        )
        dependencies = []
        if constructor_match:
            params = constructor_match.group(1)
            dep_matches = re.findall(
                r"(?:private|public|protected)\s+(?:readonly\s+)?(\w+):\s+(\w+)",
                params,
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
            "calls": [dep["type"] for dep in dependencies],
            "line_start": self._get_class_line_number(content, class_name),
        }

        self.services.append(service)

    def _extract_service_methods(self, content: str) -> List[Dict[str, Any]]:
        """Extract methods from a service class."""
        methods = []

        # Pattern for async methods
        method_pattern = r"(?:async\s+)?(\w+)\s*\([^)]*\)(?:\s*:\s*Promise<[^>]+>)?\s*{"

        matches = re.finditer(method_pattern, content)

        for match in matches:
            method_name = match.group(1)

            # Skip constructor
            if method_name == "constructor":
                continue

            # Extract method body
            method_body = self._extract_method_body(content, method_name)

            # Find what this method calls
            repository_calls = re.findall(r"this\.(\w+)\.(\w+)\(", method_body)
            external_calls = [
                {"repository": call[0], "method": call[1]}
                for call in repository_calls
            ]

            # Extract comments/docs
            line_number = content[: match.start()].count("\n") + 1
            doc_comment = self._extract_doc_comment(content, line_number)

            methods.append(
                {
                    "name": method_name,
                    "calls": external_calls,
                    "line_number": line_number,
                    "description": doc_comment,
                }
            )

        return methods

    def _parse_dto(self, content: str, relative_path: str, file_path: Path):
        """Parse a DTO (Data Transfer Object) file."""
        class_match = re.search(r"export\s+class\s+(\w+)\s+", content)
        if not class_match:
            return

        class_name = class_match.group(1)

        # Extract properties with decorators
        properties = []
        prop_pattern = r"@(\w+)\([^)]*\)\s+(\w+):\s+(\w+)"
        matches = re.finditer(prop_pattern, content)

        for match in matches:
            decorator = match.group(1)
            prop_name = match.group(2)
            prop_type = match.group(3)
            line_number = content[: match.start()].count("\n") + 1

            properties.append(
                {
                    "name": prop_name,
                    "type": prop_type,
                    "validators": [decorator],
                    "line_number": line_number,
                }
            )

        dto = {
            "id": class_name,
            "name": class_name,
            "type": "dto",
            "layer": "backend",
            "file_path": relative_path,
            "properties": properties,
            "line_start": self._get_class_line_number(content, class_name),
        }

        self.dtos.append(dto)

    def _parse_entity(self, content: str, relative_path: str, file_path: Path):
        """Parse a TypeORM entity file."""
        class_match = re.search(r"export\s+class\s+(\w+)\s+", content)
        if not class_match:
            return

        class_name = class_match.group(1)

        # Extract @Entity decorator
        entity_decorator = re.search(r"@Entity\(['\"]?([^'\")\s]*)?", content)
        table_name = (
            entity_decorator.group(1) if entity_decorator else class_name.lower()
        )

        # Extract columns
        columns = []
        column_pattern = r"@(\w+)\([^)]*\)\s+(\w+):\s+(\w+)"
        matches = re.finditer(column_pattern, content)

        for match in matches:
            decorator = match.group(1)
            col_name = match.group(2)
            col_type = match.group(3)
            line_number = content[: match.start()].count("\n") + 1

            if decorator in ["Column", "PrimaryGeneratedColumn", "CreateDateColumn"]:
                columns.append(
                    {
                        "name": col_name,
                        "type": col_type,
                        "decorator": decorator,
                        "line_number": line_number,
                    }
                )

        entity = {
            "id": class_name,
            "name": class_name,
            "type": "entity",
            "layer": "data",
            "file_path": relative_path,
            "table_name": table_name,
            "columns": columns,
            "line_start": self._get_class_line_number(content, class_name),
        }

        self.entities.append(entity)

    def _parse_repository(self, content: str, relative_path: str, file_path: Path):
        """Parse a repository file."""
        class_match = re.search(r"export\s+class\s+(\w+)\s+", content)
        if not class_match:
            return

        class_name = class_match.group(1)

        # Extract methods
        methods = self._extract_service_methods(content)

        # Find associated entity
        entity_import = re.search(r"import\s+{\s*(\w+)\s*}", content)
        associated_entity = entity_import.group(1) if entity_import else None

        repository = {
            "id": class_name,
            "name": class_name,
            "type": "repository",
            "layer": "data",
            "file_path": relative_path,
            "entity": associated_entity,
            "methods": methods,
            "line_start": self._get_class_line_number(content, class_name),
        }

        self.repositories.append(repository)

    def _extract_method_body(self, content: str, method_name: str) -> str:
        """Extract the body of a method."""
        pattern = rf"\b{method_name}\s*\([^)]*\)[^{{]*\{{"
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

    def _extract_service_calls(self, method_body: str) -> List[str]:
        """Extract service method calls from a method body."""
        # Pattern: this.serviceName.methodName(
        pattern = r"this\.(\w+)\.(\w+)\("
        matches = re.findall(pattern, method_body)
        return [f"{service}.{method}" for service, method in matches]

    def _extract_dtos_from_method(self, content: str, method_name: str) -> List[str]:
        """Extract DTOs used in method parameters."""
        # Find method signature
        pattern = rf"{method_name}\s*\([^)]*@Body\(\)\s+\w+:\s+(\w+)"
        matches = re.findall(pattern, content)
        return matches

    def _get_class_line_number(self, content: str, class_name: str) -> int:
        """Get the line number where a class is defined."""
        pattern = rf"export\s+class\s+{class_name}"
        match = re.search(pattern, content)
        if match:
            return content[: match.start()].count("\n") + 1
        return 0

    def _extract_doc_comment(self, content: str, line_number: int) -> Optional[str]:
        """Extract documentation comment above a line."""
        lines = content.split("\n")
        if line_number < 2:
            return None

        # Look for /** ... */ or // comments
        comment_lines = []
        for i in range(line_number - 2, -1, -1):
            line = lines[i].strip()
            if line.startswith("/**") or line.startswith("*") or line.startswith("//"):
                comment_lines.insert(0, line)
            else:
                break

        if comment_lines:
            # Clean up comment markers
            cleaned = "\n".join(comment_lines)
            cleaned = re.sub(r"\/\*\*|\*\/|\*|\/\/", "", cleaned).strip()
            return cleaned

        return None
