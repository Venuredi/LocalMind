"""
New Feature Prompt Template

Generates prompts for adding new features:
- Add new functionality
- Follow existing patterns
- Maintain backward compatibility
- Proper integration with existing code
"""

from typing import Dict, Any
from .base_template import BasePromptTemplate


class NewFeatureTemplate(BasePromptTemplate):
    """
    Template for new feature prompts.

    Focuses on adding functionality while maintaining existing architecture.
    """

    def _header(self, context: Dict[str, Any], title: str) -> str:
        """Generate new-feature-specific header."""
        return f"""{'='*70}
✨ ONTOLOGY-GUIDED NEW FEATURE PROMPT
{{'='*70}}
NEW FEATURE: {title}
{'='*70}"""

    def _task_definition(self, context: Dict[str, Any], description: str) -> str:
        """
        Generate new-feature-specific task definition.

        Focuses on:
        - Adding new functionality
        - Following existing patterns
        - Integration with existing code
        - Backward compatibility
        """
        component = context.get('component', {})
        component_name = component.get('name', 'Component')
        component_type = component.get('component_type', 'component')
        dependency_chain = context.get('dependency_chain', 'Unknown')

        return f"""🎯 TASK: ADD NEW FEATURE TO {component_name}

## Feature Description
{description}

**Integration Point:** `{component_name}` ({component_type})
**File:** `{{context.get('file_path', 'unknown')}}`
**Architecture:** {dependency_chain}

## Feature Implementation Approach

### Phase 1: Design & Planning

1. **Understand Integration Point**
   - Review current implementation
   - Identify where new feature fits
   - Determine integration points
   - Check for similar existing features

2. **Follow Existing Patterns**
   - Use same coding style
   - Follow naming conventions
   - Use existing DTOs/entities where possible
   - Match error handling patterns

3. **Impact Analysis**
   - What existing code will be affected?
   - Are there breaking changes?
   - What dependencies are needed?
   - What new DTOs/entities are required?

### Phase 2: Implementation

1. **DTOs and Types**
   - New request/response DTOs (if needed)
   - Update existing DTOs (if needed)
   - Add validation decorators
   - Document DTO properties

2. **Business Logic**
   - Add new methods to service
   - Follow single responsibility principle
   - Reuse existing repository methods
   - Add proper error handling

3. **API Layer** (if applicable)
   - New controller endpoints (if needed)
   - Proper HTTP methods and routes
   - Request/response DTOs
   - Swagger/OpenAPI documentation

4. **Data Layer** (if needed)
   - New repository methods
   - Database queries
   - Entity changes (if required)
   - Migration scripts (if schema changes)

### Phase 3: Integration

1. **Wire Up Dependencies**
   - Inject new dependencies
   - Update module providers
   - Configure services
   - Set up middleware/guards

2. **Maintain Backward Compatibility**
   - Don't break existing APIs
   - Deprecate old features gracefully
   - Provide migration path
   - Version APIs if needed

3. **Error Handling**
   - Add specific error types
   - Handle edge cases
   - Provide meaningful error messages
   - Log appropriately

## Implementation Requirements

### MANDATORY:
- ✅ Follow existing architectural patterns
- ✅ Use ONLY existing DTOs (or justify new ones)
- ✅ Maintain backward compatibility
- ✅ Follow the dependency chain: {dependency_chain}
- ✅ Add proper validation
- ✅ Include error handling
- ✅ Document public APIs

### NEW COMPONENTS (Justify If Needed):
- **New DTOs**: Only if existing ones don't fit
- **New Repository Methods**: Only if current ones insufficient
- **New Entities**: Only if new data model needed
- **New Services**: Only if new domain logic required

### FORBIDDEN:
- ❌ Breaking changes to existing APIs (without justification)
- ❌ Modifying existing DTO contracts (create new ones instead)
- ❌ Changing database schema without migrations
- ❌ Introducing technical debt
- ❌ Skipping validation or error handling

## Deliverables

1. **New Code**
   - Service methods
   - Controller endpoints (if applicable)
   - Repository methods (if needed)
   - DTOs (if needed)

2. **Updates to Existing Code**
   - Modified method signatures (if justified)
   - Updated module providers
   - Updated dependencies

3. **Documentation**
   - API documentation (Swagger/comments)
   - Usage examples
   - Migration notes (if breaking changes)

4. **Testing Recommendations**
   - Unit tests for new methods
   - Integration tests for end-to-end flow
   - Edge case testing

## Component-Specific Guidance
{self._generate_new_feature_guidance(context)}"""

    def _generate_new_feature_guidance(self, context: Dict[str, Any]) -> str:
        """Generate component-specific new feature guidance."""
        component_type = context.get('component_type', '').lower()

        if 'service' in component_type:
            return self._service_new_feature_guidance()
        elif 'controller' in component_type:
            return self._controller_new_feature_guidance()
        elif 'repository' in component_type:
            return self._repository_new_feature_guidance()
        else:
            return self._generic_new_feature_guidance()

    def _service_new_feature_guidance(self) -> str:
        """New feature guidance for services."""
        return """
**Service-Specific Implementation:**

1. **New Method Design:**
   - Clear method name (verb + noun pattern)
   - Single responsibility
   - Proper parameter validation
   - Return appropriate DTOs

2. **Business Logic:**
   - Validate inputs
   - Call repository methods
   - Transform data
   - Handle errors gracefully

3. **Integration:**
   - Inject required dependencies
   - Use existing repository methods
   - Reuse existing DTOs where possible
   - Add to module providers

4. **Example Pattern:**
```typescript
async newFeature(dto: NewFeatureDto): Promise<ResponseDto> {
  // 1. Validate input
  if (!dto.requiredField) {
    throw new BadRequestException('Required field missing');
  }

  // 2. Call repository
  try {
    const result = await this.repository.doSomething(dto);

    // 3. Transform to DTO
    return this.mapToResponseDto(result);

  } catch (error) {
    // 4. Handle errors
    throw this.handleError(error);
  }
}
```"""

    def _controller_new_feature_guidance(self) -> str:
        """New feature guidance for controllers."""
        return """
**Controller-Specific Implementation:**

1. **New Endpoint Design:**
   - RESTful route naming
   - Appropriate HTTP method
   - Clear path parameters
   - Query parameters for filters

2. **Endpoint Structure:**
```typescript
@Post('/new-feature')
@ApiOperation({ summary: 'Description of new feature' })
@ApiResponse({ status: 201, type: ResponseDto })
async newFeature(@Body() dto: NewFeatureDto): Promise<ResponseDto> {
  return await this.service.newFeature(dto);
}
```

3. **Best Practices:**
   - Use DTOs for request/response
   - Add Swagger decorators
   - Proper HTTP status codes
   - Add guards/interceptors if needed

4. **Validation:**
   - Use ValidationPipe
   - DTO validation decorators
   - Custom validators if needed"""

    def _repository_new_feature_guidance(self) -> str:
        """New feature guidance for repositories."""
        return """
**Repository-Specific Implementation:**

1. **New Query Design:**
   - Efficient SQL/query
   - Proper indexes
   - Use select for specific fields
   - Include relations if needed

2. **Method Pattern:**
```typescript
async newFeatureQuery(filters: Filters): Promise<Entity[]> {
  return await this.prisma.entity.findMany({
    where: {
      ...filters,
    },
    select: {
      // Only needed fields
    },
    include: {
      // Related entities
    },
  });
}
```

3. **Best Practices:**
   - Transaction support if needed
   - Proper error handling
   - Return domain entities
   - Handle null/empty results"""

    def _generic_new_feature_guidance(self) -> str:
        """Generic new feature guidance."""
        return """
**General Implementation Guidance:**

1. **Design First:**
   - Understand requirements
   - Plan integration points
   - Identify dependencies

2. **Follow Patterns:**
   - Match existing code style
   - Use same error handling
   - Follow naming conventions

3. **Test Thoroughly:**
   - Unit tests
   - Integration tests
   - Edge cases

4. **Document:**
   - Code comments where needed
   - API documentation
   - Usage examples"""

    def _success_criteria(self, context: Dict[str, Any]) -> str:
        """New-feature-specific success criteria."""
        base_criteria = super()._success_criteria(context)

        new_feature_criteria = """

**New Feature-Specific Success:**
  - Feature works as specified
  - Follows existing architectural patterns
  - Backward compatibility maintained
  - Proper error handling implemented
  - Validation added for all inputs
  - API documented (if applicable)
  - Integration tests recommended
  - No breaking changes (unless justified)"""

        return base_criteria + new_feature_criteria
