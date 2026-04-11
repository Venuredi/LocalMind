"""
Parser Adapter
Converts framework-specific parser outputs to unified ontology format.

This adapter bridges the gap between specialized parsers (NestJS, Angular, React)
and the generic ontology generator that expects a standard entity structure.
"""

from typing import Dict, List, Any, Optional
from pathlib import Path


class ParserAdapter:
    """
    Converts framework-specific parser outputs to unified ontology format.

    Each framework parser (NestJS, Angular, React) has its own output structure.
    This adapter normalizes them into a common format that the ontology generator
    can process.
    """

    def __init__(self):
        self.framework_handlers = {
            "nestjs": self.adapt_nestjs,
            "angular": self.adapt_angular,
            "react": self.adapt_react,
        }

    def adapt(self, framework: str, parser_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Adapt framework-specific parser data to ontology format.

        Args:
            framework: Framework type (nestjs, angular, react)
            parser_data: Raw parser output

        Returns:
            Normalized ontology-compatible data structure
        """
        handler = self.framework_handlers.get(framework.lower())

        if not handler:
            raise ValueError(f"Unsupported framework: {framework}")

        return handler(parser_data)

    def adapt_nestjs(self, nestjs_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert NestJS parser output to ontology format.

        NestJS parser outputs:
            - controllers (with routes)
            - services (with methods)
            - dtos (with properties)
            - entities (with columns)
            - repositories
            - graphql_resolvers
            - socket_gateways
            - bull_processors
            - mongo_schemas
            - guards, interceptors, middleware, modules

        Converts to:
            - entities: {
                classes: [...],
                methods: [...],
                api_endpoints: [...],
                dtos: [...],
                repositories: [...],
                ...
              }
        """
        entities = {
            "classes": [],
            "functions": [],
            "methods": [],
            "api_endpoints": [],
            "dtos": [],
            "repositories": [],
            "entities": [],
            "graphql_resolvers": [],
            "socket_gateways": [],
            "bull_processors": [],
            "guards": [],
            "interceptors": [],
            "middleware": [],
            "modules": [],
        }

        # Convert controllers → classes + api_endpoints
        for controller in nestjs_data.get("controllers", []):
            entities["classes"].append({
                "id": controller["id"],
                "name": controller["name"],
                "type": "controller",
                "layer": "backend",
                "file_path": controller["file_path"],
                "line_start": controller.get("line_start", 0),
                "api_base_route": controller.get("base_route", "/"),
                "dependencies": controller.get("dependencies", []),
                "swagger": controller.get("swagger", []),
                "auth_guards": controller.get("auth_guards", []),
            })

            # Extract routes as API endpoints
            for route in controller.get("routes", []):
                endpoint_id = f"{controller['id']}::{route['handler']}"
                entities["api_endpoints"].append({
                    "id": endpoint_id,
                    "name": route["path"],
                    "type": "api_endpoint",
                    "layer": "backend",
                    "controller": controller["id"],
                    "http_method": route["method"],
                    "path": route["path"],
                    "handler": route["handler"],
                    "service_calls": route.get("service_calls", []),
                    "dtos": route.get("dtos", []),
                    "line_number": route.get("line_number", 0),
                    "file_path": controller["file_path"],
                })

        # Convert services → classes + methods
        for service in nestjs_data.get("services", []):
            entities["classes"].append({
                "id": service["id"],
                "name": service["name"],
                "type": "service",
                "layer": "backend",
                "file_path": service["file_path"],
                "line_start": service.get("line_start", 0),
                "dependencies": service.get("dependencies", []),
                "mongo_usage": service.get("mongo_usage", {}),
                "redis_usage": service.get("redis_usage", {}),
                "bull_usage": service.get("bull_usage", {}),
                "http_usage": service.get("http_usage", {}),
                "integrations": service.get("integrations", {}),
            })

            # Extract methods
            for method in service.get("methods", []):
                entities["methods"].append({
                    "id": f"{service['id']}::{method['name']}",
                    "name": method["name"],
                    "parent": service["id"],
                    "type": "method",
                    "layer": "backend",
                    "file_path": service["file_path"],
                    "line_start": method.get("line_number", 0),
                })

        # Convert DTOs
        for dto in nestjs_data.get("dtos", []):
            entities["dtos"].append({
                "id": dto["id"],
                "name": dto["name"],
                "type": "dto",
                "layer": "backend",
                "file_path": dto["file_path"],
                "line_start": dto.get("line_start", 0),
                "properties": dto.get("properties", []),
            })

        # Convert entities (TypeORM, Prisma)
        for entity in nestjs_data.get("entities", []):
            entities["entities"].append({
                "id": entity["id"],
                "name": entity["name"],
                "type": entity.get("type", "entity"),
                "layer": "data",
                "file_path": entity["file_path"],
                "line_start": entity.get("line_start", 0),
                "table_name": entity.get("table_name"),
                "columns": entity.get("columns", []),
                "types": entity.get("types", []),
                "enums_used": entity.get("enums_used", []),
            })

        # Convert repositories
        for repo in nestjs_data.get("repositories", []):
            entities["repositories"].append({
                "id": repo["id"],
                "name": repo["name"],
                "type": "repository",
                "layer": "data",
                "file_path": repo["file_path"],
                "line_start": repo.get("line_start", 0),
                "entity": repo.get("entity"),
                "methods": repo.get("methods", []),
            })

            # Extract repository methods
            for method in repo.get("methods", []):
                entities["methods"].append({
                    "id": f"{repo['id']}::{method['name']}",
                    "name": method["name"],
                    "parent": repo["id"],
                    "type": "method",
                    "layer": "data",
                    "file_path": repo["file_path"],
                    "line_start": method.get("line_number", 0),
                })

        # Convert GraphQL resolvers
        for resolver in nestjs_data.get("graphql_resolvers", []):
            entities["graphql_resolvers"].append({
                "id": resolver["id"],
                "name": resolver["name"],
                "type": "graphql_resolver",
                "layer": "backend",
                "file_path": resolver["file_path"],
                "line_start": resolver.get("line_start", 0),
                "resolver_type": resolver.get("resolver_type"),
                "queries": resolver.get("queries", []),
                "mutations": resolver.get("mutations", []),
                "subscriptions": resolver.get("subscriptions", []),
            })

        # Convert socket gateways
        for gateway in nestjs_data.get("socket_gateways", []):
            entities["socket_gateways"].append({
                "id": gateway["id"],
                "name": gateway["name"],
                "type": "socket_gateway",
                "layer": "backend",
                "file_path": gateway["file_path"],
                "line_start": gateway.get("line_start", 0),
                "namespace": gateway.get("namespace"),
                "message_handlers": gateway.get("message_handlers", []),
            })

        # Convert Bull processors
        for processor in nestjs_data.get("bull_processors", []):
            entities["bull_processors"].append({
                "id": processor["id"],
                "name": processor["name"],
                "type": "bull_processor",
                "layer": "backend",
                "file_path": processor["file_path"],
                "line_start": processor.get("line_start", 0),
                "queue_name": processor.get("queue_name"),
                "processes": processor.get("processes", []),
            })

        # Convert guards, interceptors, middleware
        for guard in nestjs_data.get("guards", []):
            entities["guards"].append(guard)

        for interceptor in nestjs_data.get("interceptors", []):
            entities["interceptors"].append(interceptor)

        for middleware_item in nestjs_data.get("middleware", []):
            entities["middleware"].append(middleware_item)

        # Convert modules
        for module in nestjs_data.get("modules", []):
            entities["modules"].append({
                "id": module["id"],
                "name": module["name"],
                "type": "module",
                "layer": "backend",
                "file_path": module["file_path"],
                "line_start": module.get("line_start", 0),
                "controllers": module.get("controllers", []),
                "providers": module.get("providers", []),
                "imports": module.get("imports", []),
                "exports": module.get("exports", []),
            })

        return {"entities": entities}

    def adapt_angular(self, angular_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert Angular parser output to ontology format.

        Angular parser typically outputs:
            - components
            - services
            - modules
            - directives
            - pipes
        """
        entities = {
            "classes": [],
            "functions": [],
            "methods": [],
            "components": [],
            "services": [],
            "modules": [],
            "http_calls": [],
        }

        # Convert components
        for component in angular_data.get("components", []):
            entities["components"].append({
                "id": component.get("id") or component.get("name"),
                "name": component.get("name"),
                "type": "component",
                "layer": "frontend",
                "file_path": component.get("file_path"),
                "selector": component.get("selector"),
                "template": component.get("template"),
                "styles": component.get("styles"),
            })

        # Convert services
        for service in angular_data.get("services", []):
            entities["services"].append({
                "id": service.get("id") or service.get("name"),
                "name": service.get("name"),
                "type": "service",
                "layer": "frontend",
                "file_path": service.get("file_path"),
                "methods": service.get("methods", []),
            })

        return {"entities": entities}

    def adapt_react(self, react_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert React parser output to ontology format.

        React parser typically outputs:
            - components
            - hooks
            - contexts
        """
        entities = {
            "classes": [],
            "functions": [],
            "components": [],
            "hooks": [],
            "contexts": [],
            "http_calls": [],
        }

        # Convert components
        for component in react_data.get("components", []):
            entities["components"].append({
                "id": component.get("id") or component.get("name"),
                "name": component.get("name"),
                "type": "component",
                "layer": "frontend",
                "file_path": component.get("file_path"),
                "props": component.get("props", []),
                "hooks_used": component.get("hooks_used", []),
            })

        # Convert hooks
        for hook in react_data.get("hooks", []):
            entities["hooks"].append({
                "id": hook.get("id") or hook.get("name"),
                "name": hook.get("name"),
                "type": "hook",
                "layer": "frontend",
                "file_path": hook.get("file_path"),
            })

        return {"entities": entities}

    def merge_parsed_data(
        self,
        *parsed_datasets: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Merge multiple parsed datasets into a single unified structure.

        Useful when parsing a multi-stack repository with both frontend and backend.

        Args:
            *parsed_datasets: Variable number of adapted parser outputs

        Returns:
            Merged ontology data
        """
        merged = {
            "entities": {
                "classes": [],
                "functions": [],
                "methods": [],
                "api_endpoints": [],
                "dtos": [],
                "repositories": [],
                "entities": [],
                "components": [],
                "services": [],
                "modules": [],
                "graphql_resolvers": [],
                "socket_gateways": [],
                "bull_processors": [],
                "guards": [],
                "interceptors": [],
                "middleware": [],
                "hooks": [],
                "contexts": [],
                "http_calls": [],
            }
        }

        # Merge all datasets
        for dataset in parsed_datasets:
            entities = dataset.get("entities", {})

            for entity_type, entity_list in entities.items():
                if entity_type in merged["entities"]:
                    merged["entities"][entity_type].extend(entity_list)

        return merged
