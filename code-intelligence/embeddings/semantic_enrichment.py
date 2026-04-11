"""
Semantic Enrichment using LLM
Adds intelligent tags, descriptions, and domain classification to code components.
"""

import os
from typing import Dict, List, Any, Optional
import json
from pathlib import Path


class SemanticEnricher:
    """
    Enriches code components with semantic information using LLM.

    Features:
    - Auto-generate descriptions
    - Domain classification (Auth, Payment, Notification, etc.)
    - Risk assessment (High/Medium/Low)
    - Tag generation
    """

    def __init__(self, api_key: Optional[str] = None):
        """Initialize the semantic enricher."""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.use_llm = self.api_key is not None

        if not self.use_llm:
            print("⚠️  No OpenAI API key found. Using rule-based enrichment.")

    def enrich_components(
        self, components: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Enrich all components with semantic information.

        Args:
            components: List of components from index

        Returns:
            Enriched components
        """
        print(f"🧠 Enriching {len(components)} components...")

        enriched = []

        for component in components:
            enriched_comp = self._enrich_component(component)
            enriched.append(enriched_comp)

        print(f"✅ Enriched {len(enriched)} components")

        return enriched

    def _enrich_component(self, component: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich a single component."""
        # Add semantic metadata
        component["semantic"] = {
            "domain": self._classify_domain(component),
            "risk_level": self._assess_risk(component),
            "tags": self._generate_tags(component),
            "auto_description": self._generate_description(component),
        }

        return component

    def _classify_domain(self, component: Dict[str, Any]) -> str:
        """
        Classify component into a domain category.

        Domains:
        - Authentication
        - Authorization
        - User Management
        - Payment
        - Notification
        - Data Storage
        - API
        - UI
        - Infrastructure
        - Testing
        - Unknown
        """
        name = (component.get("name") or "").lower()
        file_path = (component.get("file_path") or "").lower()
        description = (component.get("description") or "").lower()

        text = f"{name} {file_path} {description}"

        # Rule-based classification
        if any(
            keyword in text
            for keyword in ["auth", "login", "signin", "signup", "register", "token", "jwt"]
        ):
            return "Authentication"

        if any(keyword in text for keyword in ["permission", "role", "access", "guard"]):
            return "Authorization"

        if any(keyword in text for keyword in ["user", "profile", "account"]):
            return "User Management"

        if any(keyword in text for keyword in ["payment", "billing", "invoice", "checkout"]):
            return "Payment"

        if any(keyword in text for keyword in ["notification", "email", "sms", "push"]):
            return "Notification"

        if any(
            keyword in text
            for keyword in ["database", "repository", "entity", "model", "storage"]
        ):
            return "Data Storage"

        if any(keyword in text for keyword in ["api", "endpoint", "controller", "route"]):
            return "API"

        if any(
            keyword in text
            for keyword in ["screen", "page", "component", "widget", "ui", "view"]
        ):
            return "UI"

        if any(
            keyword in text
            for keyword in ["terraform", "kubernetes", "deployment", "infra", "config"]
        ):
            return "Infrastructure"

        if any(keyword in text for keyword in ["test", "spec", "mock"]):
            return "Testing"

        return "Unknown"

    def _assess_risk(self, component: Dict[str, Any]) -> str:
        """
        Assess the risk level of changing this component.

        Risk levels:
        - High: Critical components (auth, payment, core services)
        - Medium: Important but not critical
        - Low: UI components, utilities
        """
        domain = self._classify_domain(component)
        comp_type = component.get("type", "")

        # High risk domains
        if domain in ["Authentication", "Authorization", "Payment", "Data Storage"]:
            return "High"

        # High risk types
        if comp_type in ["service", "repository", "entity"]:
            return "High"

        # Medium risk
        if comp_type in ["controller", "api_client"]:
            return "Medium"

        # Infrastructure changes are high risk
        if component.get("layer") == "infrastructure":
            return "High"

        # UI components are generally lower risk
        if comp_type in ["screen", "page", "component", "widget"]:
            return "Low"

        return "Medium"

    def _generate_tags(self, component: Dict[str, Any]) -> List[str]:
        """Generate tags for the component."""
        tags = []

        # Layer tag
        layer = component.get("layer", "")
        if layer:
            tags.append(layer)

        # Type tag
        comp_type = component.get("type", "")
        if comp_type:
            tags.append(comp_type)

        # Domain tag
        domain = self._classify_domain(component)
        if domain != "Unknown":
            tags.append(domain.lower().replace(" ", "-"))

        # Technology tags
        file_path = component.get("file_path", "")

        if ".dart" in file_path:
            tags.append("dart")
            tags.append("flutter")
        elif ".tsx" in file_path or ".ts" in file_path:
            if "/react" in file_path or "Page" in component.get("name", ""):
                tags.append("react")
                tags.append("typescript")
            else:
                tags.append("nestjs")
                tags.append("typescript")
        elif ".tf" in file_path:
            tags.append("terraform")
            tags.append("hcl")
        elif ".yaml" in file_path or ".yml" in file_path:
            tags.append("kubernetes")
            tags.append("yaml")

        # API tags
        metadata = component.get("metadata", {})
        if metadata.get("api_calls"):
            tags.append("api-consumer")
        if metadata.get("routes"):
            tags.append("api-provider")

        return list(set(tags))

    def _generate_description(self, component: Dict[str, Any]) -> str:
        """Generate a description for the component."""
        # If already has description, return it
        existing = component.get("description")
        if existing and isinstance(existing, str):
            return existing

        # Generate based on component info
        name = component.get("name") or ""
        comp_type = component.get("type") or ""
        domain = self._classify_domain(component)

        # Basic description
        descriptions = {
            "controller": f"REST API controller handling {domain.lower()} endpoints",
            "service": f"Service providing {domain.lower()} business logic",
            "repository": f"Data access layer for {domain.lower()}",
            "entity": f"Database entity representing {domain.lower()} data",
            "dto": f"Data transfer object for {domain.lower()} operations",
            "screen": f"Mobile screen for {domain.lower()}",
            "page": f"Web page for {domain.lower()}",
            "component": f"UI component for {domain.lower()}",
            "hook": f"React hook for {domain.lower()} state management",
            "widget": f"Flutter widget for {domain.lower()}",
        }

        return descriptions.get(comp_type, f"{name} - {comp_type} in {domain}")


def main():
    """CLI for semantic enrichment."""
    import argparse

    parser = argparse.ArgumentParser(description="Semantic Enrichment")
    parser.add_argument("--index", required=True, help="Path to index JSON file")
    parser.add_argument("--output", required=True, help="Output path for enriched index")

    args = parser.parse_args()

    # Load index
    with open(args.index, "r") as f:
        index_data = json.load(f)

    # Enrich
    enricher = SemanticEnricher()
    enriched_components = enricher.enrich_components(index_data.get("components", []))

    # Update index
    index_data["components"] = enriched_components

    # Save
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        json.dump(index_data, f, indent=2, ensure_ascii=False)

    print(f"💾 Enriched index saved to: {output_path}")


if __name__ == "__main__":
    main()
