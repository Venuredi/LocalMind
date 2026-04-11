"""
Terraform Parser
Extracts resources, variables, outputs, and dependencies from Terraform HCL files.
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Any
import hcl2
import json


class TerraformParser:
    """Parse Terraform HCL files and extract infrastructure intelligence."""

    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.resources: List[Dict[str, Any]] = []
        self.variables: List[Dict[str, Any]] = []
        self.outputs: List[Dict[str, Any]] = []
        self.data_sources: List[Dict[str, Any]] = []

    def parse(self) -> Dict[str, Any]:
        """Parse all Terraform files in the repository."""
        tf_files = list(self.repo_path.rglob("*.tf"))

        for file_path in tf_files:
            self._parse_file(file_path)

        return {
            "resources": self.resources,
            "variables": self.variables,
            "outputs": self.outputs,
            "data_sources": self.data_sources,
        }

    def _parse_file(self, file_path: Path):
        """Parse a single Terraform file."""
        try:
            content = file_path.read_text(encoding="utf-8")
            relative_path = file_path.relative_to(self.repo_path)

            # Try to parse with hcl2
            try:
                with open(file_path, "r") as f:
                    parsed = hcl2.load(f)

                self._extract_from_hcl(parsed, str(relative_path), content)

            except Exception as hcl_error:
                # Fallback to regex parsing
                print(f"HCL parsing failed for {file_path}, using regex: {hcl_error}")
                self._parse_with_regex(content, str(relative_path))

        except Exception as e:
            print(f"Error parsing {file_path}: {e}")

    def _extract_from_hcl(
        self, parsed: Dict, relative_path: str, content: str
    ):
        """Extract resources from parsed HCL."""
        # Extract resources
        if "resource" in parsed:
            for resource_block in parsed["resource"]:
                for resource_type, resources in resource_block.items():
                    for resource_name, resource_config in resources.items():
                        self._add_resource(
                            resource_type,
                            resource_name,
                            resource_config,
                            relative_path,
                            content,
                        )

        # Extract variables
        if "variable" in parsed:
            for variable_block in parsed["variable"]:
                for var_name, var_config in variable_block.items():
                    self._add_variable(var_name, var_config, relative_path, content)

        # Extract outputs
        if "output" in parsed:
            for output_block in parsed["output"]:
                for output_name, output_config in output_block.items():
                    self._add_output(
                        output_name, output_config, relative_path, content
                    )

        # Extract data sources
        if "data" in parsed:
            for data_block in parsed["data"]:
                for data_type, data_sources in data_block.items():
                    for data_name, data_config in data_sources.items():
                        self._add_data_source(
                            data_type, data_name, data_config, relative_path, content
                        )

    def _add_resource(
        self,
        resource_type: str,
        resource_name: str,
        config: Dict,
        relative_path: str,
        content: str,
    ):
        """Add a resource to the list."""
        # Extract dependencies
        depends_on_list = []
        raw_depends_on = config.get("depends_on", [])
        if isinstance(raw_depends_on, list):
            for d in raw_depends_on:
                if isinstance(d, list):
                    depends_on_list.extend([str(x) for x in d])
                elif isinstance(d, str):
                    depends_on_list.append(d)
        elif isinstance(raw_depends_on, str):
            depends_on_list.append(raw_depends_on)

        try:
            config_str = json.dumps(config, default=str)
            implicit_pattern = re.compile(r'\b([a-z0-9_]+\.[a-zA-Z0-9_-]+)\.[a-zA-Z0-9_.-]+\b')
            for m in implicit_pattern.findall(config_str):
                if not m.startswith(("var.", "local.")):
                    if m not in depends_on_list:
                        depends_on_list.append(m)
        except Exception:
            pass

        # Extract environment variables and secrets
        env_vars = self._extract_env_vars(config)
        secrets = self._extract_secrets(config)

        # Get line number
        line_number = self._find_resource_line(
            content, resource_type, resource_name
        )

        # Extract tags
        tags = config.get("tags", {})

        resource = {
            "id": f"{resource_type}.{resource_name}",
            "name": resource_name,
            "type": "terraform_resource",
            "resource_type": resource_type,
            "layer": "infrastructure",
            "file_path": relative_path,
            "config": config,
            "depends_on": depends_on_list,
            "env_vars": env_vars,
            "secrets": secrets,
            "tags": tags,
            "line_start": line_number,
        }

        self.resources.append(resource)

    def _add_variable(
        self, var_name: str, config: Dict, relative_path: str, content: str
    ):
        """Add a variable to the list."""
        var_type = config.get("type", "string")
        default = config.get("default")
        description = config.get("description", "")

        line_number = self._find_variable_line(content, var_name)

        variable = {
            "id": f"var.{var_name}",
            "name": var_name,
            "type": "terraform_variable",
            "var_type": var_type,
            "layer": "infrastructure",
            "file_path": relative_path,
            "default": default,
            "description": description,
            "line_start": line_number,
        }

        self.variables.append(variable)

    def _add_output(
        self, output_name: str, config: Dict, relative_path: str, content: str
    ):
        """Add an output to the list."""
        value = config.get("value")
        description = config.get("description", "")

        line_number = self._find_output_line(content, output_name)

        output = {
            "id": f"output.{output_name}",
            "name": output_name,
            "type": "terraform_output",
            "layer": "infrastructure",
            "file_path": relative_path,
            "value": str(value),
            "description": description,
            "line_start": line_number,
        }

        self.outputs.append(output)

    def _add_data_source(
        self,
        data_type: str,
        data_name: str,
        config: Dict,
        relative_path: str,
        content: str,
    ):
        """Add a data source to the list."""
        line_number = self._find_data_source_line(content, data_type, data_name)

        data_source = {
            "id": f"data.{data_type}.{data_name}",
            "name": data_name,
            "type": "terraform_data",
            "data_type": data_type,
            "layer": "infrastructure",
            "file_path": relative_path,
            "config": config,
            "line_start": line_number,
        }

        self.data_sources.append(data_source)

    def _extract_env_vars(self, config: Dict) -> List[Dict[str, Any]]:
        """Extract environment variables from resource config."""
        env_vars = []

        # Check common locations for env vars
        if isinstance(config, dict):
            # Check container_definitions (ECS)
            if "container_definitions" in config:
                container_defs = config["container_definitions"]
                if isinstance(container_defs, str):
                    try:
                        container_json = json.loads(container_defs)
                        if isinstance(container_json, list):
                            for container in container_json:
                                if "environment" in container:
                                    for env in container["environment"]:
                                        env_vars.append(
                                            {
                                                "name": env.get("name"),
                                                "value": env.get("value"),
                                            }
                                        )
                    except:
                        pass

            # Check environment blocks
            if "environment" in config:
                for env in config["environment"]:
                    env_vars.append(
                        {"name": env.get("name"), "value": env.get("value")}
                    )

            # Recursively search for env vars
            for key, value in config.items():
                if key.upper() == key and isinstance(value, str):
                    # Likely an environment variable
                    env_vars.append({"name": key, "value": value})

        return env_vars

    def _extract_secrets(self, config: Dict) -> List[Dict[str, Any]]:
        """Extract secrets references from resource config."""
        secrets = []

        if isinstance(config, dict):
            # Check secrets block (ECS)
            if "secrets" in config:
                for secret in config["secrets"]:
                    secrets.append(
                        {
                            "name": secret.get("name"),
                            "valueFrom": secret.get("valueFrom"),
                        }
                    )

            # Check for secretsmanager references
            for key, value in config.items():
                if isinstance(value, str) and "secretsmanager" in value:
                    secrets.append({"name": key, "reference": value})

        return secrets

    def _parse_with_regex(self, content: str, relative_path: str):
        """Fallback regex-based parsing."""
        # Extract resources
        resource_pattern = r'resource\s+"([^"]+)"\s+"([^"]+)"\s*{'
        matches = re.finditer(resource_pattern, content)

        for match in matches:
            resource_type = match.group(1)
            resource_name = match.group(2)
            line_number = content[: match.start()].count("\n") + 1

            # Extract block content
            block_content = self._extract_block(content, match.end())

            resource = {
                "id": f"{resource_type}.{resource_name}",
                "name": resource_name,
                "type": "terraform_resource",
                "resource_type": resource_type,
                "layer": "infrastructure",
                "file_path": relative_path,
                "line_start": line_number,
            }

            self.resources.append(resource)

    def _extract_block(self, content: str, start_pos: int) -> str:
        """Extract a Terraform block."""
        brace_count = 1
        i = start_pos

        while i < len(content) and brace_count > 0:
            if content[i] == "{":
                brace_count += 1
            elif content[i] == "}":
                brace_count -= 1
            i += 1

        return content[start_pos : i - 1]

    def _find_resource_line(
        self, content: str, resource_type: str, resource_name: str
    ) -> int:
        """Find line number of a resource."""
        pattern = rf'resource\s+"{resource_type}"\s+"{resource_name}"'
        match = re.search(pattern, content)
        if match:
            return content[: match.start()].count("\n") + 1
        return 0

    def _find_variable_line(self, content: str, var_name: str) -> int:
        """Find line number of a variable."""
        pattern = rf'variable\s+"{var_name}"'
        match = re.search(pattern, content)
        if match:
            return content[: match.start()].count("\n") + 1
        return 0

    def _find_output_line(self, content: str, output_name: str) -> int:
        """Find line number of an output."""
        pattern = rf'output\s+"{output_name}"'
        match = re.search(pattern, content)
        if match:
            return content[: match.start()].count("\n") + 1
        return 0

    def _find_data_source_line(
        self, content: str, data_type: str, data_name: str
    ) -> int:
        """Find line number of a data source."""
        pattern = rf'data\s+"{data_type}"\s+"{data_name}"'
        match = re.search(pattern, content)
        if match:
            return content[: match.start()].count("\n") + 1
        return 0
