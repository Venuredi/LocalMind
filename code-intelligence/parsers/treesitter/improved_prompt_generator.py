"""
Improved Prompt Generator with Intent Classification and File Targeting
Addresses critical feedback issues:
1. File targeting - explicitly mentions files get priority
2. Intent classification - analyze vs refactor vs enhance vs prompt generation
3. Prompt output mode - generates ready-to-use prompts
4. Context filtering - only relevant files (top 1-3)
5. Noise reduction - no irrelevant components
"""

from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple
import json
from datetime import datetime
import re


class IntentType:
    """Intent classification for requirements."""
    ANALYZE = "analyze"
    REFACTOR = "refactor"
    ENHANCE = "enhance"
    GENERATE_PROMPT = "generate_prompt"
    FEATURE = "feature"
    BUGFIX = "bugfix"
    TEST = "test"


class ImprovedPromptGenerator:
    """
    Improved prompt generator with:
    - File targeting
    - Intent classification
    - Context filtering
    - Prompt-ready output
    """

    def __init__(self, ontology_data: Dict[str, Any], repo_path: str):
        """Initialize the improved prompt generator."""
        self.ontology_data = ontology_data
        self.repo_path = Path(repo_path)
        self.entities = ontology_data.get("entities", {})
        self.files = ontology_data.get("files", [])

    def generate_prompt(
        self,
        requirement: str,
        related_files: Optional[List[str]] = None,
        constraints: Optional[List[str]] = None,
        max_context_files: int = 3,
    ) -> str:
        """
        Generate AI-ready prompt with intent classification and file targeting.

        Args:
            requirement: User requirement (e.g., "enhance AssetListGrid.tsx")
            related_files: Optional explicit file list
            constraints: Optional constraints
            max_context_files: Maximum context files (default: 3 for focus)

        Returns:
            Ready-to-use prompt string
        """
        print(f"🔨 Analyzing requirement: {requirement}")

        # Step 1: Classify intent
        intent = self._classify_intent(requirement)
        print(f"   Intent detected: {intent}")

        # Step 2: Extract target files from requirement
        target_files = self._extract_target_files(requirement)
        print(f"   Target files: {target_files if target_files else 'None'}")

        # Step 3: Analyze and get relevant context
        analysis = self._analyze_requirement_focused(
            requirement, target_files, related_files, max_context_files
        )

        # Step 4: Check if target files are present
        missing_files = self._check_target_files_present(target_files, analysis)
        if missing_files:
            print(f"   ⚠️ WARNING: Target files not found: {missing_files}")

        # Step 5: Generate prompt based on intent
        if intent == IntentType.GENERATE_PROMPT:
            prompt = self._generate_meta_prompt(requirement, analysis, constraints)
        elif intent == IntentType.ANALYZE:
            prompt = self._generate_analyze_prompt(requirement, analysis, target_files)
        elif intent == IntentType.ENHANCE:
            prompt = self._generate_enhance_prompt(requirement, analysis, target_files, constraints)
        elif intent == IntentType.REFACTOR:
            prompt = self._generate_refactor_prompt(requirement, analysis, target_files, constraints)
        elif intent == IntentType.BUGFIX:
            prompt = self._generate_bugfix_prompt(requirement, analysis, target_files, constraints)
        else:  # FEATURE
            prompt = self._generate_feature_prompt(requirement, analysis, constraints)

        print(f"✅ Prompt generated ({len(prompt)} chars)")
        return prompt

    def _classify_intent(self, requirement: str) -> str:
        """
        Classify user intent from requirement text.

        Intent mapping:
        - "analyze", "understand", "explain" → ANALYZE
        - "refactor", "restructure", "improve structure" → REFACTOR
        - "enhance", "improve", "add features" → ENHANCE
        - "give me prompt", "generate prompt" → GENERATE_PROMPT
        - "fix", "bug", "issue" → BUGFIX
        - "test", "write tests" → TEST
        - default → FEATURE
        """
        req_lower = requirement.lower()

        # Check for meta-prompt request
        if any(phrase in req_lower for phrase in [
            "give me prompt", "generate prompt", "create prompt",
            "give me the required prompt", "required prompt"
        ]):
            return IntentType.GENERATE_PROMPT

        # Check for analyze intent
        if any(phrase in req_lower for phrase in [
            "analyze", "analyse", "understand", "explain", "what does",
            "how does", "tell me about"
        ]):
            return IntentType.ANALYZE

        # Check for enhance intent
        if any(phrase in req_lower for phrase in [
            "enhance", "improve", "add features to", "make better",
            "upgrade", "extend"
        ]):
            return IntentType.ENHANCE

        # Check for refactor intent
        if any(phrase in req_lower for phrase in [
            "refactor", "restructure", "reorganize", "clean up",
            "improve structure", "simplify"
        ]):
            return IntentType.REFACTOR

        # Check for bugfix intent
        if any(phrase in req_lower for phrase in [
            "fix", "bug", "issue", "error", "broken", "not working",
            "crash", "problem"
        ]):
            return IntentType.BUGFIX

        # Check for test intent
        if any(phrase in req_lower for phrase in [
            "test", "write tests", "unit test", "integration test",
            "test coverage"
        ]):
            return IntentType.TEST

        # Default to feature
        return IntentType.FEATURE

    def _extract_target_files(self, requirement: str) -> List[str]:
        """
        Extract file names explicitly mentioned in requirement.

        Examples:
        - "enhance AssetListGrid.tsx" → ["AssetListGrid.tsx"]
        - "fix auth.service.ts and user.service.ts" → ["auth.service.ts", "user.service.ts"]
        - "improve the login component" → []
        """
        # Pattern: match file names with extensions
        file_pattern = r'\b[\w-]+\.[a-zA-Z]{2,4}\b'
        matches = re.findall(file_pattern, requirement)

        return list(set(matches))  # Deduplicate

    def _analyze_requirement_focused(
        self,
        requirement: str,
        target_files: List[str],
        related_files: Optional[List[str]],
        max_files: int
    ) -> Dict[str, Any]:
        """
        Focused analysis - prioritize target files, minimize noise.

        Priority:
        1. Explicitly mentioned files (target_files)
        2. Explicitly related files (related_files)
        3. Top matching entities (limited to max_files)
        """
        analysis = {
            "keywords": self._extract_keywords(requirement),
            "target_files": target_files or [],
            "related_files": related_files or [],
            "relevant_entities": [],
            "language": None,
        }

        # Combine target and related files
        priority_files = set(target_files or [])
        if related_files:
            priority_files.update(related_files)

        # Find entities in priority files
        for entity_type, entity_list in self.entities.items():
            for entity in entity_list:
                file_path = entity.get("file_path", "")
                file_name = Path(file_path).name

                # Priority 1: Exact match to target/related files
                if file_name in priority_files or file_path in priority_files:
                    analysis["relevant_entities"].append({
                        "entity": entity,
                        "type": entity_type,
                        "score": 100,  # Highest priority
                        "reason": "explicitly_mentioned"
                    })
                    if not analysis["language"]:
                        analysis["language"] = entity.get("language")

        # If no priority files found, fall back to keyword matching (limited)
        if not analysis["relevant_entities"]:
            keywords = analysis["keywords"]
            scored_entities = []

            for entity_type, entity_list in self.entities.items():
                for entity in entity_list:
                    score = self._calculate_relevance_score(entity, keywords, requirement)
                    if score > 10:  # Higher threshold to reduce noise
                        scored_entities.append({
                            "entity": entity,
                            "type": entity_type,
                            "score": score,
                            "reason": "keyword_match"
                        })

            # Sort and take top N
            scored_entities.sort(key=lambda x: x["score"], reverse=True)
            analysis["relevant_entities"] = scored_entities[:max_files]

        return analysis

    def _check_target_files_present(
        self, target_files: List[str], analysis: Dict[str, Any]
    ) -> List[str]:
        """Check if target files are present in analysis."""
        if not target_files:
            return []

        found_files = set()
        for item in analysis["relevant_entities"]:
            entity = item["entity"]
            file_path = entity.get("file_path", "")
            file_name = Path(file_path).name
            found_files.add(file_name)

        missing = [f for f in target_files if f not in found_files]
        return missing

    def _generate_meta_prompt(
        self, requirement: str, analysis: Dict[str, Any], constraints: Optional[List[str]]
    ) -> str:
        """
        Generate a meta-prompt (prompt for generating prompts).
        When user says "give me the required prompt".
        """
        # Extract the actual task from requirement
        task = requirement.replace("give me prompt", "").replace("give me the required prompt", "").strip()

        output = []
        output.append("## Generated Prompt for AI Tool\n")
        output.append("Copy the text below and paste into your AI coding assistant (Claude, Cursor, Copilot, etc.):\n")
        output.append("---\n")

        # Generate the actual prompt content
        output.append(f"**Task:** {task}\n")

        # Add context if available
        if analysis["relevant_entities"]:
            output.append("**Context:**\n")
            for item in analysis["relevant_entities"][:2]:  # Top 2 only
                entity = item["entity"]
                file_path = entity.get("file_path")
                output.append(f"\nFile: `{file_path}`\n")

                code = self._read_entity_code(entity, max_lines=50)
                if code:
                    lang = self._get_code_fence_language(entity.get("language"))
                    output.append(f"```{lang}\n{code}\n```\n")

        # Add constraints if provided
        if constraints:
            output.append("\n**Requirements:**\n")
            for constraint in constraints:
                output.append(f"- {constraint}\n")

        output.append("\n**Expected Output:**\n")
        output.append("- Complete implementation code\n")
        output.append("- Explanation of changes\n")
        output.append("- File paths for new/modified files\n")

        output.append("\n---\n")
        output.append("*Paste the above section into your AI tool*")

        return "".join(output)

    def _generate_analyze_prompt(
        self, requirement: str, analysis: Dict[str, Any], target_files: List[str]
    ) -> str:
        """Generate prompt for analysis intent."""
        output = []

        output.append("## Code Analysis Request\n")
        output.append(f"**Request:** {requirement}\n\n")

        if target_files:
            output.append(f"**Target File(s):** {', '.join(target_files)}\n\n")

        # Include ONLY the target file code
        output.append("**Code to Analyze:**\n\n")

        for item in analysis["relevant_entities"][:1]:  # Only the main file
            entity = item["entity"]
            file_path = entity.get("file_path")

            output.append(f"### {Path(file_path).name}\n")
            output.append(f"Location: `{file_path}`\n\n")

            code = self._read_entity_code(entity, max_lines=200)
            if code:
                lang = self._get_code_fence_language(entity.get("language"))
                output.append(f"```{lang}\n{code}\n```\n\n")

        output.append("**What to Analyze:**\n")
        output.append("1. Code structure and organization\n")
        output.append("2. Purpose and functionality\n")
        output.append("3. Dependencies and imports\n")
        output.append("4. Potential issues or improvements\n")
        output.append("5. Best practices compliance\n")

        return "".join(output)

    def _generate_enhance_prompt(
        self,
        requirement: str,
        analysis: Dict[str, Any],
        target_files: List[str],
        constraints: Optional[List[str]]
    ) -> str:
        """Generate prompt for enhancement intent."""
        output = []

        output.append("## Enhancement Request\n")
        output.append(f"**Task:** {requirement}\n\n")

        if target_files:
            output.append(f"**Target File(s):** {', '.join(target_files)}\n\n")

        # Include target file code
        output.append("**Current Implementation:**\n\n")

        for item in analysis["relevant_entities"][:2]:  # Top 2 files
            entity = item["entity"]
            file_path = entity.get("file_path")

            output.append(f"### {Path(file_path).name}\n")
            output.append(f"Location: `{file_path}`\n\n")

            code = self._read_entity_code(entity, max_lines=150)
            if code:
                lang = self._get_code_fence_language(entity.get("language"))
                output.append(f"```{lang}\n{code}\n```\n\n")

        output.append("**Enhancement Goals:**\n")
        output.append("1. **Performance:**\n")
        output.append("   - Add memoization where beneficial\n")
        output.append("   - Optimize rendering (consider virtualization for lists)\n")
        output.append("   - Reduce unnecessary re-renders\n\n")

        output.append("2. **UX Improvements:**\n")
        output.append("   - Add loading states\n")
        output.append("   - Add empty states\n")
        output.append("   - Improve error handling UI\n")
        output.append("   - Enhance responsiveness\n\n")

        output.append("3. **Code Quality:**\n")
        output.append("   - Extract reusable components\n")
        output.append("   - Separate business logic into hooks\n")
        output.append("   - Improve type safety\n")
        output.append("   - Add proper error boundaries\n\n")

        output.append("4. **Maintainability:**\n")
        output.append("   - Add documentation/comments\n")
        output.append("   - Follow existing code patterns\n")
        output.append("   - Ensure backward compatibility\n\n")

        if constraints:
            output.append("**Constraints:**\n")
            for constraint in constraints:
                output.append(f"- {constraint}\n")
            output.append("\n")

        output.append("**Expected Output:**\n")
        output.append("1. Enhanced code with improvements\n")
        output.append("2. Explanation of each enhancement\n")
        output.append("3. Before/after comparison for key changes\n")
        output.append("4. Any new files or dependencies needed\n")

        return "".join(output)

    def _generate_refactor_prompt(
        self,
        requirement: str,
        analysis: Dict[str, Any],
        target_files: List[str],
        constraints: Optional[List[str]]
    ) -> str:
        """Generate prompt for refactoring intent."""
        output = []

        output.append("## Code Refactoring Request\n")
        output.append(f"**Task:** {requirement}\n\n")

        if target_files:
            output.append(f"**Target File(s):** {', '.join(target_files)}\n\n")

        # Include target file code
        output.append("**Code to Refactor:**\n\n")

        for item in analysis["relevant_entities"][:2]:
            entity = item["entity"]
            file_path = entity.get("file_path")

            output.append(f"### {Path(file_path).name}\n")
            output.append(f"Location: `{file_path}`\n\n")

            code = self._read_entity_code(entity, max_lines=150)
            if code:
                lang = self._get_code_fence_language(entity.get("language"))
                output.append(f"```{lang}\n{code}\n```\n\n")

        output.append("**Refactoring Goals:**\n")
        output.append("1. Improve code structure and organization\n")
        output.append("2. Extract reusable components/functions\n")
        output.append("3. Apply SOLID principles\n")
        output.append("4. Reduce code duplication\n")
        output.append("5. Improve readability and maintainability\n")
        output.append("6. Maintain existing functionality (no behavior changes)\n\n")

        if constraints:
            output.append("**Constraints:**\n")
            for constraint in constraints:
                output.append(f"- {constraint}\n")
            output.append("\n")

        output.append("**Expected Output:**\n")
        output.append("1. Refactored code\n")
        output.append("2. Explanation of structural changes\n")
        output.append("3. List of extracted components/utilities\n")
        output.append("4. Migration guide if breaking changes\n")

        return "".join(output)

    def _generate_bugfix_prompt(
        self,
        requirement: str,
        analysis: Dict[str, Any],
        target_files: List[str],
        constraints: Optional[List[str]]
    ) -> str:
        """Generate prompt for bug fix intent."""
        output = []

        output.append("## Bug Fix Request\n")
        output.append(f"**Issue:** {requirement}\n\n")

        if target_files:
            output.append(f"**Affected File(s):** {', '.join(target_files)}\n\n")

        # Include relevant code
        output.append("**Current Code:**\n\n")

        for item in analysis["relevant_entities"][:2]:
            entity = item["entity"]
            file_path = entity.get("file_path")

            output.append(f"### {Path(file_path).name}\n")
            output.append(f"Location: `{file_path}`\n\n")

            code = self._read_entity_code(entity, max_lines=100)
            if code:
                lang = self._get_code_fence_language(entity.get("language"))
                output.append(f"```{lang}\n{code}\n```\n\n")

        output.append("**Debug Checklist:**\n")
        output.append("1. Identify root cause of the issue\n")
        output.append("2. Check for edge cases\n")
        output.append("3. Verify error handling\n")
        output.append("4. Test the fix thoroughly\n")
        output.append("5. Ensure no regressions\n\n")

        if constraints:
            output.append("**Constraints:**\n")
            for constraint in constraints:
                output.append(f"- {constraint}\n")
            output.append("\n")

        output.append("**Expected Output:**\n")
        output.append("1. Fixed code\n")
        output.append("2. Explanation of the bug and the fix\n")
        output.append("3. Test cases to prevent regression\n")

        return "".join(output)

    def _generate_feature_prompt(
        self, requirement: str, analysis: Dict[str, Any], constraints: Optional[List[str]]
    ) -> str:
        """Generate prompt for new feature implementation."""
        output = []

        output.append("## New Feature Implementation\n")
        output.append(f"**Feature:** {requirement}\n\n")

        # Show relevant existing code as examples
        if analysis["relevant_entities"]:
            output.append("**Related Existing Code:**\n\n")

            for item in analysis["relevant_entities"][:2]:
                entity = item["entity"]
                file_path = entity.get("file_path")

                output.append(f"### {Path(file_path).name}\n")
                output.append(f"Reference: `{file_path}`\n\n")

                code = self._read_entity_code(entity, max_lines=80)
                if code:
                    lang = self._get_code_fence_language(entity.get("language"))
                    output.append(f"```{lang}\n{code}\n```\n\n")

        output.append("**Implementation Requirements:**\n")
        output.append("1. Follow existing code patterns\n")
        output.append("2. Maintain consistency with codebase style\n")
        output.append("3. Add proper error handling\n")
        output.append("4. Include appropriate tests\n")
        output.append("5. Add documentation/comments\n\n")

        if constraints:
            output.append("**Constraints:**\n")
            for constraint in constraints:
                output.append(f"- {constraint}\n")
            output.append("\n")

        output.append("**Expected Output:**\n")
        output.append("1. Complete feature implementation\n")
        output.append("2. File paths for new/modified files\n")
        output.append("3. Integration instructions\n")
        output.append("4. Usage examples\n")

        return "".join(output)

    # Helper methods (same as before but simplified)

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text."""
        import re

        text_lower = text.lower()
        stop_words = {
            "add", "create", "implement", "fix", "update", "modify",
            "the", "a", "an", "and", "or", "but", "for", "to", "in",
            "enhance", "give", "me", "required", "prompt"
        }

        words = re.findall(r'\b[a-z]+\b', text_lower)
        keywords = list(set(w for w in words if w not in stop_words and len(w) > 2))

        # Also extract identifiers
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

        for keyword in keywords:
            kw = keyword.lower()

            if kw == name:
                score += 50
            if kw in name:
                score += 20
            if kw in file_path:
                score += 10

        return score

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

            start_idx = max(0, line_start - 1)
            end_idx = min(len(lines), line_end)

            code = "".join(lines[start_idx:end_idx])

            return code.strip()

        except Exception as e:
            print(f"  Error reading {file_path}: {e}")
            return None

    def _get_code_fence_language(self, language: Optional[str]) -> str:
        """Get code fence language identifier."""
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
        }

        return mapping.get(language, language)

    def save_prompt(self, prompt: str, output_path: str):
        """Save generated prompt to file."""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(prompt)

        print(f"💾 Prompt saved to: {output_file}")
