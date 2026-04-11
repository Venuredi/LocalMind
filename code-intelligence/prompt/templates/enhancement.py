"""
Enhancement Prompt Template

Generates prompts for code enhancement tasks:
- Performance improvements
- Code quality improvements
- Structure improvements
- Type safety improvements
"""

from typing import Dict, Any
from .base_template import BasePromptTemplate


class EnhancementTemplate(BasePromptTemplate):
    """
    Template for enhancement prompts.

    Focuses on improving existing code without changing functionality.
    """

    def _header(self, context: Dict[str, Any], title: str) -> str:
        """Generate enhancement-specific header."""
        return f"""{'='*70}
⚡ ONTOLOGY-GUIDED CODE ENHANCEMENT PROMPT
{'='*70}
ENHANCEMENT: {title}
{'='*70}"""

    def _task_definition(self, context: Dict[str, Any], description: str) -> str:
        """
        Generate enhancement-specific task definition.

        Focuses on:
        - Performance
        - Structure
        - Type safety
        - Maintainability
        """
        component = context.get('component', {})
        component_name = component.get('name', 'Component')
        component_type = component.get('component_type', 'component')

        return f"""🎯 TASK: ENHANCE {component_name}

## What to Enhance
{description}

**Target Component:** `{component_name}` ({component_type})

## Enhancement Goals

### 1. Performance Improvements
- Reduce redundant operations
- Optimize database queries (if applicable)
- Add strategic caching/memoization
- Eliminate unnecessary computations
- Improve algorithm efficiency

### 2. Code Structure
- Extract reusable logic into helper methods
- Reduce method complexity (keep methods focused)
- Improve code readability
- Follow DRY (Don't Repeat Yourself)
- Clear separation of concerns

### 3. Type Safety
- Strengthen TypeScript types
- Eliminate `any` usage where possible
- Add proper generic types
- Ensure strict null checking
- Improve DTO usage

### 4. Error Handling
- Standardize error handling patterns
- Improve error messages
- Add defensive programming checks
- Handle edge cases gracefully
- Prevent error leakage

### 5. Maintainability
- Improve variable/method naming
- Add strategic comments (only where code isn't self-documenting)
- Simplify complex logic
- Make code more testable
- Reduce coupling

## Specific Enhancement Tasks
{self._generate_enhancement_tasks(context, description)}

## Constraints
- **DO NOT** change functionality
- **DO NOT** modify API contracts
- **DO NOT** break backward compatibility
- **MAINTAIN** all existing behavior
- **PRESERVE** all existing tests

## Expected Improvements
After enhancement, the code should:
- ✅ Be more performant
- ✅ Be easier to read and understand
- ✅ Be easier to maintain and extend
- ✅ Have better error handling
- ✅ Be more type-safe
- ✅ Follow best practices"""

    def _generate_enhancement_tasks(self, context: Dict[str, Any], description: str) -> str:
        """Generate specific enhancement tasks based on component type."""
        component_type = context.get('component_type', '').lower()

        if 'service' in component_type:
            return self._service_enhancement_tasks(context)
        elif 'controller' in component_type:
            return self._controller_enhancement_tasks(context)
        elif 'repository' in component_type:
            return self._repository_enhancement_tasks(context)
        else:
            return self._generic_enhancement_tasks(context)

    def _service_enhancement_tasks(self, context: Dict[str, Any]) -> str:
        """Enhancement tasks specific to services."""
        return """**Service-Specific Enhancements:**

1. **Method Optimization:**
   - Review method complexity
   - Extract common logic into private methods
   - Ensure each method has single responsibility

2. **Dependency Management:**
   - Ensure dependencies are properly injected
   - Review repository usage patterns
   - Check for redundant service calls

3. **Data Transformation:**
   - Optimize DTO conversions
   - Reduce unnecessary data mapping
   - Improve data validation

4. **Error Handling:**
   - Standardize error responses
   - Improve Prisma/database error mapping
   - Add specific error types where helpful

5. **Business Logic:**
   - Clarify complex business rules
   - Add validation where missing
   - Improve method documentation (if complex)"""

    def _controller_enhancement_tasks(self, context: Dict[str, Any]) -> str:
        """Enhancement tasks specific to controllers."""
        return """**Controller-Specific Enhancements:**

1. **Route Handlers:**
   - Ensure proper HTTP status codes
   - Validate request DTOs strictly
   - Return appropriate response DTOs

2. **Input Validation:**
   - Use DTOs for all inputs
   - Add validation pipes/decorators
   - Handle invalid input gracefully

3. **Response Formatting:**
   - Consistent response structure
   - Proper error responses
   - Include appropriate metadata

4. **Documentation:**
   - Add Swagger/OpenAPI decorators
   - Document request/response schemas
   - Add example responses

5. **Security:**
   - Ensure proper authentication/authorization
   - Validate all user inputs
   - Prevent injection attacks"""

    def _repository_enhancement_tasks(self, context: Dict[str, Any]) -> str:
        """Enhancement tasks specific to repositories."""
        return """**Repository-Specific Enhancements:**

1. **Query Optimization:**
   - Review query efficiency
   - Add proper indexes (document)
   - Use select to reduce data transfer
   - Optimize joins and relationships

2. **Error Handling:**
   - Handle database errors gracefully
   - Map Prisma errors to domain errors
   - Add transaction support where needed

3. **Data Mapping:**
   - Clean entity ↔ DTO conversion
   - Handle null/undefined properly
   - Ensure type safety

4. **Method Design:**
   - Keep methods focused and simple
   - Reuse query fragments
   - Add pagination where appropriate"""

    def _generic_enhancement_tasks(self, context: Dict[str, Any]) -> str:
        """Generic enhancement tasks for unknown component types."""
        return """**General Enhancements:**

1. **Code Quality:**
   - Improve readability
   - Reduce complexity
   - Follow coding standards

2. **Type Safety:**
   - Strengthen types
   - Remove unsafe casts
   - Add proper generics

3. **Performance:**
   - Identify bottlenecks
   - Optimize critical paths
   - Reduce unnecessary operations

4. **Maintainability:**
   - Clear naming
   - Logical structure
   - Proper error handling"""

    def _success_criteria(self, context: Dict[str, Any]) -> str:
        """Enhancement-specific success criteria."""
        base_criteria = super()._success_criteria(context)

        enhancement_criteria = """

**Enhancement-Specific Success:**
  - Performance improved (measurably or architecturally)
  - Code complexity reduced
  - Type safety strengthened
  - Error handling improved
  - Code is more maintainable
  - All functionality preserved
  - No breaking changes introduced"""

        return base_criteria + enhancement_criteria
