"""
Prompt Generator for Code Generation Tools
Uses Tree Sitter ontology to generate context-rich prompts for AI code generation tools.

This module takes requirements/features and generates prompts with relevant context from the ontology.
"""

from pathlib import Path
from typing import Dict, List, Any, Optional, Set
import json
from datetime import datetime


class PromptGenerator:
    """
    Generates AI-ready prompts from Tree Sitter ontology and user requirements.

    Workflow:
    1. User provides a requirement (e.g., "Add user profile editing feature")
    2. System analyzes ontology to find relevant context
    3. Generates structured prompt with:
       - Existing code structure
       - Related components
       - Dependency information
       - Code patterns to follow
       - Technical constraints
    4. Outputs prompt ready for Claude, GPT-4, Copilot, etc.
    """

    def __init__(self, ontology_data: Dict[str, Any], repo_path: str):
        """
        Initialize the prompt generator.

        Args:
            ontology_data: Parsed data from TreeSitterParser
            repo_path: Path to the source repository
        """
        self.ontology_data = ontology_data
        self.repo_path = Path(repo_path)
        self.entities = ontology_data.get("entities", {})
        self.files = ontology_data.get("files", [])

    def generate_prompt(
        self,
        requirement: str,
        context_type: str = "feature",
        related_files: Optional[List[str]] = None,
        constraints: Optional[List[str]] = None,
        include_patterns: bool = True,
        include_examples: bool = True,
    ) -> str:
        """
        Generate a comprehensive prompt for code generation tools.

        Args:
            requirement: The feature/fix/change to implement
            context_type: Type of change (feature, bugfix, refactor, test)
            related_files: Optional list of related file paths
            constraints: Optional technical constraints
            include_patterns: Whether to include existing code patterns
            include_examples: Whether to include example code

        Returns:
            Formatted prompt string ready for AI tools
        """
        print(f"🔨 Generating prompt for: {requirement}")

        # Analyze the requirement
        analysis = self._analyze_requirement(requirement, related_files)

        # Build prompt sections
        sections = []

        # Header
        sections.append(self._generate_header(requirement, context_type))

        # Project context
        sections.append(self._generate_project_context())

        # Relevant code context
        sections.append(self._generate_code_context(analysis))

        # Code patterns and conventions
        if include_patterns:
            sections.append(self._generate_patterns())

        # Examples from similar code
        if include_examples:
            sections.append(self._generate_examples(analysis))

        # Dependencies and imports
        sections.append(self._generate_dependencies(analysis))

        # Constraints
        if constraints:
            sections.append(self._generate_constraints(constraints))

        # Task specification
        sections.append(self._generate_task_specification(requirement, context_type))

        # Output requirements
        sections.append(self._generate_output_requirements(context_type))

        prompt = "\n\n".join(filter(None, sections))

        print(f"✅ Prompt generated ({len(prompt)} characters)")

        return prompt

    def _analyze_requirement(
        self, requirement: str, related_files: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Analyze the requirement to identify relevant code entities.

        Returns:
            Analysis results with relevant classes, functions, files, etc.
        """
        keywords = self._extract_keywords(requirement)

        analysis = {
            "keywords": keywords,
            "relevant_classes": [],
            "relevant_functions": [],
            "relevant_files": [],
            "related_imports": [],
            "language": None,
        }

        # Find relevant entities
        for entity_type, entity_list in self.entities.items():
            for entity in entity_list:
                score = self._calculate_relevance_score(entity, keywords, requirement)

                if score > 0:
                    if entity_type == "classes":
                        analysis["relevant_classes"].append((entity, score))
                    elif entity_type in ["functions", "methods"]:
                        analysis["relevant_functions"].append((entity, score))

                    # Track file
                    file_path = entity.get("file_path")
                    if file_path and file_path not in analysis["relevant_files"]:
                        analysis["relevant_files"].append(file_path)

                    # Track language
                    if not analysis["language"]:
                        analysis["language"] = entity.get("language")

        # Sort by relevance
        analysis["relevant_classes"].sort(key=lambda x: x[1], reverse=True)
        analysis["relevant_functions"].sort(key=lambda x: x[1], reverse=True)

        # Add explicitly related files
        if related_files:
            for file in related_files:
                if file not in analysis["relevant_files"]:
                    analysis["relevant_files"].append(file)

        return analysis

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from requirement text."""
        import re

        # Convert to lowercase
        text_lower = text.lower()

        # Remove common words
        stop_words = {
            "add", "create", "implement", "fix", "update", "modify",
            "the", "a", "an", "and", "or", "but", "for", "to", "in",
            "on", "at", "by", "with", "from", "about", "feature"
        }

        # Extract words
        words = re.findall(r'\b[a-z]+\b', text_lower)

        # Filter and deduplicate
        keywords = list(set(w for w in words if w not in stop_words and len(w) > 2))

        # Also extract CamelCase/snake_case identifiers
        identifiers = re.findall(r'\b[A-Z][a-zA-Z0-9_]*\b', text)
        keywords.extend(identifiers)

        return keywords

    def _calculate_relevance_score(
        self, entity: Dict, keywords: List[str], requirement: str
    ) -> int:
        """Calculate relevance score for an entity."""
        score = 0

        name = entity.get("name", "").lower()
        file_path = entity.get("file_path", "").lower()
        description = entity.get("description", "").lower() if entity.get("description") else ""

        for keyword in keywords:
            kw = keyword.lower()

            # Exact name match
            if kw == name:
                score += 50

            # Name contains keyword
            if kw in name:
                score += 20

            # File path match
            if kw in file_path:
                score += 10

            # Description match
            if description and kw in description:
                score += 5

        return score

    def _generate_header(self, requirement: str, context_type: str) -> str:
        """Generate prompt header."""
        return f"""# Code Generation Request

**Type:** {context_type.title()}
**Requirement:** {requirement}
**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---"""

    def _generate_project_context(self) -> str:
        """Generate project context section."""
        summary = self.ontology_data.get("summary", {})

        languages = summary.get("languages", [])
        total_files = summary.get("total_files", 0)
        entity_counts = summary.get("entity_counts", {})

        output = ["## 📁 Project Context\n"]

        output.append(f"**Total Files:** {total_files}")
        output.append(f"**Languages:** {', '.join(languages)}")

        if entity_counts:
            output.append("\n**Codebase Structure:**")
            for entity_type, count in entity_counts.items():
                if count > 0:
                    output.append(f"- {entity_type}: {count}")

        return "\n".join(output)

    def _generate_code_context(self, analysis: Dict[str, Any]) -> str:
        """Generate relevant code context section."""
        output = ["## 📝 Relevant Existing Code\n"]

        # Language context
        if analysis.get("language"):
            output.append(f"**Primary Language:** {analysis['language']}\n")

        # Relevant classes
        if analysis["relevant_classes"]:
            output.append("### Related Classes\n")

            for entity, score in analysis["relevant_classes"][:5]:  # Top 5
                output.append(f"#### {entity['name']}")
                output.append(f"- **File:** `{entity['file_path']}:{entity.get('line_start', 0)}`")
                output.append(f"- **Language:** {entity.get('language')}")

                if entity.get("bases"):
                    output.append(f"- **Inherits from:** {', '.join(entity['bases'])}")

                if entity.get("docstring"):
                    output.append(f"- **Description:** {entity['docstring'][:200]}")

                # Read actual code
                code = self._read_entity_code(entity)
                if code:
                    lang = self._get_code_fence_language(entity.get("language"))
                    output.append(f"\n```{lang}\n{code}\n```\n")

        # Relevant functions
        if analysis["relevant_functions"]:
            output.append("### Related Functions/Methods\n")

            for entity, score in analysis["relevant_functions"][:5]:  # Top 5
                output.append(f"#### {entity['name']}")
                output.append(f"- **File:** `{entity['file_path']}:{entity.get('line_start', 0)}`")
                output.append(f"- **Type:** {entity.get('type')}")

                if entity.get("parameters"):
                    output.append(f"- **Parameters:** {', '.join(entity['parameters'])}")

                if entity.get("docstring"):
                    output.append(f"- **Description:** {entity['docstring'][:200]}")

                code = self._read_entity_code(entity)
                if code:
                    lang = self._get_code_fence_language(entity.get("language"))
                    output.append(f"\n```{lang}\n{code}\n```\n")

        if not analysis["relevant_classes"] and not analysis["relevant_functions"]:
            output.append("*No directly related code found in the ontology.*\n")
            output.append("*You may be creating a new component.*\n")

        return "\n".join(output)

    def _generate_patterns(self) -> str:
        """Generate code patterns and conventions section."""
        output = ["## 🎨 Code Patterns & Conventions\n"]

        # Analyze naming conventions from existing code
        patterns = self._analyze_code_patterns()

        if patterns.get("naming_patterns"):
            output.append("### Naming Conventions")
            for pattern_type, examples in patterns["naming_patterns"].items():
                if examples:
                    output.append(f"- **{pattern_type}:** {', '.join(examples[:3])}")
            output.append("")

        if patterns.get("common_imports"):
            output.append("### Common Imports")
            for imp in patterns["common_imports"][:10]:
                output.append(f"- `{imp}`")
            output.append("")

        if patterns.get("file_structure"):
            output.append("### File Structure Patterns")
            for pattern in patterns["file_structure"]:
                output.append(f"- {pattern}")
            output.append("")

        return "\n".join(output)

    def _analyze_code_patterns(self) -> Dict[str, Any]:
        """Analyze patterns in existing codebase."""
        patterns = {
            "naming_patterns": {
                "Classes": [],
                "Functions": [],
                "Files": [],
            },
            "common_imports": [],
            "file_structure": [],
        }

        # Analyze classes
        for cls in self.entities.get("classes", [])[:20]:
            patterns["naming_patterns"]["Classes"].append(cls.get("name"))

        # Analyze functions
        for func in self.entities.get("functions", [])[:20]:
            patterns["naming_patterns"]["Functions"].append(func.get("name"))

        # Analyze imports
        import_counts = {}
        for imp in self.entities.get("imports", []):
            module = imp.get("module", "")
            if module:
                import_counts[module] = import_counts.get(module, 0) + 1

        # Get most common imports
        sorted_imports = sorted(import_counts.items(), key=lambda x: x[1], reverse=True)
        patterns["common_imports"] = [imp for imp, _ in sorted_imports[:10]]

        # File structure
        file_paths = [f.get("file_path") for f in self.files if f.get("file_path")]
        if file_paths:
            # Detect common directory patterns
            common_dirs = set()
            for path in file_paths:
                parts = Path(path).parts
                if len(parts) > 1:
                    common_dirs.add(parts[0])

            patterns["file_structure"] = [
                f"Code organized in: {', '.join(sorted(common_dirs))}"
            ]

        return patterns

    def _generate_examples(self, analysis: Dict[str, Any]) -> str:
        """Generate example code from similar implementations."""
        output = ["## 💡 Example Implementations\n"]

        language = analysis.get("language")

        if language:
            output.append(f"Here are examples from the {language} codebase:\n")

            # Show example class if available
            if analysis["relevant_classes"]:
                entity, _ = analysis["relevant_classes"][0]
                output.append(f"### Example Class: {entity['name']}\n")

                code = self._read_entity_code(entity)
                if code:
                    lang = self._get_code_fence_language(language)
                    output.append(f"```{lang}\n{code[:1000]}\n```\n")

        else:
            output.append("*No specific examples found. Create new implementation following best practices.*\n")

        return "\n".join(output)

    def _generate_dependencies(self, analysis: Dict[str, Any]) -> str:
        """Generate dependencies and imports section."""
        output = ["## 📦 Dependencies & Imports\n"]

        # Collect imports from relevant files
        relevant_imports = set()

        for file_path in analysis["relevant_files"]:
            for imp in self.entities.get("imports", []):
                if imp.get("file_path") == file_path:
                    module = imp.get("module")
                    if module:
                        relevant_imports.add(module)

        if relevant_imports:
            output.append("### Common Imports in Related Files\n")
            for imp in sorted(relevant_imports):
                output.append(f"- `{imp}`")
        else:
            output.append("*No specific imports identified. Include necessary dependencies as needed.*")

        return "\n".join(output)

    def _generate_constraints(self, constraints: List[str]) -> str:
        """Generate constraints section."""
        output = ["## ⚠️ Technical Constraints\n"]

        for constraint in constraints:
            output.append(f"- {constraint}")

        return "\n".join(output)

    def _generate_task_specification(self, requirement: str, context_type: str) -> str:
        """Generate task specification section."""
        output = ["## 🎯 Task Specification\n"]

        output.append(f"**Primary Goal:** {requirement}\n")

        if context_type == "feature":
            output.append("**Requirements:**")
            output.append("1. Implement the feature following existing code patterns")
            output.append("2. Ensure compatibility with existing components")
            output.append("3. Add appropriate error handling")
            output.append("4. Follow naming conventions from examples above")
            output.append("5. Add documentation/comments where appropriate")

        elif context_type == "bugfix":
            output.append("**Requirements:**")
            output.append("1. Identify and fix the root cause")
            output.append("2. Ensure the fix doesn't break existing functionality")
            output.append("3. Add checks to prevent similar issues")
            output.append("4. Maintain existing code style")

        elif context_type == "refactor":
            output.append("**Requirements:**")
            output.append("1. Improve code structure while maintaining functionality")
            output.append("2. Follow best practices and design patterns")
            output.append("3. Ensure backward compatibility")
            output.append("4. Update related documentation")

        elif context_type == "test":
            output.append("**Requirements:**")
            output.append("1. Write comprehensive test cases")
            output.append("2. Cover edge cases and error scenarios")
            output.append("3. Follow existing test patterns")
            output.append("4. Ensure tests are maintainable")

        return "\n".join(output)

    def _generate_output_requirements(self, context_type: str) -> str:
        """Generate output requirements section."""
        output = ["## 📤 Expected Output\n"]

        output.append("Please provide:\n")
        output.append("1. **Complete implementation code** with proper structure")
        output.append("2. **File paths** where code should be placed")
        output.append("3. **Brief explanation** of the approach")
        output.append("4. **Any additional files** needed (configs, types, etc.)")

        if context_type == "feature":
            output.append("5. **Integration points** with existing code")
            output.append("6. **Usage examples** if applicable")

        elif context_type == "test":
            output.append("5. **Test coverage** description")
            output.append("6. **Mock/fixture requirements** if needed")

        output.append("\n**Format:** Provide code blocks with file paths as comments.")

        return "\n".join(output)

    def _read_entity_code(self, entity: Dict[str, Any], max_lines: int = 100) -> Optional[str]:
        """Read source code for an entity."""
        file_path = entity.get("file_path")
        line_start = entity.get("line_start", 1)
        line_end = entity.get("line_end", line_start + max_lines)

        if not file_path:
            return None

        try:
            full_path = self.repo_path / file_path

            if not full_path.exists():
                return None

            with open(full_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            # Extract relevant lines
            start_idx = max(0, line_start - 1)
            end_idx = min(len(lines), line_end)

            code = "".join(lines[start_idx:end_idx])

            return code.strip()

        except Exception as e:
            print(f"  Error reading {file_path}: {e}")
            return None

    def _get_code_fence_language(self, language: Optional[str]) -> str:
        """Get appropriate code fence language identifier."""
        if not language:
            return ""

        mapping = {
            "python": "python",
            "javascript": "javascript",
            "typescript": "typescript",
            "java": "java",
            "go": "go",
            "rust": "rust",
            "c": "c",
            "cpp": "cpp",
            "c_sharp": "csharp",
            "ruby": "ruby",
            "php": "php",
            "swift": "swift",
            "kotlin": "kotlin",
        }

        return mapping.get(language, language)

    def save_prompt(self, prompt: str, output_path: str):
        """Save generated prompt to file."""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(prompt)

        print(f"💾 Prompt saved to: {output_file}")

    def generate_batch_prompts(
        self, requirements: List[Dict[str, Any]], output_dir: str
    ) -> List[str]:
        """
        Generate multiple prompts from a list of requirements.

        Args:
            requirements: List of requirement dicts with keys: requirement, context_type, constraints
            output_dir: Directory to save prompts

        Returns:
            List of generated prompt file paths
        """
        output_directory = Path(output_dir)
        output_directory.mkdir(parents=True, exist_ok=True)

        generated_files = []

        for idx, req in enumerate(requirements, 1):
            requirement = req.get("requirement", "")
            context_type = req.get("context_type", "feature")
            constraints = req.get("constraints", [])

            print(f"\nGenerating prompt {idx}/{len(requirements)}")

            prompt = self.generate_prompt(
                requirement=requirement,
                context_type=context_type,
                constraints=constraints,
            )

            # Generate filename
            filename = f"prompt_{idx:03d}_{context_type}.md"
            filepath = output_directory / filename

            self.save_prompt(prompt, str(filepath))
            generated_files.append(str(filepath))

        print(f"\n✅ Generated {len(generated_files)} prompts in {output_dir}")

        return generated_files
