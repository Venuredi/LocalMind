"""
Enhanced NestJS Parser
Extracts controllers, services, DTOs, entities, repositories, GraphQL resolvers, 
Socket.io gateways, Bull queues, MongoDB schemas, and integrations from NestJS TypeScript code.
"""

import re
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


class EnhancedNestJSParser:
    """Parse enhanced NestJS TypeScript files and extract code intelligence."""

    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.controllers: List[Dict[str, Any]] = []
        self.services: List[Dict[str, Any]] = []
        self.dtos: List[Dict[str, Any]] = []
        self.entities: List[Dict[str, Any]] = []
        self.repositories: List[Dict[str, Any]] = []
        self.graphql_resolvers: List[Dict[str, Any]] = []
        self.graphql_mutations: List[Dict[str, Any]] = []
        self.socket_gateways: List[Dict[str, Any]] = []
        self.bull_processors: List[Dict[str, Any]] = []
        self.mongo_schemas: List[Dict[str, Any]] = []
        self.microservices: List[Dict[str, Any]] = []
        self.guards: List[Dict[str, Any]] = []
        self.interceptors: List[Dict[str, Any]] = []
        self.middleware: List[Dict[str, Any]] = []
        self.modules: List[Dict[str, Any]] = []

    def parse(self) -> Dict[str, Any]:
        """Parse the entire NestJS codebase."""
        ts_files = [f for f in self.repo_path.rglob("*.ts") if not _is_excluded(f)]

        for file_path in ts_files:
            self._parse_file(file_path)

        return {
            "controllers": self.controllers,
            "services": self.services,
            "dtos": self.dtos,
            "entities": self.entities,
            "repositories": self.repositories,
            "graphql_resolvers": self.graphql_resolvers,
            "graphql_mutations": self.graphql_mutations,
            "socket_gateways": self.socket_gateways,
            "bull_processors": self.bull_processors,
            "mongo_schemas": self.mongo_schemas,
            "microservices": self.microservices,
            "guards": self.guards,
            "interceptors": self.interceptors,
            "middleware": self.middleware,
            "modules": self.modules,
        }

    def _parse_file(self, file_path: Path):
        """Parse a single TypeScript file."""
        try:
            content = file_path.read_text(encoding="utf-8")
            relative_path = file_path.relative_to(self.repo_path)

            # Skip test files
            if ".spec.ts" in file_path.name or ".test.ts" in file_path.name:
                return

            # Determine file type
            if ".controller.ts" in file_path.name:
                self._parse_controller(content, str(relative_path), file_path)
            elif ".resolver.ts" in file_path.name or ("@Resolver" in content and "@nestjs/graphql" in content):
                self._parse_graphql_resolver(content, str(relative_path), file_path)
            elif ".service.ts" in file_path.name:
                self._parse_service(content, str(relative_path), file_path)
            elif ".dto.ts" in file_path.name:
                self._parse_dto(content, str(relative_path), file_path)
            elif ".entity.ts" in file_path.name:
                self._parse_entity(content, str(relative_path), file_path)
            elif "generated/prisma/models" in str(relative_path) and ".ts" in file_path.name:
                # Parse Prisma generated models
                self._parse_prisma_model(content, str(relative_path), file_path)
            elif ".repository.ts" in file_path.name:
                self._parse_repository(content, str(relative_path), file_path)
            elif ".schema.ts" in file_path.name and "@Schema" in content:
                self._parse_mongo_schema(content, str(relative_path), file_path)
            elif ".gateway.ts" in file_path.name or "@WebSocketGateway" in content:
                self._parse_socket_gateway(content, str(relative_path), file_path)
            elif "@Processor" in content:
                self._parse_bull_processor(content, str(relative_path), file_path)
            elif ".guard.ts" in file_path.name or "@Injectable" in content and "CanActivate" in content:
                self._parse_guard(content, str(relative_path), file_path)
            elif ".interceptor.ts" in file_path.name or "NestInterceptor" in content:
                self._parse_interceptor(content, str(relative_path), file_path)
            elif ".middleware.ts" in file_path.name or "NestMiddleware" in content:
                self._parse_middleware(content, str(relative_path), file_path)
            elif ".module.ts" in file_path.name and "@Module" in content:
                self._parse_module(content, str(relative_path), file_path)
            # FALLBACK: Capture any @Injectable class not caught above as a service
            # This ensures we don't miss services with non-standard naming
            elif "@Injectable" in content and "export class" in content:
                # Double-check it's not a specialized injectable (guard/interceptor/middleware)
                # Those should have been caught by specific parsers above
                if ("CanActivate" not in content and
                    "NestInterceptor" not in content and
                    "NestMiddleware" not in content):
                    self._parse_service(content, str(relative_path), file_path)

        except Exception as e:
            print(f"Error parsing {file_path}: {e}")

    def _parse_controller(self, content: str, relative_path: str, file_path: Path):
        """Parse a NestJS controller with enhanced features."""
        class_match = re.search(r"export\s+class\s+(\w+)\s", content)
        if not class_match:
            return

        class_name = class_match.group(1)

        # Extract @Controller decorator
        controller_decorator = re.search(
            r"@Controller\(['\"]?([^'\"\)]*)['\"]?\)", content
        )
        base_route = controller_decorator.group(1) if controller_decorator else ""

        # Extract constructor dependencies
        dependencies = self._extract_constructor_dependencies(content)

        # Extract routes with enhanced HTTP methods
        routes = self._extract_routes(content, base_route)

        # Extract Swagger/OpenAPI decorators
        swagger_decorators = self._extract_swagger_decorators(content)

        # Extract authentication guards
        auth_guards = self._extract_auth_guards(content)

        # Extract throttling/rate limiting
        throttling = self._extract_throttling(content)

        controller = {
            "id": class_name,
            "name": class_name,
            "type": "controller",
            "layer": "backend",
            "file_path": relative_path,
            "base_route": f"/{base_route}" if base_route else "/",
            "routes": routes,
            "dependencies": dependencies,
            "swagger": swagger_decorators,
            "auth_guards": auth_guards,
            "throttling": throttling,
            "calls": [dep["type"] for dep in dependencies],
            "line_start": self._get_class_line_number(content, class_name),
        }

        self.controllers.append(controller)

    def _parse_graphql_resolver(self, content: str, relative_path: str, file_path: Path):
        """Parse a GraphQL resolver."""
        class_match = re.search(r"export\s+class\s+(\w+)\s", content)
        if not class_match or "@Resolver" not in content:
            return

        class_name = class_match.group(1)

        # Extract @Resolver decorator
        resolver_match = re.search(r"@Resolver\(['\"]?(\w+)?['\"]?\)", content)
        resolver_type = resolver_match.group(1) if resolver_match else None

        # Extract constructor dependencies
        dependencies = self._extract_constructor_dependencies(content)

        # Extract queries
        queries = self._extract_graphql_queries(content)

        # Extract mutations
        mutations = self._extract_graphql_mutations(content)

        # Extract subscriptions
        subscriptions = self._extract_graphql_subscriptions(content)

        # Extract field resolvers
        field_resolvers = self._extract_field_resolvers(content)

        resolver = {
            "id": class_name,
            "name": class_name,
            "type": "graphql_resolver",
            "layer": "backend",
            "file_path": relative_path,
            "resolver_type": resolver_type,
            "dependencies": dependencies,
            "queries": queries,
            "mutations": mutations,
            "subscriptions": subscriptions,
            "field_resolvers": field_resolvers,
            "calls": [dep["type"] for dep in dependencies],
            "line_start": self._get_class_line_number(content, class_name),
        }

        self.graphql_resolvers.append(resolver)

        # Also add mutations separately for quick lookup
        for mutation in mutations:
            self.graphql_mutations.append({
                "resolver": class_name,
                **mutation
            })

    def _parse_service(self, content: str, relative_path: str, file_path: Path):
        """Parse a NestJS service with enhanced features."""
        class_match = re.search(r"export\s+class\s+(\w+)\s", content)
        if not class_match:
            return

        class_name = class_match.group(1)

        # Check if it's a service
        if "@Injectable" not in content:
            return

        # Extract constructor dependencies
        dependencies = self._extract_constructor_dependencies(content)

        # Extract methods
        methods = self._extract_service_methods(content)

        # Extract MongoDB/Mongoose usage
        mongo_usage = self._extract_mongo_usage(content)

        # Extract Redis usage
        redis_usage = self._extract_redis_usage(content)

        # Extract Bull queue usage
        bull_usage = self._extract_bull_usage(content)

        # Extract HTTP client usage (Axios)
        http_usage = self._extract_http_usage(content)

        # Extract external integrations
        integrations = self._extract_integrations(content)

        # Extract event emitter usage
        event_usage = self._extract_event_usage(content)

        # Extract schedule/cron jobs
        scheduled_jobs = self._extract_scheduled_jobs(content)

        service = {
            "id": class_name,
            "name": class_name,
            "type": "service",
            "layer": "backend",
            "file_path": relative_path,
            "dependencies": dependencies,
            "methods": methods,
            "mongo_usage": mongo_usage,
            "redis_usage": redis_usage,
            "bull_usage": bull_usage,
            "http_usage": http_usage,
            "integrations": integrations,
            "event_emitter": event_usage,
            "scheduled_jobs": scheduled_jobs,
            "calls": [dep["type"] for dep in dependencies],
            "line_start": self._get_class_line_number(content, class_name),
        }

        self.services.append(service)

    def _parse_mongo_schema(self, content: str, relative_path: str, file_path: Path):
        """Parse MongoDB/Mongoose schema definitions."""
        # Look for @Schema decorator
        if "@Schema" not in content:
            return

        class_match = re.search(r"export\s+class\s+(\w+)\s", content)
        if not class_match:
            return

        class_name = class_match.group(1)

        # Extract @Prop decorated fields
        fields = []
        prop_pattern = r"@Prop\([^)]*\)\s*(\w+)\s*:\s*(\w+)"
        matches = re.finditer(prop_pattern, content)
        
        for match in matches:
            fields.append({
                "name": match.group(1),
                "type": match.group(2),
            })

        # Extract schema options
        schema_match = re.search(r"@Schema\(([^)]*)\)", content)
        schema_options = schema_match.group(1) if schema_match else ""

        schema = {
            "id": class_name,
            "name": class_name,
            "type": "mongo_schema",
            "layer": "data",
            "file_path": relative_path,
            "fields": fields,
            "schema_options": schema_options,
            "line_start": self._get_class_line_number(content, class_name),
        }

        self.mongo_schemas.append(schema)

    def _parse_socket_gateway(self, content: str, relative_path: str, file_path: Path):
        """Parse Socket.io WebSocket gateway."""
        class_match = re.search(r"export\s+class\s+(\w+)\s", content)
        if not class_match or "@WebSocketGateway" not in content:
            return

        class_name = class_match.group(1)

        # Extract gateway namespace
        gateway_match = re.search(r"@WebSocketGateway\(([^)]*)\)", content)
        namespace = gateway_match.group(1) if gateway_match else "default"

        # Extract constructor dependencies
        dependencies = self._extract_constructor_dependencies(content)

        # Extract @SubscribeMessage handlers
        handlers = []
        message_pattern = r"@SubscribeMessage\(['\"]([^'\"]+)['\"]\)"
        method_pattern = r"(\w+)\s*\([^)]*\)\s*:\s*(?:Observable|Promise)?"
        
        for msg_match in re.finditer(message_pattern, content):
            event_name = msg_match.group(1)
            handlers.append({
                "event": event_name,
                "method": None,  # Will be matched below
            })

        # Extract @WebSocketServer
        has_server = "@WebSocketServer" in content

        gateway = {
            "id": class_name,
            "name": class_name,
            "type": "socket_gateway",
            "layer": "backend",
            "file_path": relative_path,
            "namespace": namespace,
            "dependencies": dependencies,
            "message_handlers": handlers,
            "has_server": has_server,
            "calls": [dep["type"] for dep in dependencies],
            "line_start": self._get_class_line_number(content, class_name),
        }

        self.socket_gateways.append(gateway)

    def _parse_bull_processor(self, content: str, relative_path: str, file_path: Path):
        """Parse Bull queue processor."""
        class_match = re.search(r"export\s+class\s+(\w+)\s", content)
        if not class_match:
            return

        class_name = class_match.group(1)

        # Extract @Processor decorator
        processor_match = re.search(r"@Processor\(['\"]([^'\"]+)['\"]\)", content)
        queue_name = processor_match.group(1) if processor_match else "default"

        # Extract @Process handlers
        processes = []
        process_pattern = r"@Process\(['\"]([^'\"]+)['\"]\)"
        
        for match in re.finditer(process_pattern, content):
            processes.append(match.group(1))

        # Extract constructor dependencies
        dependencies = self._extract_constructor_dependencies(content)

        processor = {
            "id": class_name,
            "name": class_name,
            "type": "bull_processor",
            "layer": "backend",
            "file_path": relative_path,
            "queue_name": queue_name,
            "processes": processes,
            "dependencies": dependencies,
            "calls": [dep["type"] for dep in dependencies],
            "line_start": self._get_class_line_number(content, class_name),
        }

        self.bull_processors.append(processor)

    def _parse_guard(self, content: str, relative_path: str, file_path: Path):
        """Parse authentication/authorization guards."""
        class_match = re.search(r"export\s+class\s+(\w+)\s", content)
        if not class_match or "CanActivate" not in content:
            return

        class_name = class_match.group(1)

        # Determine guard type
        guard_types = []
        if "CanActivate" in content:
            guard_types.append("CanActivate")
        if "CanActivateChild" in content:
            guard_types.append("CanActivateChild")

        # Check for JWT, Roles, etc.
        strategy = None
        if "jwt" in content.lower() or "JwtAuthGuard" in content:
            strategy = "jwt"
        elif "roles" in content.lower() or "RolesGuard" in content:
            strategy = "roles"
        elif "permissions" in content.lower():
            strategy = "permissions"

        guard = {
            "id": class_name,
            "name": class_name,
            "type": "guard",
            "layer": "backend",
            "file_path": relative_path,
            "guard_types": guard_types,
            "strategy": strategy,
            "line_start": self._get_class_line_number(content, class_name),
        }

        self.guards.append(guard)

    def _parse_interceptor(self, content: str, relative_path: str, file_path: Path):
        """Parse interceptors."""
        class_match = re.search(r"export\s+class\s+(\w+)\s", content)
        if not class_match or "NestInterceptor" not in content:
            return

        class_name = class_match.group(1)

        # Determine interceptor type
        interceptor_type = "generic"
        if "logging" in content.lower() or "Log" in class_name:
            interceptor_type = "logging"
        elif "transform" in content.lower() or "Transform" in class_name:
            interceptor_type = "transform"
        elif "cache" in content.lower() or "Cache" in class_name:
            interceptor_type = "cache"
        elif "error" in content.lower() or "Error" in class_name:
            interceptor_type = "error"
        elif "timeout" in content.lower() or "Timeout" in class_name:
            interceptor_type = "timeout"

        interceptor = {
            "id": class_name,
            "name": class_name,
            "type": "interceptor",
            "layer": "backend",
            "file_path": relative_path,
            "interceptor_type": interceptor_type,
            "line_start": self._get_class_line_number(content, class_name),
        }

        self.interceptors.append(interceptor)

    def _parse_middleware(self, content: str, relative_path: str, file_path: Path):
        """Parse middleware."""
        class_match = re.search(r"export\s+class\s+(\w+)\s", content)
        if not class_match or "NestMiddleware" not in content:
            return

        class_name = class_match.group(1)

        middleware = {
            "id": class_name,
            "name": class_name,
            "type": "middleware",
            "layer": "backend",
            "file_path": relative_path,
            "line_start": self._get_class_line_number(content, class_name),
        }

        self.middleware.append(middleware)

    def _parse_module(self, content: str, relative_path: str, file_path: Path):
        """Parse NestJS module."""
        class_match = re.search(r"export\s+class\s+(\w+)\s", content)
        if not class_match or "@Module" not in content:
            return

        class_name = class_match.group(1)

        # Extract @Module metadata
        module_match = re.search(r"@Module\(\s*\{([^}]*)\}\s*\)", content, re.DOTALL)
        metadata = {}
        
        if module_match:
            decorator_content = module_match.group(1)
            
            # Extract controllers
            controllers_match = re.search(r"controllers:\s*\[([^\]]+)\]", decorator_content)
            if controllers_match:
                metadata["controllers"] = [c.strip() for c in controllers_match.group(1).split(",")]
            
            # Extract providers
            providers_match = re.search(r"providers:\s*\[([^\]]+)\]", decorator_content)
            if providers_match:
                metadata["providers"] = [p.strip() for p in providers_match.group(1).split(",")]
            
            # Extract imports
            imports_match = re.search(r"imports:\s*\[([^\]]+)\]", decorator_content)
            if imports_match:
                metadata["imports"] = [i.strip() for i in imports_match.group(1).split(",")]
            
            # Extract exports
            exports_match = re.search(r"exports:\s*\[([^\]]+)\]", decorator_content)
            if exports_match:
                metadata["exports"] = [e.strip() for e in exports_match.group(1).split(",")]

        module = {
            "id": class_name,
            "name": class_name,
            "type": "module",
            "layer": "backend",
            "file_path": relative_path,
            "controllers": metadata.get("controllers", []),
            "providers": metadata.get("providers", []),
            "imports": metadata.get("imports", []),
            "exports": metadata.get("exports", []),
            "line_start": self._get_class_line_number(content, class_name),
        }

        self.modules.append(module)

    def _parse_dto(self, content: str, relative_path: str, file_path: Path):
        """Parse DTO with enhanced validation decorators."""
        class_match = re.search(r"export\s+class\s+(\w+)\s", content)
        if not class_match:
            return

        class_name = class_match.group(1)

        # Check if it's actually a DTO (has class-validator decorators)
        if not any(d in content for d in ["@IsString", "@IsNumber", "@IsEmail", "@Validate", "@IsOptional"]):
            return

        # Extract properties with decorators
        properties = []
        
        # Pattern for decorated properties: @Decorator() prop: type
        prop_patterns = [
            r"@(\w+)\([^)]*\)\s+(\w+):\s+(\w+)",
            r"@(\w+)\s+(\w+):\s+(\w+)",
        ]
        
        for pattern in prop_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                decorator = match.group(1)
                prop_name = match.group(2)
                prop_type = match.group(3)
                
                if decorator not in ["Injectable", "Controller", "Module"]:
                    properties.append({
                        "name": prop_name,
                        "type": prop_type,
                        "validators": [decorator],
                    })

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
        """Parse TypeORM entity."""
        class_match = re.search(r"export\s+class\s+(\w+)\s", content)
        if not class_match or "@Entity" not in content:
            return

        class_name = class_match.group(1)

        # Extract @Entity decorator
        entity_match = re.search(r"@Entity\(['\"]?(\w+)?['\"]?\)", content)
        table_name = entity_match.group(1) if entity_match else class_name.lower()

        # Extract columns
        columns = []
        column_pattern = r"@(\w+)\([^)]*\)\s+(\w+):\s+(\w+)"
        matches = re.finditer(column_pattern, content)
        
        for match in matches:
            decorator = match.group(1)
            col_name = match.group(2)
            col_type = match.group(3)
            
            if decorator in ["Column", "PrimaryGeneratedColumn", "CreateDateColumn", "UpdateDateColumn", "PrimaryColumn"]:
                columns.append({
                    "name": col_name,
                    "type": col_type,
                    "decorator": decorator,
                })

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

    def _parse_prisma_model(self, content: str, relative_path: str, file_path: Path):
        """Parse Prisma generated model files."""
        # Extract model name from export type statements
        model_match = re.search(r"export\s+type\s+(\w+Model)\s*=", content)
        if not model_match:
            return

        model_name = model_match.group(1).replace("Model", "")

        # Extract type definitions
        type_exports = []
        type_pattern = r"export\s+type\s+(\w+)\s*="
        for match in re.finditer(type_pattern, content):
            type_exports.append(match.group(1))

        # Extract enum references
        enum_refs = []
        enum_pattern = r"\$Enums\.(\w+)"
        for match in re.finditer(enum_pattern, content):
            enum_name = match.group(1)
            if enum_name not in enum_refs:
                enum_refs.append(enum_name)

        entity = {
            "id": model_name,
            "name": model_name,
            "type": "prisma_model",
            "layer": "data",
            "file_path": relative_path,
            "types": type_exports,
            "enums_used": enum_refs,
            "line_start": 1,
        }

        self.entities.append(entity)

    def _parse_repository(self, content: str, relative_path: str, file_path: Path):
        """Parse TypeORM repository."""
        class_match = re.search(r"export\s+class\s+(\w+)\s", content)
        if not class_match:
            return

        class_name = class_match.group(1)

        # Check if it's an EntityRepository
        if "@EntityRepository" not in content and "Repository<" not in content:
            return

        # Extract entity type
        entity_match = re.search(r"Repository<(\w+)>", content)
        associated_entity = entity_match.group(1) if entity_match else None

        # Extract methods
        methods = self._extract_service_methods(content)

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

    def _extract_routes(self, content: str, base_route: str) -> List[Dict[str, Any]]:
        """Extract route methods from controller with enhanced methods."""
        routes = []

        # Pattern for route decorators including @All, @Head, @Options
        route_pattern = r"@(Get|Post|Put|Delete|Patch|All|Head|Options)\(['\"]?([^'\"\)]*)['\"]?\)"

        # Find all route decorators and their following methods
        for match in re.finditer(route_pattern, content):
            http_method = match.group(1).upper()
            route_path = match.group(2) or ""

            # Find the method name that follows (skip decorators)
            pos = match.end()
            next_content = content[pos:pos+1000]  # Increased to handle many decorators

            # Skip all decorator lines (lines starting with @)
            # Pattern: skip whitespace and decorators, then find the actual method
            method_match = re.search(r"(?:^\s*@[\w\.]+\([^)]*\)\s*$\s*)*\s*(?:async\s+)?(\w+)\s*\(", next_content, re.MULTILINE)

            if method_match:
                method_name = method_match.group(1)
                
                # Build full route
                full_route = f"/{base_route}".rstrip("/")
                if route_path:
                    full_route = f"{full_route}/{route_path}".replace("//", "/")
                
                # Extract method body
                method_body = self._extract_method_body(content, method_name)
                service_calls = self._extract_service_calls(method_body)
                
                # Extract DTOs
                dtos_used = self._extract_dtos_from_method(content, method_name)
                
                line_number = content[:match.start()].count("\n") + 1

                routes.append({
                    "method": http_method,
                    "path": full_route,
                    "handler": method_name,
                    "service_calls": service_calls,
                    "dtos": dtos_used,
                    "line_number": line_number,
                })

        return routes

    def _extract_graphql_queries(self, content: str) -> List[Dict[str, Any]]:
        """Extract @Query decorators."""
        queries = []
        query_pattern = r"@Query\(['\"]?(\w+)?['\"]?\)"
        
        for match in re.finditer(query_pattern, content):
            name = match.group(1)
            line_number = content[:match.start()].count("\n") + 1
            
            queries.append({
                "name": name,
                "type": "query",
                "line_number": line_number,
            })

        return queries

    def _extract_graphql_mutations(self, content: str) -> List[Dict[str, Any]]:
        """Extract @Mutation decorators."""
        mutations = []
        mutation_pattern = r"@Mutation\(['\"]?(\w+)?['\"]?\)"
        
        for match in re.finditer(mutation_pattern, content):
            name = match.group(1)
            line_number = content[:match.start()].count("\n") + 1
            
            mutations.append({
                "name": name,
                "type": "mutation",
                "line_number": line_number,
            })

        return mutations

    def _extract_graphql_subscriptions(self, content: str) -> List[Dict[str, Any]]:
        """Extract @Subscription decorators."""
        subscriptions = []
        subscription_pattern = r"@Subscription\(['\"]?(\w+)?['\"]?\)"
        
        for match in re.finditer(subscription_pattern, content):
            name = match.group(1)
            line_number = content[:match.start()].count("\n") + 1
            
            subscriptions.append({
                "name": name,
                "type": "subscription",
                "line_number": line_number,
            })

        return subscriptions

    def _extract_field_resolvers(self, content: str) -> List[Dict[str, Any]]:
        """Extract @ResolveField decorators."""
        resolvers = []
        resolver_pattern = r"@ResolveField\(['\"]?(\w+)?['\"]?\)"
        
        for match in re.finditer(resolver_pattern, content):
            name = match.group(1)
            line_number = content[:match.start()].count("\n") + 1
            
            resolvers.append({
                "name": name,
                "type": "field_resolver",
                "line_number": line_number,
            })

        return resolvers

    def _extract_swagger_decorators(self, content: str) -> List[str]:
        """Extract Swagger/OpenAPI decorators."""
        swagger_decs = []
        swagger_pattern = r"@(ApiOperation|ApiResponse|ApiBody|ApiQuery|ApiParam|ApiTags|ApiBearerAuth)\("
        
        for match in re.finditer(swagger_pattern, content):
            swagger_decs.append(match.group(1))

        return list(set(swagger_decs))

    def _extract_auth_guards(self, content: str) -> List[str]:
        """Extract authentication guards."""
        guards = []
        
        # Look for @UseGuards
        guards_pattern = r"@UseGuards\(([^)]+)\)"
        matches = re.finditer(guards_pattern, content)
        
        for match in matches:
            guard_list = match.group(1)
            guards.extend([g.strip() for g in guard_list.split(",")])

        return guards

    def _extract_throttling(self, content: str) -> Dict[str, Any]:
        """Extract throttling/rate limiting decorators."""
        throttling = {
            "has_skip_throttle": "@SkipThrottle" in content,
            "has_throttle": "@Throttle" in content,
        }
        return throttling

    def _extract_constructor_dependencies(self, content: str) -> List[Dict[str, Any]]:
        """Extract constructor dependencies."""
        dependencies = []
        
        constructor_match = re.search(
            r"constructor\((.*?)\)\s*\{", content, re.DOTALL
        )
        
        if constructor_match:
            params = constructor_match.group(1)
            dep_matches = re.findall(
                r"(?:private|public|protected)\s+(?:readonly\s+)?(\w+):\s+(\w+)",
                params,
            )
            dependencies = [
                {"name": dep[0], "type": dep[1]} for dep in dep_matches
            ]

        return dependencies

    def _extract_service_methods(self, content: str) -> List[Dict[str, Any]]:
        """Extract methods from a service class."""
        methods = []
        method_pattern = r"(?:async\s+)?(\w+)\s*\([^)]*\)(?:\s*:\s*Promise<[^>]+>)?\s*\{"
        
        matches = re.finditer(method_pattern, content)
        
        for match in matches:
            method_name = match.group(1)
            if method_name == "constructor":
                continue
            
            line_number = content[:match.start()].count("\n") + 1
            
            methods.append({
                "name": method_name,
                "line_number": line_number,
            })

        return methods

    def _extract_mongo_usage(self, content: str) -> Dict[str, Any]:
        """Extract MongoDB/Mongoose usage patterns."""
        usage = {
            "model_injected": False,
            "models": [],
            "operations": [],
        }
        
        # Check for @InjectModel
        if "@InjectModel" in content:
            usage["model_injected"] = True
            model_matches = re.findall(r"@InjectModel\(['\"](\w+)['\"]\)", content)
            usage["models"] = model_matches
        
        # Extract common Mongoose operations
        operations = []
        mongo_ops = ["find", "findOne", "findById", "create", "updateOne", "deleteOne", "aggregate", "populate"]
        for op in mongo_ops:
            if f".{op}(" in content:
                operations.append(op)
        
        usage["operations"] = operations
        return usage

    def _extract_redis_usage(self, content: str) -> Dict[str, Any]:
        """Extract Redis usage."""
        usage = {
            "has_redis": "redis" in content.lower() or "Redis" in content,
            "operations": [],
        }
        
        redis_ops = ["get", "set", "del", "expire", "ttl", "incr", "decr", "keys", "flushall"]
        for op in redis_ops:
            if f"redis.{op}(" in content or f".redis.{op}(" in content:
                usage["operations"].append(op)

        return usage

    def _extract_bull_usage(self, content: str) -> Dict[str, Any]:
        """Extract Bull queue usage."""
        usage = {
            "has_bull": "@InjectQueue" in content or "Bull" in content,
            "queues": [],
        }
        
        queue_matches = re.findall(r"@InjectQueue\(['\"](\w+)['\"]\)", content)
        usage["queues"] = queue_matches

        return usage

    def _extract_http_usage(self, content: str) -> Dict[str, Any]:
        """Extract HTTP client usage."""
        usage = {
            "has_http": "HttpService" in content or "axios" in content.lower(),
            "client": None,
        }
        
        if "HttpService" in content:
            usage["client"] = "HttpService"
        elif "axios" in content.lower():
            usage["client"] = "axios"

        return usage

    def _extract_integrations(self, content: str) -> Dict[str, Any]:
        """Extract third-party service integrations."""
        integrations = {}
        
        # Payment
        if "stripe" in content.lower():
            integrations["stripe"] = True
        if "plaid" in content.lower():
            integrations["plaid"] = True
        if "dwolla" in content.lower():
            integrations["dwolla"] = True
        
        # Communication
        if "twilio" in content.lower():
            integrations["twilio"] = True
        if "slack" in content.lower():
            integrations["slack"] = True
        if "mailchimp" in content.lower():
            integrations["mailchimp"] = True
        
        # Maps/Geo
        if "mapbox" in content.lower() or "google.maps" in content.lower():
            integrations["maps"] = True
        if "geocoder" in content.lower():
            integrations["geocoding"] = True
        
        # Storage
        if "s3" in content.lower() or "aws" in content.lower():
            integrations["aws_s3"] = True
        
        # GitHub
        if "octokit" in content.lower() or "github" in content.lower():
            integrations["github"] = True
        
        # EDI
        if "edi" in content.lower():
            integrations["edi"] = True
        
        # File processing
        if "xlsx" in content.lower() or "exceljs" in content.lower():
            integrations["excel"] = True
        if "pdf" in content.lower():
            integrations["pdf"] = True

        return integrations

    def _extract_event_usage(self, content: str) -> Dict[str, Any]:
        """Extract event emitter usage."""
        usage = {
            "has_event_emitter": "EventEmitter" in content or "@EventEmitter" in content,
            "emits": [],
            "listeners": [],
        }
        
        # Extract emits
        emit_matches = re.findall(r"eventEmitter\.emit\(['\"](\w+)['\"]", content)
        usage["emits"] = emit_matches
        
        # Extract @OnEvent listeners
        listener_matches = re.findall(r"@OnEvent\(['\"](\w+)['\"]\)", content)
        usage["listeners"] = listener_matches

        return usage

    def _extract_scheduled_jobs(self, content: str) -> List[Dict[str, Any]]:
        """Extract @Cron and @Interval decorators."""
        jobs = []
        
        # Cron jobs
        cron_pattern = r"@Cron\(['\"]([^'\"]+)['\"]\)"
        for match in re.finditer(cron_pattern, content):
            jobs.append({
                "type": "cron",
                "pattern": match.group(1),
            })
        
        # Interval jobs
        interval_pattern = r"@Interval\(['\"]?(\w+)?['\"]?\,\s*(\d+)\)"
        for match in re.finditer(interval_pattern, content):
            jobs.append({
                "type": "interval",
                "name": match.group(1),
                "milliseconds": int(match.group(2)),
            })
        
        # Timeout jobs
        timeout_pattern = r"@Timeout\(['\"]?(\w+)?['\"]?\,\s*(\d+)\)"
        for match in re.finditer(timeout_pattern, content):
            jobs.append({
                "type": "timeout",
                "name": match.group(1),
                "milliseconds": int(match.group(2)),
            })

        return jobs

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

        return content[start:i - 1]

    def _extract_service_calls(self, method_body: str) -> List[str]:
        """Extract service method calls."""
        pattern = r"this\.(\w+)\.(\w+)\("
        matches = re.findall(pattern, method_body)
        return [f"{service}.{method}" for service, method in matches]

    def _extract_dtos_from_method(self, content: str, method_name: str) -> List[str]:
        """Extract DTOs used in method parameters."""
        pattern = rf"{method_name}\s*\([^)]*@Body\(\)\s*\w+:\s*(\w+)"
        matches = re.findall(pattern, content)
        return matches

    def _get_class_line_number(self, content: str, class_name: str) -> int:
        """Get line number where class is defined."""
        pattern = rf"export\s+class\s+{class_name}"
        match = re.search(pattern, content)
        if match:
            return content[:match.start()].count("\n") + 1
        return 0
