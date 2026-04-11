"""
Universal Code Extractor
Works for ANY language supported by Tree-sitter using generic AST pattern matching.
No language-specific code needed!
"""

from typing import Dict, List, Any, Optional, Set
from pathlib import Path
import re


class UniversalExtractor:
    """
    Universal code extractor that works for ANY programming language.

    Uses tree-sitter's AST structure to identify common patterns across languages:
    - Classes/Types
    - Functions/Methods
    - Interfaces
    - Imports/Dependencies
    - Inheritance/Implementation

    No language-specific logic required!
    """

    # Common AST node types across languages
    CLASS_NODE_TYPES = {
        'class_declaration',      # Java, C#, Python, TypeScript
        'class_definition',       # Python
        'type_declaration',       # Go
        'struct_item',           # Rust
        'class',                 # Ruby, PHP
        'interface_declaration', # TypeScript, Java, C#
        'trait_item',            # Rust
        'protocol_declaration',  # Swift
    }

    FUNCTION_NODE_TYPES = {
        'function_declaration',   # C, C++, Go, TypeScript
        'function_definition',    # Python, C++
        'method_declaration',     # Java, C#
        'method_definition',      # Ruby, Python
        'function_item',          # Rust
        'func_literal',          # Go
        'arrow_function',        # JavaScript, TypeScript
        'lambda',                # Python
    }

    METHOD_NODE_TYPES = {
        'method_declaration',     # Java, C#
        'method_definition',      # Ruby, Python
        'function_declaration',   # TypeScript (inside class)
    }

    IMPORT_NODE_TYPES = {
        'import_statement',       # Python, JavaScript
        'import_declaration',     # Java, TypeScript
        'using_directive',        # C#
        'use_declaration',        # Rust, PHP
        'package_clause',         # Go
        'include_statement',      # C/C++
        'require_statement',      # Ruby
    }

    INTERFACE_NODE_TYPES = {
        'interface_declaration',  # Java, C#, TypeScript
        'protocol_declaration',   # Swift
        'trait_item',            # Rust
    }

    ENUM_NODE_TYPES = {
        'enum_declaration',       # Java, C#, TypeScript
        'enum_item',             # Rust
    }

    STRUCT_NODE_TYPES = {
        'struct_item',              # Rust
        'struct_declaration',       # C, C++
        'type_declaration',         # Go (with struct type_spec)
        'type_spec',               # Go
    }

    def __init__(self):
        """Initialize the universal extractor."""
        pass

    def extract_all(self, root_node, content: str, file_path: str, language: str) -> Dict[str, List]:
        """
        Extract all entities from AST using universal patterns.

        Args:
            root_node: Tree-sitter root node
            content: Source code content
            file_path: Path to the file
            language: Programming language

        Returns:
            Dictionary with extracted entities
        """
        entities = {
            'classes': [],
            'functions': [],
            'methods': [],
            'imports': [],
            'interfaces': [],
            'enums': [],
            'structs': [],
        }

        # Traverse AST and extract entities
        self._traverse_node(root_node, content, file_path, language, entities)

        return entities

    def _traverse_node(self, node, content: str, file_path: str, language: str, entities: Dict):
        """Recursively traverse AST nodes and extract entities."""

        node_type = node.type

        # Extract based on node type
        if node_type in self.CLASS_NODE_TYPES:
            cls = self._extract_class(node, content, file_path, language)
            if cls:
                entities['classes'].append(cls)

        elif node_type in self.INTERFACE_NODE_TYPES:
            interface = self._extract_interface(node, content, file_path, language)
            if interface:
                entities['interfaces'].append(interface)

        elif node_type in self.ENUM_NODE_TYPES:
            enum = self._extract_enum(node, content, file_path, language)
            if enum:
                entities['enums'].append(enum)

        elif node_type in self.STRUCT_NODE_TYPES:
            struct = self._extract_struct(node, content, file_path, language)
            if struct:
                # Structs are conceptually similar to classes in Go/Rust
                # Treat them as classes for consistency
                struct['type'] = 'class'  # Normalize to class
                entities['classes'].append(struct)
                entities['structs'].append(struct)  # Also keep in structs

        elif node_type in self.FUNCTION_NODE_TYPES:
            func = self._extract_function(node, content, file_path, language)
            if func:
                # Determine if it's a method (inside a class) or standalone function
                if self._is_inside_class(node):
                    entities['methods'].append(func)
                else:
                    entities['functions'].append(func)

        elif node_type in self.IMPORT_NODE_TYPES:
            imp = self._extract_import(node, content, file_path, language)
            if imp:
                entities['imports'].append(imp)

        # Recursively process children
        for child in node.children:
            self._traverse_node(child, content, file_path, language, entities)

    def _extract_class(self, node, content: str, file_path: str, language: str) -> Optional[Dict]:
        """Extract class information from node."""
        try:
            name = self._get_node_text(node, content, ['name', 'identifier', 'type_identifier'])

            if not name:
                return None

            # Get base classes / inheritance
            base_classes = self._extract_inheritance(node, content)

            # Get methods
            methods = []
            for child in node.children:
                if child.type in self.METHOD_NODE_TYPES:
                    method_name = self._get_node_text(child, content, ['name', 'identifier'])
                    if method_name:
                        methods.append(method_name)

            # Get interfaces implemented
            interfaces = self._extract_implemented_interfaces(node, content)

            return {
                'id': f"{file_path}::{name}",
                'name': name,
                'type': 'class',
                'language': language,
                'file_path': file_path,
                'line_start': node.start_point[0] + 1,
                'line_end': node.end_point[0] + 1,
                'base_classes': base_classes,
                'methods': methods,
                'interfaces': interfaces,
                'node_type': node.type,  # Useful for debugging
            }
        except Exception as e:
            # Silently skip problematic nodes
            return None

    def _extract_function(self, node, content: str, file_path: str, language: str) -> Optional[Dict]:
        """Extract function/method information from node."""
        try:
            name = self._get_node_text(node, content, ['name', 'identifier', 'property_identifier'])

            if not name:
                return None

            # Get parameters
            parameters = self._extract_parameters(node, content)

            # Get return type
            return_type = self._extract_return_type(node, content)

            return {
                'id': f"{file_path}::{name}",
                'name': name,
                'type': 'function',
                'language': language,
                'file_path': file_path,
                'line_start': node.start_point[0] + 1,
                'line_end': node.end_point[0] + 1,
                'parameters': parameters,
                'return_type': return_type,
                'node_type': node.type,
            }
        except Exception as e:
            return None

    def _extract_interface(self, node, content: str, file_path: str, language: str) -> Optional[Dict]:
        """Extract interface information from node."""
        try:
            name = self._get_node_text(node, content, ['name', 'identifier', 'type_identifier'])

            if not name:
                return None

            # Get methods
            methods = []
            for child in node.children:
                if child.type in self.METHOD_NODE_TYPES or 'method' in child.type:
                    method_name = self._get_node_text(child, content, ['name', 'identifier'])
                    if method_name:
                        methods.append(method_name)

            return {
                'id': f"{file_path}::{name}",
                'name': name,
                'type': 'interface',
                'language': language,
                'file_path': file_path,
                'line_start': node.start_point[0] + 1,
                'line_end': node.end_point[0] + 1,
                'methods': methods,
                'node_type': node.type,
            }
        except Exception as e:
            return None

    def _extract_enum(self, node, content: str, file_path: str, language: str) -> Optional[Dict]:
        """Extract enum information from node."""
        try:
            name = self._get_node_text(node, content, ['name', 'identifier', 'type_identifier'])

            if not name:
                return None

            return {
                'id': f"{file_path}::{name}",
                'name': name,
                'type': 'enum',
                'language': language,
                'file_path': file_path,
                'line_start': node.start_point[0] + 1,
                'line_end': node.end_point[0] + 1,
                'node_type': node.type,
            }
        except Exception as e:
            return None

    def _extract_struct(self, node, content: str, file_path: str, language: str) -> Optional[Dict]:
        """Extract struct information from node."""
        try:
            name = self._get_node_text(node, content, ['name', 'identifier', 'type_identifier'])

            if not name:
                return None

            return {
                'id': f"{file_path}::{name}",
                'name': name,
                'type': 'struct',
                'language': language,
                'file_path': file_path,
                'line_start': node.start_point[0] + 1,
                'line_end': node.end_point[0] + 1,
                'node_type': node.type,
            }
        except Exception as e:
            return None

    def _extract_import(self, node, content: str, file_path: str, language: str) -> Optional[Dict]:
        """Extract import/using/include statement."""
        try:
            # Get the full import text
            import_text = self._get_node_text(node, content, ['source', 'name', 'identifier', 'string'])

            if not import_text:
                # Fallback: get full node text
                import_text = content[node.start_byte:node.end_byte]

            # Clean up the import text
            import_text = import_text.strip().strip('"').strip("'").strip(';')

            if not import_text:
                return None

            return {
                'type': 'import',
                'language': language,
                'file_path': file_path,
                'module': import_text,
                'line_number': node.start_point[0] + 1,
                'node_type': node.type,
            }
        except Exception as e:
            return None

    def _get_node_text(self, node, content: str, field_names: List[str]) -> Optional[str]:
        """
        Get text from node by trying multiple possible field names.
        Different languages use different field names for the same concept.
        """
        # Try to get child node by field name
        for field_name in field_names:
            child = node.child_by_field_name(field_name)
            if child:
                text = content[child.start_byte:child.end_byte]
                return text.strip()

        # Fallback: try to find identifier in children
        for child in node.children:
            if 'identifier' in child.type or 'name' in child.type:
                text = content[child.start_byte:child.end_byte]
                return text.strip()

        return None

    def _extract_inheritance(self, node, content: str) -> List[str]:
        """Extract base classes / inheritance."""
        base_classes = []

        # Common field names for inheritance
        inheritance_fields = ['superclass', 'base_class_list', 'extends', 'implements']

        for field_name in inheritance_fields:
            child = node.child_by_field_name(field_name)
            if child:
                text = content[child.start_byte:child.end_byte]
                # Extract class names from the text
                matches = re.findall(r'\b[A-Z]\w+\b', text)
                base_classes.extend(matches)

        return list(set(base_classes))  # Remove duplicates

    def _extract_implemented_interfaces(self, node, content: str) -> List[str]:
        """Extract implemented interfaces."""
        interfaces = []

        # Look for implements/interface list
        for child in node.children:
            if 'implements' in child.type or 'interface' in child.type:
                text = content[child.start_byte:child.end_byte]
                matches = re.findall(r'\b[A-Z]\w+\b', text)
                interfaces.extend(matches)

        return list(set(interfaces))

    def _extract_parameters(self, node, content: str) -> List[Dict]:
        """Extract function/method parameters."""
        parameters = []

        # Look for parameter list
        param_list = node.child_by_field_name('parameters')
        if not param_list:
            # Try to find parameter list in children
            for child in node.children:
                if 'parameter' in child.type:
                    param_list = child
                    break

        if param_list:
            for child in param_list.children:
                if 'parameter' in child.type or 'identifier' in child.type:
                    param_name = self._get_node_text(child, content, ['name', 'identifier'])
                    if param_name and param_name not in ['(', ')', ',']:
                        parameters.append({'name': param_name})

        return parameters

    def _extract_return_type(self, node, content: str) -> Optional[str]:
        """Extract return type of function/method."""
        return_type_node = node.child_by_field_name('return_type')
        if return_type_node:
            return content[return_type_node.start_byte:return_type_node.end_byte].strip()

        # Try to find type in children
        for child in node.children:
            if 'type' in child.type and 'type_' in child.type:
                return content[child.start_byte:child.end_byte].strip()

        return None

    def _is_inside_class(self, node) -> bool:
        """Check if a node is inside a class/struct."""
        parent = node.parent
        while parent:
            if parent.type in self.CLASS_NODE_TYPES or parent.type in self.STRUCT_NODE_TYPES:
                return True
            parent = parent.parent
        return False
