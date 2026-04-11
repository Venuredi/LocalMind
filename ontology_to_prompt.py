#!/usr/bin/env python3
"""
Ontology to Prompt Generator (Standalone)

Converts ontology JSON into clean, validated, hallucination-resistant prompts.

Features:
✅ Ontology parsing
✅ Layer detection (backend vs frontend)
✅ Constructor dependency extraction
✅ Deduplication
✅ Validation checks (fail fast)
✅ Strict mode prompt generation

Usage:
    python ontology_to_prompt.py <ontology.json> <ComponentName>

Example:
    python ontology_to_prompt.py code-intelligence/data/index.json SurgeonsService
"""

import json
import re
import sys
from typing import Dict, List, Set
from pathlib import Path


# ============================================================================
# Helpers
# ============================================================================

def load_ontology(file_path: str) -> Dict:
    """Load ontology JSON file."""
    with open(file_path, "r") as f:
        data = json.load(f)

    # Convert components list to dict for easier lookup
    components = data.get('components', [])
    ontology = {}

    for comp in components:
        name = comp.get('name', '')
        if name:
            ontology[name] = comp

    return ontology


def dedupe(items: List[str]) -> List[str]:
    """Deduplicate and sort list of strings."""
    return sorted(list(set(items)))


def detect_stack(file_path: str) -> str:
    """
    Detect technology stack from file path.

    Returns: 'nestjs-backend', 'react-frontend', 'flutter-mobile', or 'unknown'
    """
    file_path_lower = file_path.lower()

    # Backend detection
    if any(keyword in file_path_lower for keyword in [
        'backend', 'backend-service', 'api', 'server', '/services/', '/repositories/'
    ]):
        return 'nestjs-backend'

    # Frontend web detection
    if any(keyword in file_path_lower for keyword in [
        'frontend', 'web', 'react', '/components/', '/pages/', '/hooks/'
    ]):
        return 'react-frontend'

    # Mobile detection
    if any(keyword in file_path_lower for keyword in [
        'mobile', 'flutter', 'dart', '/lib/', '/screens/'
    ]):
        return 'flutter-mobile'

    return 'unknown'


def extract_constructor_dependencies(code: str) -> List[str]:
    """
    Extract dependencies from TypeScript/JavaScript constructor.

    Example:
        constructor(private readonly repo: RepoService)

    Returns:
        ['RepoService']
    """
    if not code:
        return []

    # Find constructor
    pattern = r'constructor\s*\((.*?)\)'
    match = re.search(pattern, code, re.DOTALL)

    if not match:
        return []

    params_block = match.group(1)

    # Extract type annotations (what comes after ':')
    deps = re.findall(r':\s*([A-Za-z0-9_]+)', params_block)

    return dedupe(deps)


def validate_prompt_inputs(stack: str, dependencies: List[str], component_name: str, code: str):
    """
    Validate inputs before generating prompt.

    Raises:
        ValueError: If validation fails
    """
    errors = []
    warnings = []

    if stack == 'unknown':
        errors.append("Stack detection failed (Unknown Stack)")

    if not code:
        warnings.append("Source code not available - prompt will lack implementation details")

    if not dependencies and code:
        warnings.append(f"No dependencies detected for {component_name} - component may be isolated or constructor parsing failed")

    if errors:
        raise ValueError(f"Validation failed:\n" + "\n".join(f"  - {e}" for e in errors))

    if warnings:
        print("⚠️  Warnings:")
        for warning in warnings:
            print(f"  - {warning}")
        print()


def categorize_dependencies(dependencies: List[str], ontology: Dict) -> Dict[str, List[str]]:
    """
    Categorize dependencies by type.

    Returns:
        {
            'repositories': [...],
            'services': [...],
            'controllers': [...]
        }
    """
    categorized = {
        'repositories': [],
        'services': [],
        'controllers': [],
        'others': []
    }

    for dep_name in dependencies:
        if 'Repository' in dep_name:
            categorized['repositories'].append(dep_name)
        elif 'Service' in dep_name:
            categorized['services'].append(dep_name)
        elif 'Controller' in dep_name:
            categorized['controllers'].append(dep_name)
        else:
            categorized['others'].append(dep_name)

    # Deduplicate each category
    for category in categorized:
        categorized[category] = dedupe(categorized[category])

    return categorized


def format_list(items: List[str], prefix: str = " - ") -> str:
    """Format list of items with prefix."""
    if not items:
        return f"{prefix}None"
    return "\n".join([f"{prefix}{i}" for i in items])


# ============================================================================
# Prompt Builder
# ============================================================================

def build_strict_prompt(
    component_name: str,
    file_path: str,
    code: str,
    dependencies: List[str],
    ontology: Dict
) -> str:
    """
    Build strict mode prompt with validation.

    Args:
        component_name: Name of component
        file_path: Path to source file
        code: Source code content
        dependencies: List of dependency class names
        ontology: Full ontology dict

    Returns:
        Formatted prompt string
    """
    # Detect stack
    stack = detect_stack(file_path)

    # Categorize dependencies
    categorized = categorize_dependencies(dependencies, ontology)

    # Validate inputs
    validate_prompt_inputs(stack, dependencies, component_name, code)

    # Determine architecture description
    if stack == 'nestjs-backend':
        arch_desc = """
### ✅ Correct Architecture (MANDATORY)
**Controller → Service → Repository → Database**

### Layer Rules
- Controllers handle HTTP only
- Services contain ALL business logic
- Repositories handle ALL database access
- Services MUST NOT access database directly
- Controllers MUST NOT access repositories
"""
    elif stack == 'react-frontend':
        arch_desc = """
### ✅ Correct Architecture (MANDATORY)
**Page → Component → Hook → Service/API**

### Layer Rules
- Pages route and compose components
- Components handle UI rendering
- Hooks manage state and side effects
- Services handle API calls
- Components MUST NOT call APIs directly
"""
    else:
        arch_desc = """
### Architecture
Follow the established patterns in the codebase.
"""

    # Build prompt
    prompt = f"""
{'='*70}
⚡ ONTOLOGY-GUIDED CODE ENHANCEMENT PROMPT (STRICT MODE)
{'='*70}

🔒 SYSTEM CONTEXT (STRICT — DO NOT VIOLATE)

You are working in a **{stack.replace('-', ' ').title()}** project.
{arch_desc}

---

🧠 ONTOLOGY CONTEXT

### 🎯 Target Component
**{component_name}**

### 📂 Target File
`{file_path}`

---

🔗 DEPENDENCIES (STRICT)

### Repositories:
{format_list(categorized['repositories'])}

### Services:
{format_list(categorized['services'])}

### Controllers:
{format_list(categorized['controllers'])}

### Others:
{format_list(categorized['others'])}

**Total Constructor Dependencies: {len(dependencies)}**

---

🚫 ANTI-HALLUCINATION RULES

### ❌ DO NOT CREATE
- New services
- New repositories
- New DTOs
- New modules
- New database models

### ❌ DO NOT MODIFY
- Controller routes
- Repository method signatures
- DTO contracts
- Public method signatures

### ❌ DO NOT INTRODUCE
- New libraries
- Direct database access (bypass repository)
- Breaking API changes

### ⚠️  UNCERTAINTY HANDLING (MANDATORY)

If ANY information is missing:

**DO NOT GUESS**

Add:
```typescript
// TODO: Missing information from context — cannot safely implement
// QUESTION: <what is missing?>
```

---

🧾 BUSINESS CONTEXT

**{component_name}** is responsible for:
- Business logic orchestration
- Coordinating repository calls
- Validating domain entities
- Managing transactional operations

---

📌 CURRENT IMPLEMENTATION

```typescript
{code if code else "// Source code not available"}
```

---

🎯 TASK

Enhance **{component_name}** with STRICT NON-BREAKING improvements:

### 1. Performance
- Eliminate redundant repository calls
- Avoid repeated existence checks (cache within request scope if safe)
- Optimize async execution (parallelize independent calls)

### 2. Structure
- Extract reusable validation methods
- Reduce method complexity (single responsibility)
- Improve readability and logical grouping

### 3. Type Safety
- Remove unsafe `any` / weak generics
- Strengthen return types
- Ensure strict null/undefined handling

### 4. Error Handling
- Standardize exception patterns
- Improve error handling consistency
- Ensure meaningful error messages

### 5. Maintainability
- Improve naming clarity
- Remove duplication
- Add minimal but meaningful comments

---

⚠️  HARD CONSTRAINTS

- ✅ Preserve ALL existing functionality
- ✅ Maintain ALL method signatures
- ✅ Maintain ALL API contracts
- ❌ DO NOT change behavior

---

📦 OUTPUT FORMAT (STRICT)

### 1. Updated Code
- FULL file output
- No omissions
- No pseudo-code

### 2. Explanation

Provide structured explanation:

**Changes Made:**
- List each change

**Why It Was Needed:**
- Rationale for each change

**Impact:**
- Performance improvement
- Maintainability improvement
- Safety improvement

### 3. Notes (if applicable)
- Assumptions (ONLY if explicitly marked)
- TODOs added due to missing context

---

✅ SUCCESS CRITERIA

- ✅ Compiles with ZERO TypeScript errors
- ✅ No new dependencies
- ✅ No architectural violations
- ✅ No behavior changes
- ✅ Cleaner, safer, more maintainable code

---

🚀 BEGIN TASK

{'='*70}
"""

    return prompt


# ============================================================================
# Main
# ============================================================================

def main():
    """Main entry point."""
    if len(sys.argv) < 3:
        print("Usage: python ontology_to_prompt.py <ontology.json> <ComponentName>")
        print("\nExample:")
        print("  python ontology_to_prompt.py code-intelligence/data/index.json SurgeonsService")
        sys.exit(1)

    ontology_file = sys.argv[1]
    component_name = sys.argv[2]

    # Load ontology
    print(f"Loading ontology from: {ontology_file}")
    ontology = load_ontology(ontology_file)
    print(f"✅ Loaded {len(ontology)} components\n")

    # Find component
    if component_name not in ontology:
        print(f"❌ Component '{component_name}' not found in ontology")

        # Find similar components
        similar = [name for name in ontology.keys() if component_name.lower() in name.lower()]
        if similar:
            print(f"\n💡 Did you mean one of these?")
            for name in similar[:5]:
                print(f"   - {name}")

        sys.exit(1)

    component = ontology[component_name]

    # Extract component details
    file_path = component.get('file_path', '')
    code = component.get('source_code', component.get('code', ''))

    # If code not in ontology, try reading from file system
    if not code and file_path:
        try:
            file_full_path = Path(file_path)
            if file_full_path.exists():
                code = file_full_path.read_text()
                print(f"✅ Loaded source code from file system")
            else:
                # Try relative to demo-repo
                alt_path = Path('demo-repo') / file_path
                if alt_path.exists():
                    code = alt_path.read_text()
                    print(f"✅ Loaded source code from: {alt_path}")
        except Exception as e:
            print(f"⚠️  Could not read source file: {e}")

    print(f"\nFound component: {component_name}")
    print(f"File: {file_path}")
    print(f"Code length: {len(code)} characters\n")

    # Extract dependencies
    dependencies = extract_constructor_dependencies(code)
    print(f"Constructor dependencies: {dependencies}\n")

    # Generate prompt
    try:
        prompt = build_strict_prompt(
            component_name=component_name,
            file_path=file_path,
            code=code,
            dependencies=dependencies,
            ontology=ontology
        )

        # Print prompt
        print(prompt)

        # Save to file
        output_file = f"/tmp/prompt_{component_name}.md"
        Path(output_file).write_text(prompt)
        print(f"\n✅ Prompt saved to: {output_file}")

    except ValueError as e:
        print(f"❌ Validation Error:\n{e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
