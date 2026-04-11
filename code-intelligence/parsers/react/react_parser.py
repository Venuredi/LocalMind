"""
React Parser
Extracts components, hooks, API calls, and dependencies from React TypeScript/JavaScript code.
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Any

# Directories that should never be indexed (dependencies, build output, etc.)
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
    """Return True if the file lives inside a dependency/build directory."""
    return any(part in _EXCLUDED_DIRS for part in file_path.parts)


class ReactParser:
    """Parse React/TypeScript files and extract code intelligence."""

    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.components: List[Dict[str, Any]] = []
        self.hooks: List[Dict[str, Any]] = []
        self.pages: List[Dict[str, Any]] = []
        self.services: List[Dict[str, Any]] = []

    def parse(self) -> Dict[str, Any]:
        """Parse the entire React codebase."""
        # Find all TypeScript/JavaScript files, excluding dependency directories
        tsx_files = [f for f in self.repo_path.rglob("*.tsx") if not _is_excluded(f)]
        ts_files  = [f for f in self.repo_path.rglob("*.ts")  if not _is_excluded(f)]

        all_files = tsx_files + ts_files

        for file_path in all_files:
            self._parse_file(file_path)

        return {
            "components": self.components,
            "hooks": self.hooks,
            "pages": self.pages,
            "services": self.services,
        }

    def _parse_file(self, file_path: Path):
        """Parse a single React/TypeScript file."""
        try:
            content = file_path.read_text(encoding="utf-8")
            relative_path = file_path.relative_to(self.repo_path)

            # Determine file type
            if "/pages/" in str(relative_path) or "Page.tsx" in file_path.name:
                self._parse_page(content, str(relative_path), file_path)
            elif "/hooks/" in str(relative_path) or file_path.name.startswith("use") or file_path.stem.startswith("use"):
                self._parse_hook(content, str(relative_path), file_path)
            elif "/services/" in str(relative_path) or "Client.ts" in file_path.name or file_path.name.endswith("api.ts") or file_path.name.endswith("-api.ts"):
                self._parse_service(content, str(relative_path), file_path)
            elif ".tsx" in file_path.name:
                self._parse_component(content, str(relative_path), file_path)
            elif ".ts" in file_path.name and ("hook" in file_path.name.lower() or "use" in file_path.stem.lower()):
                # Catch any .ts files that might be hooks
                self._parse_hook(content, str(relative_path), file_path)

        except Exception as e:
            print(f"Error parsing {file_path}: {e}")

    def _parse_component(self, content: str, relative_path: str, file_path: Path):
        """Parse a React component."""
        # Try to find component name
        # Pattern 1: export const ComponentName = () => {
        # Pattern 2: export const ComponentName: React.FC = () => {
        # Pattern 3: export function ComponentName() {

        component_name = None

        # Try pattern 1 & 2 (export const X = ..., const X = ...)
        match = re.search(r"(?:export\s+)?(?:default\s+)?const\s+(\w+)(?::\s*React\.FC)?\s*=", content)
        if match:
            component_name = match.group(1)

        # Try pattern 3 (export [default] function X)
        if not component_name:
            match = re.search(r"(?:export\s+)?(?:default\s+)?(?:function|const)\s+(\w+)", content)
            if match:
                component_name = match.group(1)

        # Fallback to file name if no explicit match
        if not component_name:
            component_name = file_path.stem
            # Still don't know if it's a component, verify it looks like one
            if not (component_name[0].isupper() or "return" in content):
                return

        # Extract imports
        imports = self._extract_imports(content)

        # Extract hooks used
        hooks_used = self._extract_hooks_used(content)

        # Extract API calls
        api_calls = self._extract_api_calls(content)

        # Extract props interface
        props_interface = self._extract_props_interface(content, component_name)

        # Extract state variables
        state_vars = self._extract_state_variables(content)

        # Find line number
        line_number = self._get_component_line_number(content, component_name)

        # Extract doc comment
        doc_comment = self._extract_doc_comment(content, line_number)

        component = {
            "id": component_name,
            "name": component_name,
            "type": "component",
            "layer": "frontend-web",
            "file_path": relative_path,
            "imports": imports,
            "hooks": hooks_used,
            "api_calls": api_calls,
            "props": props_interface,
            "state": state_vars,
            "line_start": line_number,
            "description": doc_comment,
        }

        self.components.append(component)

    def _parse_page(self, content: str, relative_path: str, file_path: Path):
        """Parse a React page component (special type of component)."""
        # Extract page name
        page_name = None

        match = re.search(r"(?:export\s+)?(?:default\s+)?const\s+(\w+)(?::\s*React\.FC)?\s*=", content)
        if match:
            page_name = match.group(1)

        if not page_name:
            match = re.search(r"(?:export\s+)?(?:default\s+)?function\s+(\w+)", content)
            if match:
                page_name = match.group(1)

        # Fallback to file name
        if not page_name:
            page_name = file_path.stem

        # Extract all the same info as component
        imports = self._extract_imports(content)
        hooks_used = self._extract_hooks_used(content)
        api_calls = self._extract_api_calls(content)
        state_vars = self._extract_state_variables(content)

        # Extract navigation/routing
        navigation = self._extract_navigation(content)

        # Find line number
        line_number = self._get_component_line_number(content, page_name)
        doc_comment = self._extract_doc_comment(content, line_number)

        page = {
            "id": page_name,
            "name": page_name,
            "type": "page",
            "layer": "frontend-web",
            "file_path": relative_path,
            "imports": imports,
            "hooks": hooks_used,
            "api_calls": api_calls,
            "state": state_vars,
            "navigation": navigation,
            "line_start": line_number,
            "description": doc_comment,
        }

        self.pages.append(page)

    def _parse_hook(self, content: str, relative_path: str, file_path: Path):
        """Parse a custom React hook."""
        # Extract hook name (should start with 'use')
        hook_match = re.search(r"export\s+(?:const|function)\s+(use\w+)", content)

        if not hook_match:
            return

        hook_name = hook_match.group(1)

        # Extract what this hook uses
        hooks_used = self._extract_hooks_used(content)

        # Extract API calls
        api_calls = self._extract_api_calls(content)

        # Extract state management
        state_vars = self._extract_state_variables(content)

        # Extract dependencies
        imports = self._extract_imports(content)

        # Extract return value
        return_pattern = r"return\s+{\s*([^}]+)\s*}"
        return_match = re.search(return_pattern, content, re.DOTALL)
        returns = []
        if return_match:
            returns = [
                r.strip() for r in return_match.group(1).split(",") if r.strip()
            ]

        # Find line number
        line_number = content[: hook_match.start()].count("\n") + 1
        doc_comment = self._extract_doc_comment(content, line_number)

        hook = {
            "id": hook_name,
            "name": hook_name,
            "type": "hook",
            "layer": "frontend-web",
            "file_path": relative_path,
            "hooks_used": hooks_used,
            "api_calls": api_calls,
            "state": state_vars,
            "returns": returns,
            "imports": imports,
            "line_start": line_number,
            "description": doc_comment,
        }

        self.hooks.append(hook)

    def _parse_service(self, content: str, relative_path: str, file_path: Path):
        """Parse API service files (like apiClient.ts)."""
        # Extract exported client name
        client_match = re.search(r"export\s+const\s+(\w+)\s*=\s*axios\.create", content)

        service_name = client_match.group(1) if client_match else file_path.stem

        # Extract base URL
        base_url_match = re.search(r"baseURL:\s*['\"]([^'\"]+)['\"]", content)
        base_url = base_url_match.group(1) if base_url_match else None

        # Extract interceptors
        interceptors = {
            "request": bool(re.search(r"interceptors\.request\.use", content)),
            "response": bool(re.search(r"interceptors\.response\.use", content)),
        }

        # Extract API calls defined in the file
        api_methods = []

        # Pattern for async function definitions
        method_pattern = r"export\s+(?:const|async\s+function)\s+(\w+)"
        matches = re.finditer(method_pattern, content)

        for match in matches:
            method_name = match.group(1)
            if method_name != service_name:
                api_methods.append(method_name)

        # Find line number
        line_number = self._get_service_line_number(content, service_name)
        doc_comment = self._extract_doc_comment(content, line_number)

        service = {
            "id": service_name,
            "name": service_name,
            "type": "api_client",
            "layer": "frontend-web",
            "file_path": relative_path,
            "base_url": base_url,
            "interceptors": interceptors,
            "methods": api_methods,
            "line_start": line_number,
            "description": doc_comment,
        }

        self.services.append(service)

    def _extract_imports(self, content: str) -> List[Dict[str, Any]]:
        """Extract import statements."""
        imports = []

        # Pattern: import { ... } from '...'
        import_pattern = r"import\s+(?:{([^}]+)}|(\w+))\s+from\s+['\"]([^'\"]+)['\"]"
        matches = re.finditer(import_pattern, content)

        for match in matches:
            named = match.group(1)
            default = match.group(2)
            source = match.group(3)

            if named:
                items = [item.strip() for item in named.split(",")]
                imports.append({"type": "named", "items": items, "from": source})
            elif default:
                imports.append({"type": "default", "items": [default], "from": source})

        return imports

    def _extract_hooks_used(self, content: str) -> List[str]:
        """Extract React hooks used in the component."""
        hooks = []

        # Standard hooks
        standard_hooks = [
            "useState",
            "useEffect",
            "useContext",
            "useReducer",
            "useCallback",
            "useMemo",
            "useRef",
            "useLayoutEffect",
        ]

        for hook in standard_hooks:
            if re.search(rf"\b{hook}\s*\(", content):
                hooks.append(hook)

        # Custom hooks (start with 'use')
        custom_hooks = re.findall(r"\b(use[A-Z]\w+)\s*\(", content)
        hooks.extend(list(set(custom_hooks)))

        return list(set(hooks))

    def _extract_api_calls(self, content: str) -> List[Dict[str, Any]]:
        """Extract API calls (axios, fetch, etc.)."""
        api_calls = []

        # Pattern: apiClient.get/post/put/delete('/path')
        client_pattern = r"(\w+)\.(get|post|put|delete|patch)\(['\"]([^'\"]+)['\"]"
        matches = re.finditer(client_pattern, content)

        for match in matches:
            client = match.group(1)
            method = match.group(2).upper()
            endpoint = match.group(3)
            line_number = content[: match.start()].count("\n") + 1

            api_calls.append(
                {
                    "client": client,
                    "method": method,
                    "endpoint": endpoint,
                    "line_number": line_number,
                }
            )

        # Pattern: await fetch('/path', { method: 'POST' })
        fetch_pattern = r"fetch\(['\"]([^'\"]+)['\"]"
        matches = re.finditer(fetch_pattern, content)

        for match in matches:
            endpoint = match.group(1)
            line_number = content[: match.start()].count("\n") + 1

            api_calls.append(
                {
                    "client": "fetch",
                    "method": "UNKNOWN",
                    "endpoint": endpoint,
                    "line_number": line_number,
                }
            )

        return api_calls

    def _extract_state_variables(self, content: str) -> List[Dict[str, Any]]:
        """Extract useState declarations."""
        state_vars = []

        # Pattern: const [varName, setVarName] = useState(...)
        pattern = r"const\s+\[(\w+),\s*(\w+)\]\s*=\s*useState(?:<([^>]+)>)?\("
        matches = re.finditer(pattern, content)

        for match in matches:
            var_name = match.group(1)
            setter_name = match.group(2)
            type_hint = match.group(3)
            line_number = content[: match.start()].count("\n") + 1

            state_vars.append(
                {
                    "name": var_name,
                    "setter": setter_name,
                    "type": type_hint,
                    "line_number": line_number,
                }
            )

        return state_vars

    def _extract_props_interface(
        self, content: str, component_name: str
    ) -> Optional[Dict[str, Any]]:
        """Extract props interface for a component."""
        # Pattern: interface ComponentNameProps { ... }
        interface_pattern = rf"interface\s+{component_name}Props\s*{{\s*([^}}]+)\s*}}"
        match = re.search(interface_pattern, content, re.DOTALL)

        if not match:
            return None

        props_body = match.group(1)

        # Extract individual props
        prop_pattern = r"(\w+)\??\s*:\s*([^;\n]+)"
        props = {}

        for prop_match in re.finditer(prop_pattern, props_body):
            prop_name = prop_match.group(1)
            prop_type = prop_match.group(2).strip()
            props[prop_name] = prop_type

        return props

    def _extract_navigation(self, content: str) -> List[Dict[str, Any]]:
        """Extract navigation calls."""
        navigation = []

        # Pattern: navigate('/path') or router.push('/path')
        nav_pattern = r"(?:navigate|router\.push)\(['\"]([^'\"]+)['\"]"
        matches = re.finditer(nav_pattern, content)

        for match in matches:
            path = match.group(1)
            line_number = content[: match.start()].count("\n") + 1

            navigation.append({"path": path, "line_number": line_number})

        return navigation

    def _get_component_line_number(self, content: str, component_name: str) -> int:
        """Get line number where component is defined."""
        pattern = rf"(?:export\s+)?(?:default\s+)?(?:const|function)\s+{component_name}"
        match = re.search(pattern, content)
        if match:
            return content[: match.start()].count("\n") + 1
        return 0

    def _get_service_line_number(self, content: str, service_name: str) -> int:
        """Get line number where service is defined."""
        pattern = rf"export\s+const\s+{service_name}"
        match = re.search(pattern, content)
        if match:
            return content[: match.start()].count("\n") + 1
        return 0

    def _extract_doc_comment(self, content: str, line_number: int) -> Optional[str]:
        """Extract documentation comment above a line."""
        if line_number < 2:
            return None

        lines = content.split("\n")
        comment_lines = []

        for i in range(line_number - 2, -1, -1):
            line = lines[i].strip()
            if line.startswith("/**") or line.startswith("*") or line.startswith("//"):
                comment_lines.insert(0, line)
            else:
                break

        if comment_lines:
            cleaned = "\n".join(comment_lines)
            cleaned = re.sub(r"\/\*\*|\*\/|\*|\/\/", "", cleaned).strip()
            return cleaned

        return None
