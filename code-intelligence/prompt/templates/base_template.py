"""
Base Prompt Template

Provides the foundation for all prompt templates.
Subclasses override specific sections to customize for different prompt types.
"""

from typing import Dict, List, Any
from abc import ABC, abstractmethod


class BasePromptTemplate(ABC):
    """
    Base class for all prompt templates.

    Subclasses should override specific section methods to customize
    the prompt for different use cases (enhancement, bug fix, etc.)
    """

    def generate(self, context: Dict[str, Any], description: str, title: str) -> str:
        """
        Generate the complete prompt.

        Args:
            context: Ontology context from OntologyContextBuilder
            description: User's description of what they want
            title: Title of the task

        Returns:
            Fully formatted prompt string
        """
        sections = []

        # Header
        sections.append(self._header(context, title))

        # System Context
        sections.append(self._system_context(context))

        # Ontology Constraints
        sections.append(self._ontology_constraints(context))

        # Dependency Graph
        sections.append(self._dependency_graph(context))

        # Anti-Hallucination Rules
        sections.append(self._anti_hallucination_rules(context))

        # Business Context
        sections.append(self._business_context(context, description))

        # Target Files
        sections.append(self._target_files(context))

        # Current Implementation
        if context.get('file_content') or context.get('file_snippet'):
            sections.append(self._current_implementation(context))

        # Task Definition (abstract - must be implemented by subclass)
        sections.append(self._task_definition(context, description))

        # Hard Rules
        sections.append(self._hard_rules(context))

        # Output Format
        sections.append(self._output_format())

        # Failure Handling
        sections.append(self._failure_handling())

        # Success Criteria
        sections.append(self._success_criteria(context))

        # Join all sections
        return "\n\n".join(filter(None, sections))

    def _header(self, context: Dict[str, Any], title: str) -> str:
        """Generate the header section."""
        return f"""{'='*70}
🎯 ONTOLOGY-GUIDED PROMPT
{'='*70}
TASK: {title}
{'='*70}"""

    def _system_context(self, context: Dict[str, Any]) -> str:
        """Generate system context section."""
        tech_stack = context.get('tech_stack', 'Unknown')
        dependency_chain = context.get('dependency_chain', 'Unknown flow')

        # GAP 2 FIX: Use tech_stack instead of layer for architecture rules
        arch_rules = self._get_architecture_rules(tech_stack)

        return f"""🔒 SYSTEM CONTEXT (STRICT — DO NOT VIOLATE)

You are working in a **{tech_stack}** component.

Follow this strict architecture:

**Layering (MANDATORY):**
{dependency_chain}

**Architecture Rules (MANDATORY):**
{arch_rules}"""

    def _get_architecture_rules(self, tech_stack: str) -> str:
        """
        GAP 2 FIX: Get architecture rules based on tech_stack, not layer.
        Prevents mixing frontend and backend rules.
        Supports: NestJS, ASP.NET Core, Go, Laravel, Express, Python backends + React, Flutter
        """
        stack_lower = tech_stack.lower()

        # C# / ASP.NET Core
        if 'aspnet-core' in stack_lower or 'csharp' in stack_lower:
            return """**ASP.NET Core Backend Architecture (STRICT):**
- **Controller** → handles HTTP requests, delegates to Service
- **Service** → contains ALL business logic, calls Repository
- **Repository** → handles ALL database access (Entity Framework)
- **NO direct DbContext access** from Services (use Repository)
- **NO Repository calls** from Controllers (use Service)
- DTOs for request/response (data transfer)
- Entities for database models
- Dependency Injection via constructor (IServiceCollection)"""

        # Go backend
        elif 'go-backend' in stack_lower or 'go-app' in stack_lower:
            return """**Go Backend Architecture (STRICT):**
- **Handler** → handles HTTP requests, delegates to Service
- **Service** → contains ALL business logic, calls Repository
- **Repository** → handles ALL database access
- **NO direct database access** from Handlers (use Service)
- Use structs for dependency injection (constructor pattern)
- Use interfaces for testability
- Structs for DTOs and models"""

        # PHP / Laravel
        elif 'laravel-backend' in stack_lower or 'php' in stack_lower:
            return """**Laravel Backend Architecture (STRICT):**
- **Controller** → handles HTTP requests, delegates to Service
- **Service** → contains ALL business logic, calls Repository
- **Repository/Model** → handles database access (Eloquent ORM)
- **NO direct database queries** from Controllers (use Service)
- Dependency Injection via constructor (Service Container)
- Request classes for validation
- Resources for API responses"""

        # JavaScript / Express
        elif 'express-backend' in stack_lower and 'javascript' in stack_lower:
            return """**Express.js Backend Architecture (STRICT):**
- **Router** → defines routes, delegates to Controller
- **Controller** → handles requests, calls Service
- **Service** → contains ALL business logic, calls Repository/Model
- **Repository/Model** → handles database access
- **NO direct database access** from Routes (use Service)
- Middleware for auth, validation, error handling
- DTOs/Schemas for validation"""

        # Python backends (FastAPI, Flask, Django)
        elif 'python-backend' in stack_lower or 'python-app' in stack_lower:
            return """**Python Backend Architecture (STRICT):**
- **Router/View** → handles HTTP requests, delegates to Service
- **Service** → contains ALL business logic, calls Repository
- **Repository/Model** → handles database access (SQLAlchemy/ORM)
- **NO direct database access** from Routes (use Service)
- Dependency Injection via FastAPI Depends() or constructor
- Pydantic models for request/response validation
- ORM models for database"""

        # TypeScript NestJS (existing)
        elif 'nestjs-backend' in stack_lower:
            return """**NestJS Backend Architecture (STRICT):**
- **Controller** → handles HTTP, delegates to Service
- **Service** → contains ALL business logic, calls Repositories
- **Repository** → handles ALL database access
- **NO direct database access** from Services (use Repository)
- **NO Repository calls** from Controllers (use Service)
- DTOs for request/response validation
- Entities for database models"""

        # TypeScript Express
        elif 'express-backend' in stack_lower and 'typescript' in stack_lower:
            return """**Express.js (TypeScript) Backend Architecture (STRICT):**
- **Router** → defines routes, delegates to Controller
- **Controller** → handles requests, calls Service
- **Service** → contains ALL business logic, calls Repository
- **Repository** → handles database access
- **NO direct database access** from Routes (use Service)
- TypeScript interfaces for type safety
- DTOs for validation"""

        # React Frontend (existing)
        elif 'react-frontend' in stack_lower or 'react-app' in stack_lower:
            return """**React Frontend Architecture (STRICT):**
- **Pages** → route handling, composition
- **Components** → presentational UI
- **Hooks** → state management, side effects
- **Services** → API calls (centralized)
- **NO direct API calls** from Components (use hooks/services)
- Props for component communication"""

        # Flutter Mobile (existing)
        elif 'flutter-mobile' in stack_lower or 'dart-app' in stack_lower:
            return """**Flutter Mobile Architecture (STRICT):**
- **Screens** → route handling, composition
- **Widgets** → presentational UI
- **Providers/Bloc** → state management
- **Services** → API calls, business logic
- **NO direct API calls** from Widgets (use Providers)"""

        # Generic fallback
        else:
            return """**General Architecture:**
- Follow existing patterns in codebase
- Maintain separation of concerns
- Keep dependencies minimal and explicit"""

    def _ontology_constraints(self, context: Dict[str, Any]) -> str:
        """
        GAP 1 FIX: Generate ontology constraints with constructor dependencies.
        Explicitly lists ALL dependencies found in constructor.
        """
        component = context.get('component', {})
        related_dtos = context.get('related_dtos', [])
        related_entities = context.get('related_entities', [])
        related_repositories = context.get('related_repositories', [])
        related_services = context.get('related_services', [])
        related_controllers = context.get('related_controllers', [])

        # GAP 1 FIX: Get constructor dependencies
        constructor_deps_categorized = context.get('constructor_dependencies_categorized', {})

        sections = []

        sections.append("🧠 ONTOLOGY CONSTRAINTS (SOURCE OF TRUTH)")
        sections.append("")
        sections.append("**Target Component:**")
        sections.append(f"- {component.get('name')} ({component.get('type')})")

        # GAP 1 FIX: Add constructor-injected dependencies FIRST (highest priority)
        if constructor_deps_categorized:
            sections.append("\n**Constructor-Injected Dependencies (VERIFIED FROM CODE):**")

            if constructor_deps_categorized.get('repositories'):
                sections.append("\nRepositories:")
                for repo in constructor_deps_categorized['repositories']:
                    sections.append(f"  ✅ {repo}")

            if constructor_deps_categorized.get('services'):
                sections.append("\nServices:")
                for svc in constructor_deps_categorized['services']:
                    sections.append(f"  ✅ {svc}")

            if constructor_deps_categorized.get('others'):
                sections.append("\nOther Dependencies:")
                for other in constructor_deps_categorized['others']:
                    sections.append(f"  ✅ {other}")

        # Related components from ontology graph
        sections.append("\n**Related Components From Ontology:**")

        if related_services:
            sections.append("\nServices:")
            for svc in related_services[:5]:
                sections.append(f"  - {svc.get('name')}")

        if related_repositories:
            sections.append("\nRepositories:")
            for repo in related_repositories[:5]:
                sections.append(f"  - {repo.get('name')}")

        if related_controllers:
            sections.append("\nControllers:")
            for ctrl in related_controllers[:5]:
                sections.append(f"  - {ctrl.get('name')}")

        if related_dtos:
            sections.append("\nDTOs (STRICT USAGE ONLY):")
            for dto in related_dtos[:10]:
                sections.append(f"  - {dto.get('name')}")

        if related_entities:
            sections.append("\nEntities:")
            for entity in related_entities[:10]:
                sections.append(f"  - {entity.get('name')}")

        return "\n".join(sections)

    def _dependency_graph(self, context: Dict[str, Any]) -> str:
        """Generate dependency graph section."""
        dependencies = context.get('dependencies', [])
        dependents = context.get('dependents', [])
        dependency_chain = context.get('dependency_chain', 'Unknown')

        sections = []
        sections.append("🔗 ALLOWED DEPENDENCY GRAPH")
        sections.append("")
        sections.append(f"**Architectural Flow:**\n{dependency_chain}")

        if dependencies:
            sections.append("\n**This component depends on:**")
            for dep in dependencies[:10]:
                dep_type = dep.get('type', 'unknown')
                dep_name = dep.get('name', 'unknown')
                sections.append(f"  - {dep_name} ({dep_type})")

        if dependents:
            sections.append("\n**Components that depend on this:**")
            for dep in dependents[:10]:
                dep_type = dep.get('type', 'unknown')
                dep_name = dep.get('name', 'unknown')
                sections.append(f"  - {dep_name} ({dep_type})")

        return "\n".join(sections)

    def _anti_hallucination_rules(self, context: Dict[str, Any]) -> str:
        """
        GAP 4, GAP 5 FIX: Enhanced anti-hallucination rules.
        """
        # GAP 5 FIX: Get constructor dependencies for strict enforcement
        constructor_deps = context.get('constructor_dependencies', [])

        rules = []
        rules.append("🚫 FORBIDDEN (ANTI-HALLUCINATION RULES)")
        rules.append("")

        # GAP 5 FIX: Explicit "DO NOT CALL" rule for unlisted dependencies
        if constructor_deps:
            rules.append("**DEPENDENCY ENFORCEMENT (STRICT):**")
            rules.append("ONLY call these dependencies (from constructor):")
            for dep in constructor_deps:
                rules.append(f"  ✅ {dep}")
            rules.append("")
            rules.append("❌ DO NOT call any service/repository NOT listed above")
            rules.append("❌ DO NOT invent new repository methods")
            rules.append("❌ DO NOT create new service instances")
            rules.append("")

        rules.append("**DO NOT create new:**")
        rules.append("  - Services (use existing ones from ontology)")
        rules.append("  - Repositories (use existing ones from ontology)")
        rules.append("  - DTOs (use existing ones, or justify additions)")
        rules.append("  - Modules (use existing architecture)")
        rules.append("  - Database schemas (use existing entities)")
        rules.append("")

        rules.append("**DO NOT modify:**")
        rules.append("  - Controller routes (unless explicitly requested)")
        rules.append("  - Repository method signatures (maintain contracts)")
        rules.append("  - Database schema structure")
        rules.append("  - Existing API contracts")
        rules.append("  - Public interfaces")
        rules.append("")

        rules.append("**DO NOT introduce:**")
        rules.append("  - New libraries (unless justified and approved)")
        rules.append("  - New database queries outside repository layer")
        rules.append("  - Breaking changes to existing APIs")
        rules.append("  - Unused or speculative code")
        rules.append("")

        # GAP 4 FIX: Code completion rule
        rules.append("**CODE COMPLETION RULE (CRITICAL):**")
        rules.append("  ❌ DO NOT complete truncated code beyond visible context")
        rules.append("  ❌ DO NOT guess implementation of methods not shown")
        rules.append("  ❌ If code is cut off → add comment: // TODO: Implementation needed")
        rules.append("  ✅ ONLY modify code you can see in full")
        rules.append("")

        rules.append("**DO NOT assume missing fields or behaviors:**")
        rules.append("  - If something is unclear → ADD A COMMENT, DO NOT GUESS")
        rules.append("  - If data is missing from context → ASK, do not fabricate")
        rules.append("  - If you're uncertain → EXPLAIN THE UNCERTAINTY, don't hide it")

        return "\n".join(rules)

    def _business_context(self, context: Dict[str, Any], description: str) -> str:
        """Generate business context section."""
        component = context.get('component', {})
        component_name = component.get('name', 'Unknown')
        component_type = component.get('type', 'unknown')

        return f"""🧾 BUSINESS CONTEXT

**Component:** {component_name} ({component_type})

**Purpose:**
{description}

**Responsibilities:**
{self._infer_component_responsibilities(context)}"""

    def _infer_component_responsibilities(self, context: Dict[str, Any]) -> str:
        """Infer component responsibilities from context."""
        component_type = context.get('component_type', '').lower()
        component_name = context.get('component', {}).get('name', '')

        if 'service' in component_type:
            return f"""- Business logic implementation
- Orchestrating data operations via repositories
- Data transformation and validation
- Error handling and business rule enforcement"""

        elif 'controller' in component_type:
            return f"""- Handling HTTP requests
- Input validation (using DTOs)
- Calling appropriate services
- Returning appropriate responses"""

        elif 'repository' in component_type:
            return f"""- Database operations (CRUD)
- Query construction
- Data mapping (database ↔ entities)
- Transaction management"""

        elif 'dto' in component_type:
            return f"""- Data transfer between layers
- Input validation schemas
- Type safety for API contracts"""

        else:
            return "- Responsibilities inferred from component type and context"

    def _target_files(self, context: Dict[str, Any]) -> str:
        """Generate target files section."""
        file_path = context.get('file_path', 'Unknown')

        return f"""📂 TARGET FILE(S)

**Primary File:** `{file_path}`"""

    def _current_implementation(self, context: Dict[str, Any]) -> str:
        """Generate current implementation section."""
        component_name = context.get('component', {}).get('name', 'Component')
        file_path = context.get('file_path', 'unknown')
        file_snippet = context.get('file_snippet')
        file_content = context.get('file_content')

        sections = []
        sections.append("📌 CURRENT IMPLEMENTATION")
        sections.append("")
        sections.append(f"### {component_name} (`{file_path}`)")
        sections.append("```")

        # Use snippet if available (shorter), otherwise full content (truncated)
        if file_snippet:
            sections.append(file_snippet)
        elif file_content:
            # Truncate if too long
            lines = file_content.split('\n')
            if len(lines) > 100:
                sections.append('\n'.join(lines[:100]))
                sections.append("\n... (truncated)")
            else:
                sections.append(file_content)
        else:
            sections.append("(Source code not available)")

        sections.append("```")

        return "\n".join(sections)

    @abstractmethod
    def _task_definition(self, context: Dict[str, Any], description: str) -> str:
        """
        Generate task definition section.

        MUST be implemented by subclasses.
        This is where each template type defines its specific requirements.
        """
        pass

    def _hard_rules(self, context: Dict[str, Any]) -> str:
        """
        GAP 3, GAP 6 FIX: Enhanced hard rules with allowed operations and diff awareness.
        """
        return """⚠️  HARD RULES

**Use ONLY existing:**
  - DTOs (from ontology)
  - Repository methods (from ontology)
  - Service methods (from ontology)

**Maintain ALL:**
  - Existing functionality
  - API contracts
  - Method signatures
  - Error handling patterns

**DO NOT:**
  - Change method signatures without justification
  - Break backward compatibility
  - Remove existing functionality
  - Introduce breaking changes

---

## GAP 3 FIX: ALLOWED OPERATIONS (EXPLICIT BOUNDARY)

**✅ YOU MAY:**
  - Refactor private methods (internal implementation)
  - Extract complex logic into helper functions
  - Add type annotations and improve type safety
  - Optimize performance (without changing behavior)
  - Improve error messages
  - Add defensive programming checks
  - Restructure code for readability
  - Remove code duplication
  - Simplify conditional logic

**❌ YOU MAY NOT:**
  - Change public method signatures (without justification)
  - Modify constructor parameters
  - Change return types of public methods
  - Remove existing functionality
  - Add new public methods (without justification)
  - Change error handling strategy (can improve messages only)

---

## GAP 6 FIX: DIFF AWARENESS (MINIMAL CHANGES RULE)

**CRITICAL: Minimize Code Changes**

  - ✅ ONLY modify lines that need improvement
  - ✅ Preserve surrounding code exactly as-is
  - ✅ Make surgical, targeted changes
  - ❌ DO NOT rewrite entire methods unnecessarily
  - ❌ DO NOT reformat code "for consistency"
  - ❌ DO NOT add comments to unchanged code

**Example:**
```typescript
// GOOD (surgical change):
// Changed only the filter logic, kept everything else
const active = users.filter(u => u.isActive && !u.deleted)

// BAD (unnecessary rewrite):
// Rewrote entire method just to change one line
```

**Rule:** If a line works correctly, leave it untouched."""

    def _output_format(self) -> str:
        """Generate output format section."""
        return """📦 OUTPUT FORMAT (STRICT)

**1. Updated Code**
   - Provide FULL updated file(s)
   - No partial snippets
   - Include all imports and dependencies

**2. Explanation**
   - Structured explanation with:
     - What changed
     - Why it was needed
     - Impact (performance/maintainability/safety)

**3. Migration Notes** (if applicable)
   - Breaking changes (if any - with justification)
   - Required updates in other files
   - Testing recommendations"""

    def _failure_handling(self) -> str:
        """Generate failure handling section."""
        return """🧠 FAILURE HANDLING

If any required information is missing:

**DO NOT hallucinate**

Insert a comment in code:
```
// TODO: Missing information from context — cannot safely implement
// QUESTION: [Specific question about missing information]
```

**DO NOT guess:**
- Method signatures
- DTO structures
- Database schemas
- Business logic

**DO ask:**
- Clarifying questions
- About missing dependencies
- About ambiguous requirements"""

    def _success_criteria(self, context: Dict[str, Any]) -> str:
        """Generate success criteria section."""
        component_type = context.get('component_type', 'component')

        return f"""✅ SUCCESS CRITERIA

**Code Quality:**
  - Compiles without TypeScript/type errors
  - Follows existing code style and patterns
  - No linting errors

**Architecture:**
  - Follows dependency chain: {context.get('dependency_chain', 'N/A')}
  - No architectural violations
  - Proper layer separation maintained

**Functionality:**
  - All existing functionality preserved
  - No breaking changes (unless justified)
  - Error handling maintained/improved

**Dependencies:**
  - No new dependencies introduced (unless justified)
  - All imports valid and necessary
  - Uses only existing ontology components

🚀 BEGIN TASK"""
