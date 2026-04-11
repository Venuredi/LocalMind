"""
ArgoCD/Kubernetes YAML Parser
Extracts deployments, services, configmaps, secrets, and ingress from Kubernetes YAML files.
"""

import yaml
from yaml import SafeLoader
from pathlib import Path
from typing import Dict, List, Optional, Any, Set


# ---------------------------------------------------------------------------
# Custom YAML loader that tolerates CloudFormation / non-standard tags
# (e.g. !Sub, !Ref, !If, !Join …) instead of raising ConstructorError.
# ---------------------------------------------------------------------------
class _PermissiveSafeLoader(SafeLoader):
    """SafeLoader extended to silently accept any unknown YAML tag."""


def _ignore_unknown_tag(loader, tag_suffix, node):
    """Return the plain Python object for any unknown tag."""
    if isinstance(node, yaml.ScalarNode):
        return loader.construct_scalar(node)
    elif isinstance(node, yaml.SequenceNode):
        return loader.construct_sequence(node)
    else:
        return loader.construct_mapping(node)


# Register the catch-all constructor for any tag prefix
_PermissiveSafeLoader.add_multi_constructor("", _ignore_unknown_tag)


# Directories to exclude from parsing
EXCLUDED_DIRS: Set[str] = {
    "node_modules",
    ".git",
    "vendor",
    "dist",
    "build",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".tox",
    ".egg-info",
    ".idea",
    ".vscode",
    "coverage",
    "htmlcov",
    ".coverage",
    "target",  # Rust/Maven build
    "bin",
    "obj",
}


def _is_excluded_path(file_path: Path) -> bool:
    """Check if file path contains any excluded directory."""
    return any(part in EXCLUDED_DIRS for part in file_path.parts)


class ArgoCDParser:
    """Parse Kubernetes/ArgoCD YAML files and extract deployment intelligence."""

    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.applications: List[Dict[str, Any]] = []
        self.deployments: List[Dict[str, Any]] = []
        self.services: List[Dict[str, Any]] = []
        self.configmaps: List[Dict[str, Any]] = []
        self.secrets: List[Dict[str, Any]] = []
        self.ingresses: List[Dict[str, Any]] = []

    def parse(self) -> Dict[str, Any]:
        """Parse all YAML files in the repository."""
        yaml_files = list(self.repo_path.rglob("*.yaml")) + list(
            self.repo_path.rglob("*.yml")
        )

        for file_path in yaml_files:
            # Skip files in excluded directories
            if _is_excluded_path(file_path):
                continue
            self._parse_file(file_path)

        return {
            "applications": self.applications,
            "deployments": self.deployments,
            "services": self.services,
            "configmaps": self.configmaps,
            "secrets": self.secrets,
            "ingresses": self.ingresses,
        }

    def _parse_file(self, file_path: Path):
        """Parse a single YAML file."""
        try:
            # Skip anything inside node_modules — those are dependency files,
            # not project manifests, so they'll never be valid K8s resources.
            if "node_modules" in file_path.parts:
                return

            content = file_path.read_text(encoding="utf-8")
            relative_path = file_path.relative_to(self.repo_path)

            # Parse YAML using the permissive loader so that CloudFormation
            # intrinsic tags (!Sub, !Ref, !If, !Join …) don't crash the parser.
            documents = list(yaml.load_all(content, Loader=_PermissiveSafeLoader))

            for doc in documents:
                if not doc or not isinstance(doc, dict):
                    continue

                kind = doc.get("kind", "")
                api_version = doc.get("apiVersion", "")

                # Route to appropriate parser based on kind
                if kind == "Application" and "argoproj.io" in api_version:
                    self._parse_argocd_application(doc, str(relative_path))
                elif kind == "Deployment":
                    self._parse_deployment(doc, str(relative_path))
                elif kind == "Service":
                    self._parse_service(doc, str(relative_path))
                elif kind == "ConfigMap":
                    self._parse_configmap(doc, str(relative_path))
                elif kind == "Secret":
                    self._parse_secret(doc, str(relative_path))
                elif kind == "Ingress":
                    self._parse_ingress(doc, str(relative_path))

        except Exception as e:
            print(f"Error parsing {file_path}: {e}")

    def _parse_argocd_application(self, doc: Dict, relative_path: str):
        """Parse an ArgoCD Application."""
        metadata = doc.get("metadata", {})
        spec = doc.get("spec", {})

        name = metadata.get("name", "unknown")
        namespace = metadata.get("namespace", "default")

        source = spec.get("source", {})
        destination = spec.get("destination", {})
        sync_policy = spec.get("syncPolicy", {})

        application = {
            "id": f"argocd.{name}",
            "name": name,
            "type": "argocd_application",
            "layer": "deployment",
            "file_path": relative_path,
            "namespace": namespace,
            "source_repo": source.get("repoURL"),
            "source_path": source.get("path"),
            "target_revision": source.get("targetRevision"),
            "destination_server": destination.get("server"),
            "destination_namespace": destination.get("namespace"),
            "sync_policy": sync_policy,
        }

        self.applications.append(application)

    def _parse_deployment(self, doc: Dict, relative_path: str):
        """Parse a Kubernetes Deployment."""
        metadata = doc.get("metadata", {})
        spec = doc.get("spec", {})

        name = metadata.get("name", "unknown")
        namespace = metadata.get("namespace", "default")
        labels = metadata.get("labels", {})

        template = spec.get("template", {})
        template_spec = template.get("spec", {})
        containers = template_spec.get("containers", [])

        # Extract container info
        container_info = []
        env_vars = []
        secrets_used = []

        for container in containers:
            container_name = container.get("name")
            image = container.get("image")
            ports = container.get("ports", [])

            # Extract environment variables
            env = container.get("env", [])
            for env_var in env:
                var_name = env_var.get("name")

                # Check if from configmap or secret
                value_from = env_var.get("valueFrom")
                if value_from:
                    if "configMapKeyRef" in value_from:
                        env_vars.append(
                            {
                                "name": var_name,
                                "source": "configmap",
                                "configmap": value_from["configMapKeyRef"].get(
                                    "name"
                                ),
                                "key": value_from["configMapKeyRef"].get("key"),
                            }
                        )
                    elif "secretKeyRef" in value_from:
                        secret_name = value_from["secretKeyRef"].get("name")
                        secrets_used.append(secret_name)
                        env_vars.append(
                            {
                                "name": var_name,
                                "source": "secret",
                                "secret": secret_name,
                                "key": value_from["secretKeyRef"].get("key"),
                            }
                        )
                else:
                    env_vars.append(
                        {
                            "name": var_name,
                            "value": env_var.get("value"),
                            "source": "direct",
                        }
                    )

            container_info.append(
                {
                    "name": container_name,
                    "image": image,
                    "ports": [p.get("containerPort") for p in ports],
                }
            )

        deployment = {
            "id": f"deployment.{name}",
            "name": name,
            "type": "k8s_deployment",
            "layer": "deployment",
            "file_path": relative_path,
            "namespace": namespace,
            "labels": labels,
            "replicas": spec.get("replicas", 1),
            "containers": container_info,
            "env_vars": env_vars,
            "secrets": list(set(secrets_used)),
        }

        self.deployments.append(deployment)

    def _parse_service(self, doc: Dict, relative_path: str):
        """Parse a Kubernetes Service."""
        metadata = doc.get("metadata", {})
        spec = doc.get("spec", {})

        name = metadata.get("name", "unknown")
        namespace = metadata.get("namespace", "default")
        labels = metadata.get("labels", {})

        service_type = spec.get("type", "ClusterIP")
        ports = spec.get("ports", [])
        selector = spec.get("selector", {})

        port_info = []
        for port in ports:
            port_info.append(
                {
                    "name": port.get("name"),
                    "port": port.get("port"),
                    "targetPort": port.get("targetPort"),
                    "protocol": port.get("protocol", "TCP"),
                }
            )

        service = {
            "id": f"service.{name}",
            "name": name,
            "type": "k8s_service",
            "layer": "deployment",
            "file_path": relative_path,
            "namespace": namespace,
            "labels": labels,
            "service_type": service_type,
            "ports": port_info,
            "selector": selector,
        }

        self.services.append(service)

    def _parse_configmap(self, doc: Dict, relative_path: str):
        """Parse a Kubernetes ConfigMap."""
        metadata = doc.get("metadata", {})
        data = doc.get("data", {})

        name = metadata.get("name", "unknown")
        namespace = metadata.get("namespace", "default")

        # Extract key-value pairs
        config_data = []
        for key, value in data.items():
            config_data.append({"key": key, "value": value})

        configmap = {
            "id": f"configmap.{name}",
            "name": name,
            "type": "k8s_configmap",
            "layer": "deployment",
            "file_path": relative_path,
            "namespace": namespace,
            "data": config_data,
        }

        self.configmaps.append(configmap)

    def _parse_secret(self, doc: Dict, relative_path: str):
        """Parse a Kubernetes Secret."""
        metadata = doc.get("metadata", {})
        data = doc.get("data", {})

        name = metadata.get("name", "unknown")
        namespace = metadata.get("namespace", "default")
        secret_type = doc.get("type", "Opaque")

        # Extract keys (not values for security)
        secret_keys = list(data.keys())

        secret = {
            "id": f"secret.{name}",
            "name": name,
            "type": "k8s_secret",
            "layer": "deployment",
            "file_path": relative_path,
            "namespace": namespace,
            "secret_type": secret_type,
            "keys": secret_keys,
        }

        self.secrets.append(secret)

    def _parse_ingress(self, doc: Dict, relative_path: str):
        """Parse a Kubernetes Ingress."""
        metadata = doc.get("metadata", {})
        spec = doc.get("spec", {})

        name = metadata.get("name", "unknown")
        namespace = metadata.get("namespace", "default")
        annotations = metadata.get("annotations", {})

        # Extract rules
        rules = spec.get("rules", [])
        ingress_rules = []

        for rule in rules:
            host = rule.get("host")
            http = rule.get("http", {})
            paths = http.get("paths", [])

            for path in paths:
                path_value = path.get("path", "/")
                backend = path.get("backend", {})
                service = backend.get("service", {})

                ingress_rules.append(
                    {
                        "host": host,
                        "path": path_value,
                        "service_name": service.get("name"),
                        "service_port": service.get("port", {}).get("number"),
                    }
                )

        # Extract TLS
        tls = spec.get("tls", [])
        tls_hosts = []
        for tls_config in tls:
            tls_hosts.extend(tls_config.get("hosts", []))

        ingress = {
            "id": f"ingress.{name}",
            "name": name,
            "type": "k8s_ingress",
            "layer": "deployment",
            "file_path": relative_path,
            "namespace": namespace,
            "annotations": annotations,
            "rules": ingress_rules,
            "tls_hosts": tls_hosts,
        }

        self.ingresses.append(ingress)
