"""
Bug Fix Prompt Template

Generates prompts for bug fix tasks:
- Fix bugs while maintaining functionality
- Root cause analysis
- Prevent similar bugs
- Add defensive checks
"""

from typing import Dict, Any
from .base_template import BasePromptTemplate


class BugFixTemplate(BasePromptTemplate):
    """
    Template for bug fix prompts.

    Focuses on fixing bugs without breaking existing functionality.
    """

    def _header(self, context: Dict[str, Any], title: str) -> str:
        """Generate bug-fix-specific header."""
        return f"""{'='*70}
🐛 ONTOLOGY-GUIDED BUG FIX PROMPT
{{'='*70}}
BUG FIX: {title}
{'='*70}"""

    def _task_definition(self, context: Dict[str, Any], description: str) -> str:
        """
        Generate bug-fix-specific task definition.

        Focuses on:
        - Root cause identification
        - Minimal fix
        - Maintaining existing functionality
        - Adding defensive checks
        """
        component = context.get('component', {})
        component_name = component.get('name', 'Component')
        component_type = component.get('component_type', 'component')

        return f"""🎯 TASK: FIX BUG IN {component_name}

## Bug Description
{description}

**Target Component:** `{component_name}` ({component_type})
**File:** `{{context.get('file_path', 'unknown')}}`

## Bug Fix Approach

### Step 1: Root Cause Analysis
1. **Read Current Implementation**
   - Understand the code flow
   - Identify where the bug occurs
   - Trace the execution path

2. **Identify Root Cause**
   - What is causing the bug?
   - Is it a logic error, edge case, race condition, or data issue?
   - Document your findings in a comment

3. **Understand Impact**
   - What functionality is affected?
   - Are there related areas that might have similar issues?
   - Check for similar patterns elsewhere

### Step 2: Minimal Fix
1. **Design the Fix**
   - Propose the minimal change needed
   - Avoid over-engineering
   - Focus on the root cause, not symptoms

2. **Implementation Constraints**
   - ✅ Fix ONLY the bug (no feature additions)
   - ✅ Maintain ALL existing functionality
   - ✅ Keep changes as small as possible
   - ✅ Don't refactor unrelated code
   - ✅ Preserve API contracts

3. **Defensive Programming**
   - Add null/undefined checks if needed
   - Add validation for edge cases
   - Add error handling where missing
   - Consider adding assertions

### Step 3: Verification
1. **Testing Strategy**
   - How to verify the fix works?
   - What test cases should be added?
   - What edge cases need testing?

2. **Regression Prevention**
   - Will this change break anything else?
   - Are there related areas to check?
   - Should we add regression tests?

## Bug Fix Requirements

### MANDATORY:
- ✅ Fix the root cause (not just symptoms)
- ✅ Maintain ALL existing functionality
- ✅ No breaking changes to API contracts
- ✅ Add defensive checks for edge cases
- ✅ Explain WHY the bug occurred
- ✅ Minimal code changes (surgical fix)

### FORBIDDEN:
- ❌ Feature additions or enhancements
- ❌ Unrelated refactoring
- ❌ Changing API signatures (unless absolutely necessary)
- ❌ Guessing at the fix (root cause analysis first!)
- ❌ Breaking changes

## Expected Deliverables

1. **Root Cause Explanation**
   - What caused the bug?
   - Why did it occur?
   - Why wasn't it caught earlier?

2. **Fix Implementation**
   - Minimal code changes
   - Focused on root cause
   - Includes defensive checks

3. **Testing Recommendations**
   - Unit tests to add
   - Integration tests needed
   - Manual testing steps

4. **Prevention Measures**
   - How to prevent similar bugs?
   - Should we add validation elsewhere?
   - Are there patterns to avoid?

## Component-Specific Bug Fix Guidance
{self._generate_bug_fix_guidance(context)}"""

    def _generate_bug_fix_guidance(self, context: Dict[str, Any]) -> str:
        """Generate component-specific bug fix guidance."""
        component_type = context.get('component_type', '').lower()

        if 'service' in component_type:
            return self._service_bug_fix_guidance()
        elif 'controller' in component_type:
            return self._controller_bug_fix_guidance()
        elif 'repository' in component_type:
            return self._repository_bug_fix_guidance()
        else:
            return self._generic_bug_fix_guidance()

    def _service_bug_fix_guidance(self) -> str:
        """Bug fix guidance for services."""
        return """
**Service-Specific Bug Fix Checklist:**

1. **Business Logic Errors:**
   - Check calculation errors
   - Verify conditional logic
   - Review data transformations
   - Validate business rules

2. **Data Handling:**
   - Null/undefined handling
   - Type coercion issues
   - DTO mapping errors
   - Data validation gaps

3. **Error Handling:**
   - Unhandled exceptions
   - Incorrect error types thrown
   - Missing try-catch blocks
   - Poor error messages

4. **Dependency Issues:**
   - Repository calls failing
   - External service errors
   - Dependency injection problems
   - Circular dependencies

5. **Concurrency:**
   - Race conditions
   - Async/await issues
   - Promise handling
   - Transaction management"""

    def _controller_bug_fix_guidance(self) -> str:
        """Bug fix guidance for controllers."""
        return """
**Controller-Specific Bug Fix Checklist:**

1. **Request Handling:**
   - Incorrect HTTP methods
   - Route parameter parsing
   - Query string handling
   - Body parsing issues

2. **Validation:**
   - Missing input validation
   - Incorrect DTO usage
   - Type validation errors
   - Business rule validation

3. **Response:**
   - Wrong status codes
   - Incorrect response format
   - Missing error responses
   - Serialization issues

4. **Security:**
   - Authentication bypass
   - Authorization gaps
   - Input sanitization missing
   - CORS issues

5. **Error Handling:**
   - Unhandled exceptions
   - Poor error responses
   - Stack trace leakage
   - Missing error logging"""

    def _repository_bug_fix_guidance(self) -> str:
        """Bug fix guidance for repositories."""
        return """
**Repository-Specific Bug Fix Checklist:**

1. **Query Issues:**
   - Incorrect WHERE clauses
   - JOIN errors
   - Missing indexes causing slowness
   - N+1 query problems

2. **Data Integrity:**
   - Transaction boundaries wrong
   - Constraint violations
   - Foreign key errors
   - Duplicate key issues

3. **Error Handling:**
   - Database errors not caught
   - Prisma errors not mapped
   - Connection timeouts
   - Deadlocks

4. **Data Mapping:**
   - Entity to DTO errors
   - Type conversion issues
   - Null handling in mapping
   - Missing fields

5. **Edge Cases:**
   - Empty result sets
   - Large datasets (pagination)
   - Concurrent updates
   - Soft delete issues"""

    def _generic_bug_fix_guidance(self) -> str:
        """Generic bug fix guidance."""
        return """
**General Bug Fix Checklist:**

1. **Logic Errors:**
   - Off-by-one errors
   - Incorrect conditionals
   - Loop issues
   - State management

2. **Data Issues:**
   - Null/undefined handling
   - Type errors
   - Data validation
   - Edge cases

3. **Error Handling:**
   - Uncaught exceptions
   - Poor error messages
   - Missing validation
   - Silent failures

4. **Dependencies:**
   - API call failures
   - External service issues
   - Library version problems
   - Configuration errors"""

    def _success_criteria(self, context: Dict[str, Any]) -> str:
        """Bug-fix-specific success criteria."""
        base_criteria = super()._success_criteria(context)

        bug_fix_criteria = """

**Bug Fix-Specific Success:**
  - Bug is completely fixed (verified)
  - Root cause identified and documented
  - No new bugs introduced
  - No functionality broken
  - Defensive checks added where needed
  - Fix is minimal and surgical
  - Test cases recommended/added
  - Prevention measures documented"""

        return base_criteria + bug_fix_criteria
