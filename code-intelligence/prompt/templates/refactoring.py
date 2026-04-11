"""
Refactoring Prompt Template

Generates prompts for code refactoring tasks:
- Restructure code without changing functionality
- Improve code quality and maintainability
- Extract reusable components
- Reduce complexity
"""

from typing import Dict, Any
from .base_template import BasePromptTemplate


class RefactoringTemplate(BasePromptTemplate):
    """
    Template for refactoring prompts.

    Focuses on improving code structure without changing behavior.
    """

    def _header(self, context: Dict[str, Any], title: str) -> str:
        """Generate refactoring-specific header."""
        return f"""{'='*70}
♻️  ONTOLOGY-GUIDED REFACTORING PROMPT
{{'='*70}}
REFACTORING: {title}
{'='*70}"""

    def _task_definition(self, context: Dict[str, Any], description: str) -> str:
        """
        Generate refactoring-specific task definition.

        Focuses on:
        - Improving structure
        - Maintaining exact functionality
        - No behavior changes
        - Better maintainability
        """
        component = context.get('component', {})
        component_name = component.get('name', 'Component')
        component_type = component.get('component_type', 'component')

        return f"""🎯 TASK: REFACTOR {component_name}

## Refactoring Goal
{description}

**Target Component:** `{component_name}` ({component_type})
**File:** `{{context.get('file_path', 'unknown')}}`

## Refactoring Principles

### 🔒 CRITICAL RULE: PRESERVE FUNCTIONALITY
**The #1 rule of refactoring: Don't change behavior!**

- ✅ Change HOW code works internally
- ❌ DON'T change WHAT code does externally
- ✅ Improve structure, readability, maintainability
- ❌ DON'T add features, fix bugs, or change logic

### Refactoring Approach

#### Phase 1: Analysis

1. **Identify Code Smells**
   - Long methods (> 50 lines)
   - Duplicate code
   - Complex conditionals
   - Deep nesting
   - Poor naming
   - Tight coupling
   - Low cohesion

2. **Understand Current Behavior**
   - What does this code do?
   - What are its inputs/outputs?
   - What are the side effects?
   - What assumptions does it make?

3. **Plan Refactoring**
   - What patterns to apply?
   - What to extract?
   - What to rename?
   - What dependencies to break?

#### Phase 2: Refactoring Techniques

1. **Extract Method/Function**
   - Break long methods into smaller ones
   - Each method does one thing
   - Clear, descriptive names

2. **Extract Class/Module**
   - Separate responsibilities
   - Create cohesive units
   - Reduce coupling

3. **Rename**
   - Meaningful variable names
   - Descriptive method names
   - Clear class names

4. **Simplify Conditionals**
   - Extract complex conditions to methods
   - Use early returns
   - Replace nested ifs with guard clauses

5. **Remove Duplication**
   - Extract common code
   - Create reusable functions
   - Use composition

6. **Improve Data Structures**
   - Use appropriate collections
   - Group related data
   - Use objects instead of primitives

#### Phase 3: Validation

1. **Verify Behavior**
   - All existing tests still pass
   - API contracts unchanged
   - Same inputs → Same outputs
   - Same side effects

2. **Safety Checks**
   - No new dependencies
   - No API changes
   - No performance degradation
   - No new errors

## Refactoring Requirements

### MANDATORY:
- ✅ PRESERVE all existing functionality
- ✅ Maintain ALL API contracts
- ✅ Keep the same behavior
- ✅ All existing tests must still pass
- ✅ Improve code quality/readability
- ✅ Reduce complexity
- ✅ Follow DRY, SOLID principles

### FORBIDDEN:
- ❌ Changing functionality
- ❌ Adding new features
- ❌ Fixing bugs (do that separately!)
- ❌ Breaking API contracts
- ❌ Changing method signatures (public APIs)
- ❌ Modifying behavior

## Common Refactoring Patterns

### 1. Extract Method
**Before:**
```typescript
async processData(data: any[]) {{{{
  // 50 lines of code doing multiple things
  const validated = data.filter(d => d.id && d.name);
  const transformed = validated.map(d => ({{{{...}}}}));
  const saved = await this.repository.save(transformed);
  return saved;
}}}}
```

**After:**
```typescript
async processData(data: any[]) {{{{
  const validated = this.validateData(data);
  const transformed = this.transformData(validated);
  return await this.saveData(transformed);
}}}}

private validateData(data: any[]) {{{{
  return data.filter(d => d.id && d.name);
}}}}

private transformData(data: any[]) {{{{
  return data.map(d => ({{{{...}}}}));
}}}}

private async saveData(data: any[]) {{{{
  return await this.repository.save(data);
}}}}
```

### 2. Replace Nested Conditionals
**Before:**
```typescript
if (user) {{{{
  if (user.isActive) {{{{
    if (user.hasPermission('read')) {{{{
      return data;
    }}}}
  }}}}
}}}}
return null;
```

**After:**
```typescript
if (!user) return null;
if (!user.isActive) return null;
if (!user.hasPermission('read')) return null;
return data;
```

### 3. Extract Complex Condition
**Before:**
```typescript
if (user.age >= 18 && user.hasLicense && !user.suspended && user.points < 12) {{{{
  // allow driving
}}}}
```

**After:**
```typescript
if (this.canDrive(user)) {{{{
  // allow driving
}}}}

private canDrive(user: User): boolean {{{{
  return user.age >= 18
    && user.hasLicense
    && !user.suspended
    && user.points < 12;
}}}}
```

## Component-Specific Refactoring
{self._generate_refactoring_guidance(context)}

## Deliverables

1. **Refactored Code**
   - Cleaner structure
   - Better organization
   - Improved readability
   - Reduced complexity

2. **Explanation**
   - What was refactored
   - Why it was refactored
   - What patterns were applied
   - How it improves the code

3. **Behavior Verification**
   - Confirm no functionality changed
   - List what remained the same
   - Identify any risk areas

4. **Before/After Comparison**
   - Show key changes
   - Highlight improvements
   - Explain benefits"""

    def _generate_refactoring_guidance(self, context: Dict[str, Any]) -> str:
        """Generate component-specific refactoring guidance."""
        component_type = context.get('component_type', '').lower()

        if 'service' in component_type:
            return self._service_refactoring_guidance()
        elif 'controller' in component_type:
            return self._controller_refactoring_guidance()
        elif 'repository' in component_type:
            return self._repository_refactoring_guidance()
        else:
            return self._generic_refactoring_guidance()

    def _service_refactoring_guidance(self) -> str:
        """Refactoring guidance for services."""
        return """
**Service Refactoring Opportunities:**

1. **Extract Business Logic:**
   - Complex calculations → private methods
   - Validation logic → validator classes
   - Transformation logic → mapper functions

2. **Reduce Method Length:**
   - Break 100+ line methods into 10-20 line methods
   - Each method has single responsibility
   - Clear method names

3. **Improve Data Flow:**
   - Remove intermediate variables
   - Use method chaining where appropriate
   - Clear input → process → output flow

4. **Better Error Handling:**
   - Extract error mapping logic
   - Consistent error handling patterns
   - Centralized error creation"""

    def _controller_refactoring_guidance(self) -> str:
        """Refactoring guidance for controllers."""
        return """
**Controller Refactoring Opportunities:**

1. **Thin Controllers:**
   - Move business logic to services
   - Controllers only orchestrate
   - No complex logic in controllers

2. **Extract Common Patterns:**
   - Common response formatting
   - Repeated validation logic
   - Error handling patterns

3. **Better Route Organization:**
   - Group related endpoints
   - Consistent naming
   - Clear resource hierarchy

4. **Decorators:**
   - Extract repeated decorators to constants
   - Use custom decorators for common patterns"""

    def _repository_refactoring_guidance(self) -> str:
        """Refactoring guidance for repositories."""
        return """
**Repository Refactoring Opportunities:**

1. **Query Reuse:**
   - Extract common query fragments
   - Build queries from reusable parts
   - Reduce duplication

2. **Better Abstraction:**
   - Generic find methods
   - Reusable filters
   - Common sorting/pagination

3. **Clearer Method Names:**
   - Descriptive query methods
   - Consistent naming patterns
   - Self-documenting code

4. **Error Handling:**
   - Centralize database error mapping
   - Consistent error responses
   - Better error messages"""

    def _generic_refactoring_guidance(self) -> str:
        """Generic refactoring guidance."""
        return """
**General Refactoring Opportunities:**

1. **Code Organization:**
   - Group related code
   - Logical file structure
   - Clear separation of concerns

2. **Naming:**
   - Descriptive names
   - Consistent conventions
   - Self-documenting code

3. **Complexity:**
   - Reduce nesting
   - Simplify logic
   - Extract complex parts

4. **Duplication:**
   - DRY principle
   - Extract common code
   - Create reusable functions"""

    def _success_criteria(self, context: Dict[str, Any]) -> str:
        """Refactoring-specific success criteria."""
        base_criteria = super()._success_criteria(context)

        refactoring_criteria = """

**Refactoring-Specific Success:**
  - Code functionality UNCHANGED
  - All existing tests pass
  - Code complexity reduced
  - Readability improved
  - Duplication eliminated
  - Better structure/organization
  - No new bugs introduced
  - No breaking changes
  - Performance maintained or improved"""

        return base_criteria + refactoring_criteria
