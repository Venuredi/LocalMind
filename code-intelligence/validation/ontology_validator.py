"""
Ontology Validator
Validates ontology completeness and ensures proper coverage of all layers.

This validator enforces the "golden rule":
"If you cannot trace a request from UI → DB, your ontology is incomplete"
"""

import networkx as nx
from typing import Dict, List, Any, Set, Optional, Tuple


class OntologyValidator:
    """
    Validates ontology completeness and coverage.

    Checks:
    - UI coverage (components present)
    - API coverage (endpoints modeled)
    - Service coverage (business logic present)
    - Repository coverage (data access present)
    - DTO coverage (data contracts present)
    - Cross-layer traceability (end-to-end paths)
    """

    def __init__(self, ontology_graph: nx.MultiDiGraph):
        """
        Initialize validator.

        Args:
            ontology_graph: The ontology graph to validate
        """
        self.graph = ontology_graph
        self.validation_results = {}

    def validate_coverage(self) -> Dict[str, Any]:
        """
        Run all coverage checks.

        Returns:
            Dictionary with validation results for each layer/aspect
        """
        return {
            "ui_coverage": self._check_ui_coverage(),
            "api_coverage": self._check_api_coverage(),
            "service_coverage": self._check_service_coverage(),
            "repository_coverage": self._check_repository_coverage(),
            "dto_coverage": self._check_dto_coverage(),
            "entity_coverage": self._check_entity_coverage(),
            "cross_layer_paths": self._check_cross_layer_paths(),
            "relationship_coverage": self._check_relationship_coverage(),
        }

    def _check_ui_coverage(self) -> Dict[str, Any]:
        """Check if UI components are properly modeled."""
        ui_components = [
            n for n, d in self.graph.nodes(data=True)
            if d.get("type") in ["component", "widget", "screen", "page"]
            or d.get("layer") == "frontend"
        ]

        return {
            "total_components": len(ui_components),
            "has_components": len(ui_components) > 0,
            "status": "✅" if len(ui_components) > 0 else "⚠️",
            "message": f"Found {len(ui_components)} UI components" if ui_components
                      else "No UI components found (backend-only repo?)",
        }

    def _check_api_coverage(self) -> Dict[str, Any]:
        """Check if APIs are properly modeled."""
        api_endpoints = [
            n for n, d in self.graph.nodes(data=True)
            if d.get("type") == "api_endpoint"
        ]

        controllers = [
            n for n, d in self.graph.nodes(data=True)
            if d.get("type") == "controller"
        ]

        return {
            "total_endpoints": len(api_endpoints),
            "total_controllers": len(controllers),
            "has_endpoints": len(api_endpoints) > 0,
            "status": "✅" if len(api_endpoints) > 0 else "❌",
            "message": f"Found {len(api_endpoints)} API endpoints in {len(controllers)} controllers"
                      if api_endpoints else "❌ No API endpoints found - ontology incomplete!",
        }

    def _check_service_coverage(self) -> Dict[str, Any]:
        """Check if services are properly modeled."""
        services = [
            n for n, d in self.graph.nodes(data=True)
            if d.get("type") == "service" and d.get("layer") == "backend"
        ]

        return {
            "total_services": len(services),
            "has_services": len(services) > 0,
            "status": "✅" if len(services) > 0 else "❌",
            "message": f"Found {len(services)} backend services"
                      if services else "❌ No backend services found!",
        }

    def _check_repository_coverage(self) -> Dict[str, Any]:
        """Check if repositories are properly modeled."""
        repositories = [
            n for n, d in self.graph.nodes(data=True)
            if d.get("type") == "repository"
        ]

        return {
            "total_repositories": len(repositories),
            "has_repositories": len(repositories) > 0,
            "status": "✅" if len(repositories) > 0 else "⚠️",
            "message": f"Found {len(repositories)} repositories"
                      if repositories else "⚠️ No repositories found (may use services directly)",
        }

    def _check_dto_coverage(self) -> Dict[str, Any]:
        """Check if DTOs are properly modeled."""
        dtos = [
            n for n, d in self.graph.nodes(data=True)
            if d.get("type") == "dto"
        ]

        return {
            "total_dtos": len(dtos),
            "has_dtos": len(dtos) > 0,
            "status": "✅" if len(dtos) > 0 else "⚠️",
            "message": f"Found {len(dtos)} DTOs"
                      if dtos else "⚠️ No DTOs found",
        }

    def _check_entity_coverage(self) -> Dict[str, Any]:
        """Check if database entities are properly modeled."""
        entities = [
            n for n, d in self.graph.nodes(data=True)
            if d.get("type") in ["entity", "model", "prisma_model", "mongo_schema"]
            or d.get("layer") == "data"
        ]

        return {
            "total_entities": len(entities),
            "has_entities": len(entities) > 0,
            "status": "✅" if len(entities) > 0 else "⚠️",
            "message": f"Found {len(entities)} data entities"
                      if entities else "⚠️ No data entities found",
        }

    def _check_cross_layer_paths(self) -> Dict[str, Any]:
        """
        Verify end-to-end traceability.

        This is the CRITICAL check that enforces the golden rule:
        "Can we trace from API endpoints to the data layer?"
        """
        # Find all API endpoints
        endpoints = [
            n for n, d in self.graph.nodes(data=True)
            if d.get("type") == "api_endpoint"
        ]

        if not endpoints:
            return {
                "total_endpoints": 0,
                "traceable_endpoints": 0,
                "coverage_percent": 0,
                "status": "❌",
                "message": "❌ No API endpoints to trace - cannot verify cross-layer paths!",
                "untraceable_endpoints": [],
            }

        traceable = 0
        untraceable_endpoints = []

        for endpoint in endpoints:
            if self._can_trace_to_data_layer(endpoint):
                traceable += 1
            else:
                endpoint_data = self.graph.nodes[endpoint]
                untraceable_endpoints.append({
                    "id": endpoint,
                    "path": endpoint_data.get("path", "unknown"),
                    "method": endpoint_data.get("http_method", "unknown"),
                })

        coverage = (traceable / len(endpoints) * 100) if endpoints else 0

        status = "✅" if coverage >= 80 else ("⚠️" if coverage >= 50 else "❌")

        return {
            "total_endpoints": len(endpoints),
            "traceable_endpoints": traceable,
            "coverage_percent": round(coverage, 1),
            "status": status,
            "message": f"{status} {traceable}/{len(endpoints)} endpoints traceable to data layer ({coverage:.1f}%)",
            "untraceable_endpoints": untraceable_endpoints[:5],  # Show first 5
        }

    def _check_relationship_coverage(self) -> Dict[str, Any]:
        """Check if critical relationship types exist."""
        edge_types = {}
        for _, _, attrs in self.graph.edges(data=True):
            rel_type = attrs.get("relationship", "unknown")
            edge_types[rel_type] = edge_types.get(rel_type, 0) + 1

        critical_relationships = {
            "exposes_endpoint": "API endpoints linked to controllers",
            "calls_service": "Controllers calling services",
            "uses_repository": "Services using repositories",
            "uses_dto": "Endpoints using DTOs",
            "manages_entity": "Repositories managing entities",
        }

        present = {}
        missing = []

        for rel_type, description in critical_relationships.items():
            count = edge_types.get(rel_type, 0)
            present[rel_type] = count
            if count == 0:
                missing.append(f"{rel_type} ({description})")

        all_present = len(missing) == 0

        return {
            "total_relationship_types": len(edge_types),
            "critical_relationships": present,
            "missing_relationships": missing,
            "has_all_critical": all_present,
            "status": "✅" if all_present else "❌",
            "message": "✅ All critical relationships present" if all_present
                      else f"❌ Missing {len(missing)} critical relationship types",
        }

    def _can_trace_to_data_layer(self, start_node: str) -> bool:
        """
        Check if we can trace from start_node to data layer.

        Uses BFS to find any path to a repository or entity node.

        Args:
            start_node: Starting node ID

        Returns:
            True if path to data layer exists
        """
        if start_node not in self.graph:
            return False

        visited = set()
        queue = [start_node]

        while queue:
            current = queue.pop(0)

            if current in visited:
                continue

            visited.add(current)

            # Check if we reached data layer
            node_data = self.graph.nodes[current]
            node_type = node_data.get("type", "")
            node_layer = node_data.get("layer", "")

            # Success: reached data layer
            if (node_layer == "data" or
                node_type in ["repository", "entity", "model", "prisma_model", "mongo_schema"]):
                return True

            # Continue BFS through execution edges
            try:
                for successor in self.graph.successors(current):
                    if successor not in visited:
                        # Only follow execution-related edges
                        edge_data = self.graph.get_edge_data(current, successor)
                        for edge_attrs in edge_data.values():
                            edge_type = edge_attrs.get("type", "")
                            if edge_type in ["execution", "api", "data_access"]:
                                queue.append(successor)
                                break
            except Exception:
                # Handle any graph traversal errors
                continue

        return False

    def get_coverage_summary(self) -> Dict[str, Any]:
        """
        Get a summary of overall coverage.

        Returns:
            Summary with overall status and key metrics
        """
        results = self.validate_coverage()

        # Count passed checks
        total_checks = len(results)
        passed_checks = sum(
            1 for data in results.values()
            if data.get("status") == "✅"
        )

        # Calculate overall score
        score = (passed_checks / total_checks * 100) if total_checks > 0 else 0

        # Determine overall status
        if score >= 80:
            overall_status = "✅ COMPLETE"
            health = "EXCELLENT"
        elif score >= 60:
            overall_status = "⚠️ MOSTLY COMPLETE"
            health = "GOOD"
        elif score >= 40:
            overall_status = "⚠️ INCOMPLETE"
            health = "FAIR"
        else:
            overall_status = "❌ SEVERELY INCOMPLETE"
            health = "POOR"

        return {
            "overall_status": overall_status,
            "health": health,
            "score": round(score, 1),
            "passed_checks": passed_checks,
            "total_checks": total_checks,
            "critical_issues": self._get_critical_issues(results),
        }

    def _get_critical_issues(self, results: Dict[str, Any]) -> List[str]:
        """Extract critical issues from validation results."""
        issues = []

        # Check for critical failures
        if results["api_coverage"]["status"] == "❌":
            issues.append("No API endpoints found - backend parsing failed")

        if results["cross_layer_paths"]["coverage_percent"] < 50:
            issues.append(
                f"Only {results['cross_layer_paths']['coverage_percent']}% "
                f"of endpoints traceable to data layer"
            )

        if not results["relationship_coverage"]["has_all_critical"]:
            missing = results["relationship_coverage"]["missing_relationships"]
            issues.append(f"Missing critical relationships: {', '.join(missing[:3])}")

        return issues

    def print_report(self):
        """Print a detailed validation report."""
        results = self.validate_coverage()
        summary = self.get_coverage_summary()

        print("\n" + "=" * 70)
        print("📊 ONTOLOGY COMPLETENESS VALIDATION REPORT")
        print("=" * 70)

        # Overall summary
        print(f"\n{summary['overall_status']}")
        print(f"Health: {summary['health']}")
        print(f"Score: {summary['score']}% ({summary['passed_checks']}/{summary['total_checks']} checks passed)")

        # Layer coverage
        print("\n" + "-" * 70)
        print("📦 Layer Coverage:")
        print("-" * 70)

        for category, data in results.items():
            if category == "relationship_coverage":
                continue

            status = data.get("status", "❓")
            message = data.get("message", "")
            print(f"\n{category.upper().replace('_', ' ')}:")
            print(f"  {message}")

            # Show key metrics
            for key, value in data.items():
                if key not in ["status", "message", "untraceable_endpoints"]:
                    print(f"    {key}: {value}")

        # Relationship coverage
        print("\n" + "-" * 70)
        print("🔗 Relationship Coverage:")
        print("-" * 70)

        rel_data = results["relationship_coverage"]
        print(f"  {rel_data['message']}")

        if rel_data["critical_relationships"]:
            print("\n  Critical Relationships:")
            for rel_type, count in rel_data["critical_relationships"].items():
                status = "✅" if count > 0 else "❌"
                print(f"    {status} {rel_type}: {count}")

        # Critical issues
        if summary["critical_issues"]:
            print("\n" + "-" * 70)
            print("🔥 Critical Issues:")
            print("-" * 70)
            for i, issue in enumerate(summary["critical_issues"], 1):
                print(f"  {i}. {issue}")

        # Recommendations
        print("\n" + "-" * 70)
        print("💡 Recommendations:")
        print("-" * 70)

        if summary["score"] < 80:
            print("  1. Review ONTOLOGY_COMPLETENESS_FIX_PLAN.md")
            print("  2. Ensure parser adapter is being used")
            print("  3. Check that all edge builders are enabled")

        if results["cross_layer_paths"]["coverage_percent"] < 80:
            untraceable = results["cross_layer_paths"].get("untraceable_endpoints", [])
            if untraceable:
                print(f"\n  Untraceable endpoints (showing first {len(untraceable)}):")
                for ep in untraceable:
                    print(f"    - {ep['method']} {ep['path']}")

        print("\n" + "=" * 70 + "\n")

    def export_validation_report(self, output_path: str):
        """
        Export validation report to JSON file.

        Args:
            output_path: Path to save JSON report
        """
        import json
        from pathlib import Path

        results = self.validate_coverage()
        summary = self.get_coverage_summary()

        report = {
            "summary": summary,
            "detailed_results": results,
            "timestamp": self._get_timestamp(),
            "graph_stats": {
                "total_nodes": self.graph.number_of_nodes(),
                "total_edges": self.graph.number_of_edges(),
            },
        }

        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        print(f"📄 Validation report saved to: {output_file}")

    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()
