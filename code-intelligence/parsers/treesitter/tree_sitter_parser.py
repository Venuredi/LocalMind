"""
Tree Sitter Global Parser
A universal parser that can read and analyze source code in any language supported by Tree Sitter.
"""

import tree_sitter_languages as tsl
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple
import json

# Import universal extractor
from .universal_extractor import UniversalExtractor


# Language file extension mappings
LANGUAGE_EXTENSIONS = {
    "python": [".py", ".pyi"],
    "javascript": [".js", ".mjs", ".cjs"],
    "typescript": [".ts"],
    "tsx": [".tsx"],
    "java": [".java"],
    "go": [".go"],
    "rust": [".rs"],
    "cpp": [".cpp", ".cc", ".cxx", ".hpp", ".h"],
    "c": [".c", ".h"],
    "c_sharp": [".cs"],
    "ruby": [".rb"],
    "php": [".php"],
    "swift": [".swift"],
    "kotlin": [".kt", ".kts"],
    "scala": [".scala"],
    "bash": [".sh", ".bash"],
    "yaml": [".yaml", ".yml"],
    "json": [".json"],
    "toml": [".toml"],
    "html": [".html", ".htm"],
    "css": [".css"],
    "sql": [".sql"],
}

# Excluded directories
_EXCLUDED_DIRS = {
    "node_modules", ".pnpm", ".npm",
    "dist", "build", ".next", "out",
    ".git", ".svn",
    "vendor", "__pycache__",
    ".venv", "venv", "env",
    "coverage", ".nyc_output",
    ".turbo", ".cache",
    "target", "bin", "obj",
}


def _is_excluded(file_path: Path) -> bool:
    """Check if a path should be excluded from parsing."""
    return any(part in _EXCLUDED_DIRS for part in file_path.parts)


class TreeSitterParser:
    """
    Universal parser using Tree Sitter for any programming language.

    Features:
    - Automatic language detection based on file extension
    - AST traversal and node extraction
    - Support for multiple languages
    - Extraction of code entities (classes, functions, imports, etc.)
    - Relationship mapping (calls, inheritance, imports)
    """

    def __init__(self, repo_path: str):
        """
        Initialize the parser.

        Args:
            repo_path: Path to the repository to parse
        """
        self.repo_path = Path(repo_path)
        self.parsers = {}  # Cache of language parsers
        self.parsed_files = []
        self.entities = {
            "classes": [],
            "functions": [],
            "methods": [],
            "imports": [],
            "variables": [],
            "constants": [],
            "interfaces": [],
            "enums": [],
            "structs": [],
        }
        self.relationships = []

        # Initialize universal extractor
        self.universal_extractor = UniversalExtractor()

    def _get_language_from_extension(self, file_path: Path) -> Optional[str]:
        """
        Determine the programming language from file extension.

        Args:
            file_path: Path to the file

        Returns:
            Language name or None if not supported
        """
        ext = file_path.suffix.lower()

        for lang, extensions in LANGUAGE_EXTENSIONS.items():
            if ext in extensions:
                return lang

        return None

    def _get_parser(self, language: str):
        """
        Get or create a Tree Sitter parser for the given language.

        Args:
            language: Language name

        Returns:
            Tree Sitter parser instance
        """
        if language not in self.parsers:
            try:
                self.parsers[language] = tsl.get_parser(language)
            except Exception as e:
                print(f"Warning: Could not load parser for {language}: {e}")
                return None

        return self.parsers[language]

    def parse_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """
        Parse a single file and extract entities.

        Args:
            file_path: Path to the file to parse

        Returns:
            Dictionary with parsed entities or None if parsing failed
        """
        # Detect language
        language = self._get_language_from_extension(file_path)
        if not language:
            return None

        # Get parser
        parser = self._get_parser(language)
        if not parser:
            return None

        try:
            # Read file content
            content = file_path.read_text(encoding="utf-8")

            # Parse with Tree Sitter
            tree = parser.parse(bytes(content, "utf-8"))
            root_node = tree.root_node

            # Extract entities based on language
            relative_path = file_path.relative_to(self.repo_path)

            result = {
                "file_path": str(relative_path),
                "language": language,
                "root_node": root_node,
                "content": content,
                "entities": self._extract_entities(root_node, content, language, str(relative_path)),
            }

            self.parsed_files.append(result)
            return result

        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
            return None

    def _extract_entities(
        self, node, content: str, language: str, file_path: str
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Extract code entities from the AST using UniversalExtractor.

        Args:
            node: Tree Sitter node
            content: Source code content
            language: Programming language
            file_path: Relative file path

        Returns:
            Dictionary of extracted entities
        """
        # Use UniversalExtractor to extract entities for ANY language
        entities = self.universal_extractor.extract_all(node, content, file_path, language)

        # Add entities to global collections
        for entity_type, entity_list in entities.items():
            if entity_type in self.entities:
                self.entities[entity_type].extend(entity_list)

        return entities

    def _traverse_ast(
        self, node, content: str, language: str, file_path: str, entities: Dict
    ):
        """
        Recursively traverse the AST and extract entities.

        Args:
            node: Current Tree Sitter node
            content: Source code content
            language: Programming language
            file_path: Relative file path
            entities: Dictionary to store extracted entities
        """
        node_type = node.type

        # Extract based on node type and language
        if language == "python":
            self._extract_python_entities(node, content, file_path, entities)
        elif language in ["javascript", "typescript", "tsx"]:
            self._extract_js_ts_entities(node, content, file_path, entities)
        elif language == "java":
            self._extract_java_entities(node, content, file_path, entities)
        elif language == "go":
            self._extract_go_entities(node, content, file_path, entities)
        elif language == "rust":
            self._extract_rust_entities(node, content, file_path, entities)

        # Recursively traverse children
        for child in node.children:
            self._traverse_ast(child, content, language, file_path, entities)

    def _extract_python_entities(
        self, node, content: str, file_path: str, entities: Dict
    ):
        """Extract entities from Python code."""
        node_type = node.type

        if node_type == "class_definition":
            class_name_node = node.child_by_field_name("name")
            if class_name_node:
                class_name = self._get_node_text(class_name_node, content)

                # Get base classes
                bases = []
                superclasses = node.child_by_field_name("superclasses")
                if superclasses:
                    for arg in superclasses.children:
                        if arg.type == "identifier":
                            bases.append(self._get_node_text(arg, content))

                # Get docstring
                docstring = self._extract_docstring(node, content)

                entities["classes"].append({
                    "id": f"{file_path}::{class_name}",
                    "name": class_name,
                    "type": "class",
                    "language": "python",
                    "file_path": file_path,
                    "line_start": node.start_point[0] + 1,
                    "line_end": node.end_point[0] + 1,
                    "bases": bases,
                    "docstring": docstring,
                })

        elif node_type == "function_definition":
            func_name_node = node.child_by_field_name("name")
            if func_name_node:
                func_name = self._get_node_text(func_name_node, content)

                # Get parameters
                params = []
                parameters = node.child_by_field_name("parameters")
                if parameters:
                    for param in parameters.children:
                        if param.type == "identifier":
                            params.append(self._get_node_text(param, content))

                # Get docstring
                docstring = self._extract_docstring(node, content)

                # Check if it's a method (inside a class)
                parent = node.parent
                is_method = False
                while parent:
                    if parent.type == "class_definition":
                        is_method = True
                        break
                    parent = parent.parent

                entity_type = "method" if is_method else "function"
                key = "methods" if is_method else "functions"

                entities[key].append({
                    "id": f"{file_path}::{func_name}",
                    "name": func_name,
                    "type": entity_type,
                    "language": "python",
                    "file_path": file_path,
                    "line_start": node.start_point[0] + 1,
                    "line_end": node.end_point[0] + 1,
                    "parameters": params,
                    "docstring": docstring,
                })

        elif node_type == "import_statement" or node_type == "import_from_statement":
            import_info = self._extract_import_info(node, content)
            if import_info:
                entities["imports"].append({
                    "type": "import",
                    "language": "python",
                    "file_path": file_path,
                    "line": node.start_point[0] + 1,
                    **import_info,
                })

    def _extract_js_ts_entities(
        self, node, content: str, file_path: str, entities: Dict
    ):
        """Extract entities from JavaScript/TypeScript code."""
        node_type = node.type

        if node_type == "class_declaration":
            name_node = node.child_by_field_name("name")
            if name_node:
                class_name = self._get_node_text(name_node, content)

                # Get heritage (extends, implements)
                heritage = []
                heritage_clause = node.child_by_field_name("heritage")
                if heritage_clause:
                    for child in heritage_clause.children:
                        if child.type in ["extends_clause", "implements_clause"]:
                            for type_node in child.children:
                                if type_node.type == "identifier":
                                    heritage.append(self._get_node_text(type_node, content))

                entities["classes"].append({
                    "id": f"{file_path}::{class_name}",
                    "name": class_name,
                    "type": "class",
                    "language": "javascript/typescript",
                    "file_path": file_path,
                    "line_start": node.start_point[0] + 1,
                    "line_end": node.end_point[0] + 1,
                    "heritage": heritage,
                })

        elif node_type in ["function_declaration", "method_definition", "arrow_function"]:
            name_node = node.child_by_field_name("name")
            func_name = self._get_node_text(name_node, content) if name_node else "anonymous"

            # Get parameters
            params = []
            parameters = node.child_by_field_name("parameters")
            if parameters:
                for param in parameters.children:
                    if param.type in ["identifier", "required_parameter", "optional_parameter"]:
                        param_name_node = param.child_by_field_name("name") if param.child_by_field_name("name") else param
                        params.append(self._get_node_text(param_name_node, content))

            is_method = node_type == "method_definition"
            entity_type = "method" if is_method else "function"
            key = "methods" if is_method else "functions"

            entities[key].append({
                "id": f"{file_path}::{func_name}",
                "name": func_name,
                "type": entity_type,
                "language": "javascript/typescript",
                "file_path": file_path,
                "line_start": node.start_point[0] + 1,
                "line_end": node.end_point[0] + 1,
                "parameters": params,
            })

        elif node_type == "interface_declaration":
            name_node = node.child_by_field_name("name")
            if name_node:
                interface_name = self._get_node_text(name_node, content)

                entities["interfaces"].append({
                    "id": f"{file_path}::{interface_name}",
                    "name": interface_name,
                    "type": "interface",
                    "language": "typescript",
                    "file_path": file_path,
                    "line_start": node.start_point[0] + 1,
                    "line_end": node.end_point[0] + 1,
                })

        elif node_type in ["import_statement", "import_declaration"]:
            import_info = self._extract_js_import_info(node, content)
            if import_info:
                entities["imports"].append({
                    "type": "import",
                    "language": "javascript/typescript",
                    "file_path": file_path,
                    "line": node.start_point[0] + 1,
                    **import_info,
                })

    def _extract_java_entities(
        self, node, content: str, file_path: str, entities: Dict
    ):
        """Extract entities from Java code."""
        node_type = node.type

        if node_type == "class_declaration":
            name_node = node.child_by_field_name("name")
            if name_node:
                class_name = self._get_node_text(name_node, content)

                # Get superclass and interfaces
                extends = []
                implements = []

                for child in node.children:
                    if child.type == "superclass":
                        type_node = child.child_by_field_name("type")
                        if type_node:
                            extends.append(self._get_node_text(type_node, content))
                    elif child.type == "super_interfaces":
                        for interface_type in child.children:
                            if interface_type.type == "type_identifier":
                                implements.append(self._get_node_text(interface_type, content))

                entities["classes"].append({
                    "id": f"{file_path}::{class_name}",
                    "name": class_name,
                    "type": "class",
                    "language": "java",
                    "file_path": file_path,
                    "line_start": node.start_point[0] + 1,
                    "line_end": node.end_point[0] + 1,
                    "extends": extends,
                    "implements": implements,
                })

        elif node_type == "interface_declaration":
            name_node = node.child_by_field_name("name")
            if name_node:
                interface_name = self._get_node_text(name_node, content)

                entities["interfaces"].append({
                    "id": f"{file_path}::{interface_name}",
                    "name": interface_name,
                    "type": "interface",
                    "language": "java",
                    "file_path": file_path,
                    "line_start": node.start_point[0] + 1,
                    "line_end": node.end_point[0] + 1,
                })

        elif node_type == "method_declaration":
            name_node = node.child_by_field_name("name")
            if name_node:
                method_name = self._get_node_text(name_node, content)

                entities["methods"].append({
                    "id": f"{file_path}::{method_name}",
                    "name": method_name,
                    "type": "method",
                    "language": "java",
                    "file_path": file_path,
                    "line_start": node.start_point[0] + 1,
                    "line_end": node.end_point[0] + 1,
                })

    def _extract_go_entities(
        self, node, content: str, file_path: str, entities: Dict
    ):
        """Extract entities from Go code."""
        node_type = node.type

        if node_type == "type_declaration":
            # Look for struct declarations
            for child in node.children:
                if child.type == "type_spec":
                    name_node = child.child_by_field_name("name")
                    type_node = child.child_by_field_name("type")

                    if name_node and type_node:
                        type_name = self._get_node_text(name_node, content)

                        if type_node.type == "struct_type":
                            entities["structs"].append({
                                "id": f"{file_path}::{type_name}",
                                "name": type_name,
                                "type": "struct",
                                "language": "go",
                                "file_path": file_path,
                                "line_start": node.start_point[0] + 1,
                                "line_end": node.end_point[0] + 1,
                            })
                        elif type_node.type == "interface_type":
                            entities["interfaces"].append({
                                "id": f"{file_path}::{type_name}",
                                "name": type_name,
                                "type": "interface",
                                "language": "go",
                                "file_path": file_path,
                                "line_start": node.start_point[0] + 1,
                                "line_end": node.end_point[0] + 1,
                            })

        elif node_type == "function_declaration":
            name_node = node.child_by_field_name("name")
            if name_node:
                func_name = self._get_node_text(name_node, content)

                entities["functions"].append({
                    "id": f"{file_path}::{func_name}",
                    "name": func_name,
                    "type": "function",
                    "language": "go",
                    "file_path": file_path,
                    "line_start": node.start_point[0] + 1,
                    "line_end": node.end_point[0] + 1,
                })

        elif node_type == "method_declaration":
            name_node = node.child_by_field_name("name")
            if name_node:
                method_name = self._get_node_text(name_node, content)

                # Get receiver type
                receiver = node.child_by_field_name("receiver")
                receiver_type = None
                if receiver:
                    for child in receiver.children:
                        if child.type in ["type_identifier", "pointer_type"]:
                            receiver_type = self._get_node_text(child, content)

                entities["methods"].append({
                    "id": f"{file_path}::{method_name}",
                    "name": method_name,
                    "type": "method",
                    "language": "go",
                    "file_path": file_path,
                    "line_start": node.start_point[0] + 1,
                    "line_end": node.end_point[0] + 1,
                    "receiver": receiver_type,
                })

    def _extract_rust_entities(
        self, node, content: str, file_path: str, entities: Dict
    ):
        """Extract entities from Rust code."""
        node_type = node.type

        if node_type == "struct_item":
            name_node = node.child_by_field_name("name")
            if name_node:
                struct_name = self._get_node_text(name_node, content)

                entities["structs"].append({
                    "id": f"{file_path}::{struct_name}",
                    "name": struct_name,
                    "type": "struct",
                    "language": "rust",
                    "file_path": file_path,
                    "line_start": node.start_point[0] + 1,
                    "line_end": node.end_point[0] + 1,
                })

        elif node_type == "enum_item":
            name_node = node.child_by_field_name("name")
            if name_node:
                enum_name = self._get_node_text(name_node, content)

                entities["enums"].append({
                    "id": f"{file_path}::{enum_name}",
                    "name": enum_name,
                    "type": "enum",
                    "language": "rust",
                    "file_path": file_path,
                    "line_start": node.start_point[0] + 1,
                    "line_end": node.end_point[0] + 1,
                })

        elif node_type == "function_item":
            name_node = node.child_by_field_name("name")
            if name_node:
                func_name = self._get_node_text(name_node, content)

                entities["functions"].append({
                    "id": f"{file_path}::{func_name}",
                    "name": func_name,
                    "type": "function",
                    "language": "rust",
                    "file_path": file_path,
                    "line_start": node.start_point[0] + 1,
                    "line_end": node.end_point[0] + 1,
                })

        elif node_type == "impl_item":
            # Extract methods from impl blocks
            type_node = node.child_by_field_name("type")
            impl_type = self._get_node_text(type_node, content) if type_node else "unknown"

            for child in node.children:
                if child.type == "function_item":
                    name_node = child.child_by_field_name("name")
                    if name_node:
                        method_name = self._get_node_text(name_node, content)

                        entities["methods"].append({
                            "id": f"{file_path}::{method_name}",
                            "name": method_name,
                            "type": "method",
                            "language": "rust",
                            "file_path": file_path,
                            "line_start": child.start_point[0] + 1,
                            "line_end": child.end_point[0] + 1,
                            "impl_for": impl_type,
                        })

    def _get_node_text(self, node, content: str) -> str:
        """Extract text content from a Tree Sitter node."""
        return content[node.start_byte:node.end_byte]

    def _extract_docstring(self, node, content: str) -> Optional[str]:
        """Extract docstring from a Python function/class."""
        body = node.child_by_field_name("body")
        if body and body.children:
            first_child = body.children[0]
            if first_child.type == "expression_statement":
                string_node = first_child.children[0]
                if string_node.type == "string":
                    return self._get_node_text(string_node, content).strip('"\' ')
        return None

    def _extract_import_info(self, node, content: str) -> Optional[Dict[str, Any]]:
        """Extract import information from Python import statements."""
        node_type = node.type

        if node_type == "import_statement":
            imports = []
            for child in node.children:
                if child.type == "dotted_name":
                    imports.append(self._get_node_text(child, content))
            return {"module": imports[0] if imports else "", "names": imports}

        elif node_type == "import_from_statement":
            module_node = node.child_by_field_name("module_name")
            module = self._get_node_text(module_node, content) if module_node else ""

            names = []
            for child in node.children:
                if child.type == "dotted_name" or child.type == "identifier":
                    if child != module_node:
                        names.append(self._get_node_text(child, content))

            return {"module": module, "names": names}

        return None

    def _extract_js_import_info(self, node, content: str) -> Optional[Dict[str, Any]]:
        """Extract import information from JavaScript/TypeScript import statements."""
        source_node = node.child_by_field_name("source")
        if not source_node:
            return None

        source = self._get_node_text(source_node, content).strip('\'"')

        names = []
        for child in node.children:
            if child.type == "import_clause":
                for subchild in child.children:
                    if subchild.type == "identifier":
                        names.append(self._get_node_text(subchild, content))
                    elif subchild.type == "named_imports":
                        for import_spec in subchild.children:
                            if import_spec.type == "import_specifier":
                                name_node = import_spec.child_by_field_name("name")
                                if name_node:
                                    names.append(self._get_node_text(name_node, content))

        return {"module": source, "names": names}

    def parse_repository(self) -> Dict[str, Any]:
        """
        Parse the entire repository.

        Returns:
            Dictionary containing all parsed entities and files
        """
        print(f"🔍 Parsing repository: {self.repo_path}")

        # Find all source files
        all_files = []
        for ext_list in LANGUAGE_EXTENSIONS.values():
            for ext in ext_list:
                all_files.extend(self.repo_path.rglob(f"*{ext}"))

        # Filter out excluded directories
        files_to_parse = [f for f in all_files if not _is_excluded(f)]

        print(f"   Found {len(files_to_parse)} files to parse")

        # Parse each file
        for file_path in files_to_parse:
            result = self.parse_file(file_path)
            if result:
                # Merge entities
                for entity_type, entity_list in result["entities"].items():
                    self.entities[entity_type].extend(entity_list)

        # Generate summary
        summary = {
            "total_files": len(self.parsed_files),
            "languages": list(set(f["language"] for f in self.parsed_files)),
            "entity_counts": {k: len(v) for k, v in self.entities.items()},
        }

        print(f"✅ Parsing complete:")
        print(f"   Files: {summary['total_files']}")
        print(f"   Languages: {', '.join(summary['languages'])}")
        print(f"   Entities: {sum(summary['entity_counts'].values())}")

        return {
            "summary": summary,
            "files": self.parsed_files,
            "entities": self.entities,
        }

    def save_results(self, output_path: str):
        """
        Save parsing results to JSON file.

        Args:
            output_path: Path to save the results
        """
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Prepare data for JSON serialization (remove non-serializable objects)
        serializable_data = {
            "summary": {
                "total_files": len(self.parsed_files),
                "languages": list(set(f["language"] for f in self.parsed_files)),
                "entity_counts": {k: len(v) for k, v in self.entities.items()},
            },
            "files": [
                {
                    "file_path": f["file_path"],
                    "language": f["language"],
                }
                for f in self.parsed_files
            ],
            "entities": self.entities,
        }

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(serializable_data, f, indent=2)

        print(f"💾 Results saved to: {output_file}")
