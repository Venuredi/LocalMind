"""
Analysis Prompt Template

Generates prompts for code analysis tasks:
- Analyze code quality
- Identify issues and improvements
- Security analysis
- Performance analysis
- Architecture review
"""

from typing import Dict, Any
from .base_template import BasePromptTemplate


class AnalysisTemplate(BasePromptTemplate):
    """
    Template for code analysis prompts.

    Focuses on analyzing code and providing insights without making changes.
    """

    def _header(self, context: Dict[str, Any], title: str) -> str:
        """Generate analysis-specific header."""
        return f"""{'='*70}
🔍 ONTOLOGY-GUIDED CODE ANALYSIS PROMPT
{{'='*70}}
ANALYSIS: {title}
{'='*70}"""

    def _task_definition(self, context: Dict[str, Any], description: str) -> str:
        """
        Generate analysis-specific task definition.

        Focuses on:
        - Code review
        - Quality assessment
        - Issue identification
        - Recommendations
        """
        component = context.get('component', {})
        component_name = component.get('name', 'Component')
        component_type = component.get('component_type', 'component')
        tech_stack = context.get('tech_stack', 'Unknown')

        return f"""🎯 TASK: ANALYZE {component_name}

## Analysis Objective
{description}

**Target Component:** `{component_name}` ({component_type})
**Technology Stack:** {tech_stack}
**File:** `{{context.get('file_path', 'unknown')}}`

## Analysis Framework

### 1. Code Quality Analysis

#### A. Readability
- **Naming Conventions:**
  - Are names descriptive and meaningful?
  - Consistent naming patterns?
  - Following language conventions?

- **Code Structure:**
  - Logical organization?
  - Clear separation of concerns?
  - Appropriate abstraction levels?

- **Complexity:**
  - Cyclomatic complexity (< 10 per method ideally)
  - Nesting depth (< 4 levels)
  - Method length (< 50 lines ideally)

#### B. Maintainability
- **DRY (Don't Repeat Yourself):**
  - Any code duplication?
  - Opportunities for extraction?

- **SOLID Principles:**
  - Single Responsibility?
  - Open/Closed?
  - Liskov Substitution?
  - Interface Segregation?
  - Dependency Inversion?

- **Documentation:**
  - Complex logic documented?
  - Public APIs documented?
  - Non-obvious behavior explained?

### 2. Performance Analysis

#### A. Efficiency
- **Algorithm Complexity:**
  - Time complexity analysis
  - Space complexity analysis
  - Optimization opportunities

- **Database Queries:**
  - N+1 query problems?
  - Missing indexes?
  - Overfetching data?
  - Unnecessary joins?

- **Resource Usage:**
  - Memory leaks?
  - Connection pooling?
  - Caching opportunities?

#### B. Scalability
- **Concurrency:**
  - Thread safety issues?
  - Race conditions?
  - Deadlock potential?

- **Load Handling:**
  - How does it scale?
  - Bottlenecks?
  - Rate limiting needed?

### 3. Security Analysis

#### A. Input Validation
- All inputs validated?
- Injection vulnerabilities (SQL, XSS, etc.)?
- Input sanitization?
- Type checking?

#### B. Authentication & Authorization
- Proper authentication checks?
- Authorization enforced?
- Role-based access control?
- Token/session management?

#### C. Data Protection
- Sensitive data exposure?
- Proper encryption?
- Secure data transmission?
- Logging sensitive information?

### 4. Error Handling Analysis

#### A. Exception Handling
- All exceptions caught?
- Proper error types thrown?
- Graceful degradation?
- Meaningful error messages?

#### B. Logging
- Appropriate logging levels?
- Sensitive data in logs?
- Enough context logged?
- Error tracking?

### 5. Architecture Analysis

#### A. Design Patterns
- Appropriate patterns used?
- Over-engineering?
- Under-engineering?
- Pattern misuse?

#### B. Dependencies
- Tight coupling?
- Circular dependencies?
- Dependency injection used properly?
- External dependencies managed?

#### C. Separation of Concerns
- Business logic in services?
- Data access in repositories?
- API layer thin?
- Clear layer boundaries?

### 6. Testing Analysis

#### A. Test Coverage
- Unit tests present?
- Integration tests needed?
- Edge cases covered?
- Error scenarios tested?

#### B. Testability
- Code easy to test?
- Dependencies mockable?
- Pure functions where possible?
- Test-friendly design?

## Analysis Deliverables

### 1. Executive Summary
- Overall quality score (1-10)
- Top 3 strengths
- Top 3 concerns
- Priority issues

### 2. Detailed Findings

For each category, provide:

**✅ Strengths:**
- What's done well
- Good practices observed
- Positive patterns

**⚠️  Issues:**
- Problems identified
- Severity (Critical/High/Medium/Low)
- Impact assessment

**💡 Recommendations:**
- Specific improvements
- Priority order
- Expected impact

### 3. Code Smells Identified

List any code smells found:
- Long methods
- Large classes
- Too many parameters
- Duplicate code
- Complex conditionals
- Poor naming
- Magic numbers
- etc.

### 4. Refactoring Opportunities

- What could be refactored?
- Why refactor it?
- Expected benefits?

### 5. Security Vulnerabilities

- Any security issues?
- Severity assessment
- Remediation steps

### 6. Performance Bottlenecks

- Identified bottlenecks
- Performance impact
- Optimization suggestions

## Component-Specific Analysis
{self._generate_analysis_guidance(context)}

## Analysis Output Format

```markdown
# Code Analysis Report: {component_name}

## Executive Summary
- **Overall Quality:** [Score/10]
- **Strengths:** [Top 3]
- **Concerns:** [Top 3]
- **Recommendation:** [Primary action]

## Detailed Analysis

### 1. Code Quality
**Score:** [X/10]

✅ **Strengths:**
- [Strength 1]
- [Strength 2]

⚠️  **Issues:**
- [Issue 1] - [Severity]
- [Issue 2] - [Severity]

💡 **Recommendations:**
- [Recommendation 1]
- [Recommendation 2]

### 2. Performance
[Same format...]

### 3. Security
[Same format...]

### 4. Maintainability
[Same format...]

### 5. Architecture
[Same format...]

## Priority Actions

### Critical (Fix Immediately):
1. [Action 1]
2. [Action 2]

### High Priority (Fix Soon):
1. [Action 1]
2. [Action 2]

### Medium Priority (Plan):
1. [Action 1]
2. [Action 2]

### Low Priority (Nice to Have):
1. [Action 1]
2. [Action 2]

## Code Examples

### Issue Example:
**Problem:**
```typescript
// Current problematic code
```

**Recommendation:**
```typescript
// Improved code
```

## Metrics

- Lines of Code: [X]
- Cyclomatic Complexity: [X]
- Methods: [X]
- Test Coverage: [X%]

## Conclusion

[Summary of findings and next steps]
```"""

    def _generate_analysis_guidance(self, context: Dict[str, Any]) -> str:
        """Generate component-specific analysis guidance."""
        component_type = context.get('component_type', '').lower()

        if 'service' in component_type:
            return self._service_analysis_guidance()
        elif 'controller' in component_type:
            return self._controller_analysis_guidance()
        elif 'repository' in component_type:
            return self._repository_analysis_guidance()
        else:
            return self._generic_analysis_guidance()

    def _service_analysis_guidance(self) -> str:
        """Analysis guidance for services."""
        return """
**Service-Specific Analysis Focus:**

1. **Business Logic:**
   - Correct implementation of business rules?
   - Edge cases handled?
   - Validation comprehensive?

2. **Dependencies:**
   - Properly injected?
   - Appropriate dependencies?
   - Avoiding circular dependencies?

3. **Data Transformation:**
   - Efficient DTO mapping?
   - Data validation?
   - Type safety?

4. **Error Handling:**
   - Business exceptions clear?
   - Error propagation correct?
   - Meaningful messages?

5. **Transaction Management:**
   - Proper transaction boundaries?
   - Rollback scenarios handled?
   - Consistency maintained?"""

    def _controller_analysis_guidance(self) -> str:
        """Analysis guidance for controllers."""
        return """
**Controller-Specific Analysis Focus:**

1. **API Design:**
   - RESTful principles followed?
   - Appropriate HTTP methods?
   - Clear route naming?
   - Proper status codes?

2. **Request Handling:**
   - Input validation complete?
   - DTO usage correct?
   - Parameter binding proper?

3. **Response Formation:**
   - Consistent response format?
   - Appropriate DTOs?
   - Error responses clear?

4. **Security:**
   - Authentication enforced?
   - Authorization checked?
   - Input sanitization?
   - Rate limiting?

5. **Documentation:**
   - Swagger decorators?
   - API documented?
   - Examples provided?"""

    def _repository_analysis_guidance(self) -> str:
        """Analysis guidance for repositories."""
        return """
**Repository-Specific Analysis Focus:**

1. **Query Efficiency:**
   - Optimal queries?
   - Indexes used?
   - N+1 problems?
   - Overfetching avoided?

2. **Data Access Patterns:**
   - Appropriate abstractions?
   - Reusable queries?
   - Clear method names?

3. **Transaction Handling:**
   - Proper isolation levels?
   - Deadlock prevention?
   - Connection management?

4. **Error Handling:**
   - Database errors mapped?
   - Constraint violations handled?
   - Meaningful error messages?

5. **Performance:**
   - Pagination implemented?
   - Lazy loading appropriate?
   - Bulk operations optimized?"""

    def _generic_analysis_guidance(self) -> str:
        """Generic analysis guidance."""
        return """
**General Analysis Focus:**

1. **Code Quality:**
   - Readability
   - Maintainability
   - Consistency

2. **Best Practices:**
   - Language conventions
   - Framework patterns
   - Industry standards

3. **Technical Debt:**
   - Shortcuts taken?
   - TODOs and FIXMEs?
   - Deprecated code?

4. **Documentation:**
   - Adequate comments?
   - API docs?
   - Complex logic explained?"""

    def _success_criteria(self, context: Dict[str, Any]) -> str:
        """Analysis-specific success criteria."""
        base_criteria = super()._success_criteria(context)

        analysis_criteria = """

**Analysis-Specific Success:**
  - Comprehensive analysis performed
  - All categories covered
  - Issues prioritized by severity
  - Actionable recommendations provided
  - Examples included for issues
  - Code quality scored
  - Security vulnerabilities identified
  - Performance bottlenecks found
  - Report is clear and structured"""

        return base_criteria + analysis_criteria
