"""
Spring Boot Parser
Extracts controllers, services, repositories, entities, DTOs, configurations,
and REST API endpoints from Spring Boot Java code.
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Any

_EXCLUDED_DIRS = {
    "target", "build", ".gradle", ".mvn",
    ".git", ".svn",
    "bin", "out",
    ".idea", ".vscode",
    "node_modules",
    "__pycache__", ".pytest_cache",
}


def _is_excluded(file_path: Path) -> bool:
    return any(part in _EXCLUDED_DIRS for part in file_path.parts)


class SpringBootParser:
    """Parse Spring Boot Java files and extract code intelligence."""

    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.controllers: List[Dict[str, Any]] = []
        self.services: List[Dict[str, Any]] = []
        self.repositories: List[Dict[str, Any]] = []
        self.entities: List[Dict[str, Any]] = []
        self.dtos: List[Dict[str, Any]] = []
        self.configurations: List[Dict[str, Any]] = []
        self.components: List[Dict[str, Any]] = []
        self.rest_clients: List[Dict[str, Any]] = []

    def parse(self) -> Dict[str, Any]:
        """Parse the entire Spring Boot codebase."""
        java_files = [f for f in self.repo_path.rglob("*.java") if not _is_excluded(f)]

        for file_path in java_files:
            self._parse_file(file_path)

        return {
            "controllers": self.controllers,
            "services": self.services,
            "repositories": self.repositories,
            "entities": self.entities,
            "dtos": self.dtos,
            "configurations": self.configurations,
            "components": self.components,
            "rest_clients": self.rest_clients,
        }

    def _parse_file(self, file_path: Path):
        """Parse a single Java file."""
        try:
            content = file_path.read_text(encoding="utf-8")
            relative_path = file_path.relative_to(self.repo_path)

            # Skip test files
            if "Test.java" in file_path.name or "test" in str(relative_path).lower():
                return

            # Determine file type based on annotations and naming conventions
            if "@RestController" in content or "@Controller" in content:
                self._parse_controller(content, str(relative_path), file_path)
            elif "@Service" in content:
                self._parse_service(content, str(relative_path), file_path)
            elif "@Repository" in content or "Repository" in file_path.name:
                self._parse_repository(content, str(relative_path), file_path)
            elif "@Entity" in content or "@Table" in content:
                self._parse_entity(content, str(relative_path), file_path)
            elif "@Configuration" in content:
                self._parse_configuration(content, str(relative_path), file_path)
            elif "@Component" in content:
                self._parse_component(content, str(relative_path), file_path)
            elif "@FeignClient" in content or "@RestTemplate" in content:
                self._parse_rest_client(content, str(relative_path), file_path)
            elif "DTO" in file_path.name or "Dto" in file_path.name or "Request" in file_path.name or "Response" in file_path.name:
                self._parse_dto(content, str(relative_path), file_path)

        except Exception as e:
            print(f"Error parsing {file_path}: {e}")

    def _parse_controller(self, content: str, relative_path: str, file_path: Path):
        """Parse a Spring Boot REST controller."""
        # Extract package name
        package_match = re.search(r"package\s+([\w.]+);", content)
        package_name = package_match.group(1) if package_match else ""

        # Extract class name
        class_match = re.search(r"(?:public\s+)?class\s+(\w+)", content)
        if not class_match:
            return

        class_name = class_match.group(1)

        # Determine if it's a REST controller
        is_rest = "@RestController" in content

        # Extract @RequestMapping base path
        base_path_match = re.search(
            r'@RequestMapping\s*\(\s*(?:value\s*=\s*)?["\']([^"\']*)["\']|@RequestMapping\s*\(\s*path\s*=\s*["\']([^"\']*)["\']',
            content
        )
        base_path = ""
        if base_path_match:
            base_path = base_path_match.group(1) or base_path_match.group(2) or ""

        # Extract constructor dependencies (constructor injection)
        dependencies = self._extract_constructor_dependencies(content, class_name)

        # Extract field dependencies (@Autowired, @Inject)
        field_dependencies = self._extract_field_dependencies(content)
        dependencies.extend(field_dependencies)

        # Extract REST endpoints
        endpoints = self._extract_endpoints(content, base_path, class_name)

        # Extract cross-origin configuration
        cors_config = self._extract_cors_config(content)

        controller = {
            "id": f"{package_name}.{class_name}",
            "name": class_name,
            "type": "rest_controller" if is_rest else "controller",
            "layer": "controller",
            "file_path": relative_path,
            "package": package_name,
            "base_path": base_path,
            "endpoints": endpoints,
            "dependencies": dependencies,
            "calls": list(set(dep["type"] for dep in dependencies)),
            "cors_enabled": cors_config is not None,
            "cors_config": cors_config,
            "line_start": self._get_class_line_number(content, class_name),
        }

        self.controllers.append(controller)

    def _parse_service(self, content: str, relative_path: str, file_path: Path):
        """Parse a Spring Boot service."""
        package_match = re.search(r"package\s+([\w.]+);", content)
        package_name = package_match.group(1) if package_match else ""

        class_match = re.search(r"(?:public\s+)?(?:class|interface)\s+(\w+)", content)
        if not class_match:
            return

        class_name = class_match.group(1)

        # Check if it's an interface
        is_interface = "interface" in content and f"interface {class_name}" in content

        # Extract dependencies
        dependencies = self._extract_constructor_dependencies(content, class_name)
        field_dependencies = self._extract_field_dependencies(content)
        dependencies.extend(field_dependencies)

        # Extract public methods
        methods = self._extract_methods(content)

        # Check for transactional methods
        has_transactions = "@Transactional" in content

        service = {
            "id": f"{package_name}.{class_name}",
            "name": class_name,
            "type": "service_interface" if is_interface else "service",
            "layer": "service",
            "file_path": relative_path,
            "package": package_name,
            "dependencies": dependencies,
            "methods": methods,
            "calls": list(set(dep["type"] for dep in dependencies)),
            "has_transactions": has_transactions,
            "line_start": self._get_class_line_number(content, class_name),
        }

        self.services.append(service)

    def _parse_repository(self, content: str, relative_path: str, file_path: Path):
        """Parse a Spring Data repository."""
        package_match = re.search(r"package\s+([\w.]+);", content)
        package_name = package_match.group(1) if package_match else ""

        # Repositories are typically interfaces
        interface_match = re.search(r"(?:public\s+)?interface\s+(\w+)", content)
        if not interface_match:
            return

        interface_name = interface_match.group(1)

        # Extract entity type from extends clause
        # e.g., extends JpaRepository<User, Long>
        entity_type = None
        id_type = None
        extends_match = re.search(
            r"extends\s+(?:JpaRepository|CrudRepository|PagingAndSortingRepository|MongoRepository)<(\w+),\s*(\w+)>",
            content
        )
        if extends_match:
            entity_type = extends_match.group(1)
            id_type = extends_match.group(2)

        # Extract custom query methods
        custom_methods = self._extract_repository_methods(content)

        # Check for custom queries
        has_custom_queries = "@Query" in content
        has_native_queries = "@Query" in content and "nativeQuery" in content

        repository = {
            "id": f"{package_name}.{interface_name}",
            "name": interface_name,
            "type": "repository",
            "layer": "repository",
            "file_path": relative_path,
            "package": package_name,
            "entity_type": entity_type,
            "id_type": id_type,
            "custom_methods": custom_methods,
            "has_custom_queries": has_custom_queries,
            "has_native_queries": has_native_queries,
            "line_start": self._get_class_line_number(content, interface_name),
        }

        self.repositories.append(repository)

    def _parse_entity(self, content: str, relative_path: str, file_path: Path):
        """Parse a JPA entity."""
        package_match = re.search(r"package\s+([\w.]+);", content)
        package_name = package_match.group(1) if package_match else ""

        class_match = re.search(r"(?:public\s+)?class\s+(\w+)", content)
        if not class_match:
            return

        class_name = class_match.group(1)

        # Extract table name
        table_name = class_name.lower()  # default
        table_match = re.search(r'@Table\s*\(\s*name\s*=\s*["\']([^"\']+)["\']', content)
        if table_match:
            table_name = table_match.group(1)

        # Extract fields
        fields = self._extract_entity_fields(content)

        # Extract relationships
        relationships = self._extract_entity_relationships(content)

        # Check for inheritance
        extends_match = re.search(r"extends\s+(\w+)", content)
        parent_class = extends_match.group(1) if extends_match else None

        entity = {
            "id": f"{package_name}.{class_name}",
            "name": class_name,
            "type": "entity",
            "layer": "model",
            "file_path": relative_path,
            "package": package_name,
            "table_name": table_name,
            "fields": fields,
            "relationships": relationships,
            "parent_class": parent_class,
            "line_start": self._get_class_line_number(content, class_name),
        }

        self.entities.append(entity)

    def _parse_dto(self, content: str, relative_path: str, file_path: Path):
        """Parse a DTO (Data Transfer Object)."""
        package_match = re.search(r"package\s+([\w.]+);", content)
        package_name = package_match.group(1) if package_match else ""

        class_match = re.search(r"(?:public\s+)?(?:class|record)\s+(\w+)", content)
        if not class_match:
            return

        class_name = class_match.group(1)

        # Check if it's a record (Java 14+)
        is_record = "record" in content and f"record {class_name}" in content

        # Extract fields
        fields = self._extract_dto_fields(content, is_record)

        # Check for validation annotations
        has_validation = any(anno in content for anno in [
            "@NotNull", "@NotEmpty", "@NotBlank", "@Valid",
            "@Size", "@Min", "@Max", "@Email", "@Pattern"
        ])

        dto = {
            "id": f"{package_name}.{class_name}",
            "name": class_name,
            "type": "record" if is_record else "dto",
            "layer": "dto",
            "file_path": relative_path,
            "package": package_name,
            "fields": fields,
            "has_validation": has_validation,
            "line_start": self._get_class_line_number(content, class_name),
        }

        self.dtos.append(dto)

    def _parse_configuration(self, content: str, relative_path: str, file_path: Path):
        """Parse a Spring configuration class."""
        package_match = re.search(r"package\s+([\w.]+);", content)
        package_name = package_match.group(1) if package_match else ""

        class_match = re.search(r"(?:public\s+)?class\s+(\w+)", content)
        if not class_match:
            return

        class_name = class_match.group(1)

        # Extract @Bean methods
        beans = self._extract_bean_definitions(content)

        # Check for component scan
        has_component_scan = "@ComponentScan" in content

        # Check for property source
        property_sources = []
        prop_pattern = r'@PropertySource\s*\(\s*["\']([^"\']+)["\']\s*\)'
        for match in re.finditer(prop_pattern, content):
            property_sources.append(match.group(1))

        configuration = {
            "id": f"{package_name}.{class_name}",
            "name": class_name,
            "type": "configuration",
            "layer": "config",
            "file_path": relative_path,
            "package": package_name,
            "beans": beans,
            "has_component_scan": has_component_scan,
            "property_sources": property_sources,
            "line_start": self._get_class_line_number(content, class_name),
        }

        self.configurations.append(configuration)

    def _parse_component(self, content: str, relative_path: str, file_path: Path):
        """Parse a Spring component."""
        package_match = re.search(r"package\s+([\w.]+);", content)
        package_name = package_match.group(1) if package_match else ""

        class_match = re.search(r"(?:public\s+)?class\s+(\w+)", content)
        if not class_match:
            return

        class_name = class_match.group(1)

        # Extract dependencies
        dependencies = self._extract_constructor_dependencies(content, class_name)
        field_dependencies = self._extract_field_dependencies(content)
        dependencies.extend(field_dependencies)

        # Extract methods
        methods = self._extract_methods(content)

        component = {
            "id": f"{package_name}.{class_name}",
            "name": class_name,
            "type": "component",
            "layer": "component",
            "file_path": relative_path,
            "package": package_name,
            "dependencies": dependencies,
            "methods": methods,
            "calls": list(set(dep["type"] for dep in dependencies)),
            "line_start": self._get_class_line_number(content, class_name),
        }

        self.components.append(component)

    def _parse_rest_client(self, content: str, relative_path: str, file_path: Path):
        """Parse a Feign client or REST template wrapper."""
        package_match = re.search(r"package\s+([\w.]+);", content)
        package_name = package_match.group(1) if package_match else ""

        # Could be interface (Feign) or class (RestTemplate wrapper)
        class_match = re.search(r"(?:public\s+)?(?:interface|class)\s+(\w+)", content)
        if not class_match:
            return

        class_name = class_match.group(1)

        # Check if it's a Feign client
        is_feign = "@FeignClient" in content

        # Extract service name and URL for Feign clients
        service_name = None
        service_url = None
        if is_feign:
            name_match = re.search(r'@FeignClient\s*\([^)]*name\s*=\s*["\']([^"\']+)["\']', content)
            url_match = re.search(r'@FeignClient\s*\([^)]*url\s*=\s*["\']([^"\']+)["\']', content)
            service_name = name_match.group(1) if name_match else None
            service_url = url_match.group(1) if url_match else None

        # Extract methods (API calls)
        methods = self._extract_methods(content)

        rest_client = {
            "id": f"{package_name}.{class_name}",
            "name": class_name,
            "type": "feign_client" if is_feign else "rest_client",
            "layer": "client",
            "file_path": relative_path,
            "package": package_name,
            "service_name": service_name,
            "service_url": service_url,
            "methods": methods,
            "line_start": self._get_class_line_number(content, class_name),
        }

        self.rest_clients.append(rest_client)

    # ==================== Helper Methods ====================

    def _extract_endpoints(self, content: str, base_path: str, class_name: str) -> List[Dict[str, Any]]:
        """Extract REST endpoints from controller."""
        endpoints = []

        # Patterns for different HTTP methods
        http_patterns = [
            (r'@GetMapping\s*\(\s*(?:value\s*=\s*)?["\']([^"\']*)["\']', "GET"),
            (r'@PostMapping\s*\(\s*(?:value\s*=\s*)?["\']([^"\']*)["\']', "POST"),
            (r'@PutMapping\s*\(\s*(?:value\s*=\s*)?["\']([^"\']*)["\']', "PUT"),
            (r'@DeleteMapping\s*\(\s*(?:value\s*=\s*)?["\']([^"\']*)["\']', "DELETE"),
            (r'@PatchMapping\s*\(\s*(?:value\s*=\s*)?["\']([^"\']*)["\']', "PATCH"),
            (r'@RequestMapping\s*\([^)]*method\s*=\s*RequestMethod\.(\w+)[^)]*value\s*=\s*["\']([^"\']*)["\']', None),
        ]

        # Find all method definitions with their annotations
        method_pattern = r'(@\w+[^}]*?)\s+(?:public|private|protected)?\s+\w+\s+(\w+)\s*\('

        for method_match in re.finditer(method_pattern, content, re.DOTALL):
            annotations = method_match.group(1)
            method_name = method_match.group(2)

            for pattern, http_method in http_patterns:
                for mapping_match in re.finditer(pattern, annotations):
                    if http_method is None:  # @RequestMapping with method
                        http_method = mapping_match.group(1)
                        path = mapping_match.group(2)
                    else:
                        path = mapping_match.group(1)

                    # Combine base path and endpoint path
                    full_path = f"{base_path}{path}".replace("//", "/")
                    if not full_path.startswith("/"):
                        full_path = "/" + full_path

                    # Extract path variables
                    path_vars = re.findall(r'\{(\w+)\}', full_path)

                    # Check for request body
                    has_request_body = "@RequestBody" in annotations

                    # Check for authentication
                    requires_auth = any(guard in annotations for guard in [
                        "@PreAuthorize", "@Secured", "@RolesAllowed"
                    ])

                    endpoints.append({
                        "path": full_path,
                        "method": http_method,
                        "handler": method_name,
                        "path_variables": path_vars,
                        "has_request_body": has_request_body,
                        "requires_auth": requires_auth,
                    })

        return endpoints

    def _extract_constructor_dependencies(self, content: str, class_name: str) -> List[Dict[str, Any]]:
        """Extract constructor injection dependencies."""
        dependencies = []

        # Find constructor
        constructor_pattern = rf'public\s+{class_name}\s*\(([^)]*)\)'
        constructor_match = re.search(constructor_pattern, content)

        if constructor_match:
            params = constructor_match.group(1)
            # Extract parameter types and names
            param_pattern = r'(?:final\s+)?(\w+(?:<[^>]+>)?)\s+(\w+)'
            for param_match in re.finditer(param_pattern, params):
                param_type = param_match.group(1)
                param_name = param_match.group(2)
                dependencies.append({
                    "type": param_type,
                    "name": param_name,
                    "injection_type": "constructor",
                })

        return dependencies

    def _extract_field_dependencies(self, content: str) -> List[Dict[str, Any]]:
        """Extract field injection dependencies (@Autowired, @Inject)."""
        dependencies = []

        # Pattern for @Autowired or @Inject fields
        field_pattern = r'@(?:Autowired|Inject)\s+(?:private\s+)?(\w+(?:<[^>]+>)?)\s+(\w+);'

        for match in re.finditer(field_pattern, content):
            field_type = match.group(1)
            field_name = match.group(2)
            dependencies.append({
                "type": field_type,
                "name": field_name,
                "injection_type": "field",
            })

        return dependencies

    def _extract_methods(self, content: str) -> List[Dict[str, str]]:
        """Extract public methods."""
        methods = []

        # Pattern for public methods
        method_pattern = r'public\s+(\w+(?:<[^>]+>)?)\s+(\w+)\s*\([^)]*\)'

        for match in re.finditer(method_pattern, content):
            return_type = match.group(1)
            method_name = match.group(2)

            # Skip constructors and getters/setters for brevity
            if return_type == "void" or not method_name.startswith("get") and not method_name.startswith("set"):
                methods.append({
                    "name": method_name,
                    "return_type": return_type,
                })

        return methods[:10]  # Limit to first 10 methods

    def _extract_repository_methods(self, content: str) -> List[Dict[str, str]]:
        """Extract custom repository methods."""
        methods = []

        # Extract method signatures (typically in interfaces)
        method_pattern = r'(?:List<|Optional<)?(\w+)(?:>)?\s+(\w+)\s*\([^)]*\);'

        for match in re.finditer(method_pattern, content):
            return_type = match.group(1)
            method_name = match.group(2)

            methods.append({
                "name": method_name,
                "return_type": return_type,
            })

        return methods

    def _extract_entity_fields(self, content: str) -> List[Dict[str, Any]]:
        """Extract entity fields."""
        fields = []

        # Pattern for private fields
        field_pattern = r'private\s+(\w+(?:<[^>]+>)?)\s+(\w+);'

        for match in re.finditer(field_pattern, content):
            field_type = match.group(1)
            field_name = match.group(2)

            # Check if it's an ID field
            is_id = "@Id" in content and field_name in content

            # Check if it's a generated value
            is_generated = "@GeneratedValue" in content and field_name in content

            fields.append({
                "name": field_name,
                "type": field_type,
                "is_id": is_id,
                "is_generated": is_generated,
            })

        return fields

    def _extract_entity_relationships(self, content: str) -> List[Dict[str, str]]:
        """Extract JPA relationships."""
        relationships = []

        relationship_types = [
            ("@OneToOne", "one_to_one"),
            ("@OneToMany", "one_to_many"),
            ("@ManyToOne", "many_to_one"),
            ("@ManyToMany", "many_to_many"),
        ]

        for annotation, rel_type in relationship_types:
            if annotation in content:
                # Find fields with this annotation
                pattern = rf'{annotation}[^;]*?private\s+(\w+(?:<[^>]+>)?)\s+(\w+);'
                for match in re.finditer(pattern, content, re.DOTALL):
                    target_type = match.group(1)
                    field_name = match.group(2)
                    relationships.append({
                        "type": rel_type,
                        "target": target_type,
                        "field": field_name,
                    })

        return relationships

    def _extract_dto_fields(self, content: str, is_record: bool) -> List[Dict[str, str]]:
        """Extract DTO fields."""
        fields = []

        if is_record:
            # For records, extract from record header
            record_pattern = r'record\s+\w+\s*\(([^)]+)\)'
            record_match = re.search(record_pattern, content)
            if record_match:
                params = record_match.group(1)
                param_pattern = r'(\w+(?:<[^>]+>)?)\s+(\w+)'
                for param_match in re.finditer(param_pattern, params):
                    fields.append({
                        "name": param_match.group(2),
                        "type": param_match.group(1),
                    })
        else:
            # For classes, extract private fields
            field_pattern = r'private\s+(\w+(?:<[^>]+>)?)\s+(\w+);'
            for match in re.finditer(field_pattern, content):
                fields.append({
                    "name": match.group(2),
                    "type": match.group(1),
                })

        return fields

    def _extract_bean_definitions(self, content: str) -> List[Dict[str, str]]:
        """Extract @Bean method definitions."""
        beans = []

        bean_pattern = r'@Bean[^}]*?public\s+(\w+(?:<[^>]+>)?)\s+(\w+)\s*\('

        for match in re.finditer(bean_pattern, content, re.DOTALL):
            bean_type = match.group(1)
            bean_name = match.group(2)
            beans.append({
                "name": bean_name,
                "type": bean_type,
            })

        return beans

    def _extract_cors_config(self, content: str) -> Optional[Dict[str, Any]]:
        """Extract CORS configuration."""
        if "@CrossOrigin" not in content:
            return None

        # Try to extract origins
        origins = []
        origins_match = re.search(r'@CrossOrigin\s*\([^)]*origins\s*=\s*\{([^}]+)\}', content)
        if origins_match:
            origin_list = origins_match.group(1)
            origins = [o.strip().strip('"\'') for o in origin_list.split(',')]

        return {
            "enabled": True,
            "origins": origins if origins else ["*"],
        }

    def _get_class_line_number(self, content: str, class_name: str) -> int:
        """Get the line number where the class is defined."""
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            if f"class {class_name}" in line or f"interface {class_name}" in line or f"record {class_name}" in line:
                return i
        return 1
