"""
Feature Extension Prompt Template

Generates prompts for extending existing features:
- Extend existing functionality
- Add optional parameters
- Add new variants
- Backward compatible enhancements
"""

from typing import Dict, Any
from .base_template import BasePromptTemplate


class FeatureExtensionTemplate(BasePromptTemplate):
    """
    Template for feature extension prompts.

    Focuses on extending existing features while maintaining backward compatibility.
    """

    def _header(self, context: Dict[str, Any], title: str) -> str:
        """Generate feature-extension-specific header."""
        return f"""{'='*70}
🔧 ONTOLOGY-GUIDED FEATURE EXTENSION PROMPT
{{'='*70}}
FEATURE EXTENSION: {title}
{'='*70}"""

    def _task_definition(self, context: Dict[str, Any], description: str) -> str:
        """
        Generate feature-extension-specific task definition.

        Focuses on:
        - Extending existing features
        - Maintaining backward compatibility
        - Adding optional capabilities
        - Preserving existing behavior
        """
        component = context.get('component', {})
        component_name = component.get('name', 'Component')
        component_type = component.get('component_type', 'component')

        return f"""🎯 TASK: EXTEND FEATURE IN {component_name}

## Feature Extension Description
{description}

**Base Component:** `{component_name}` ({component_type})
**File:** `{{context.get('file_path', 'unknown')}}`

## Feature Extension Strategy

### Core Principle: Backward Compatibility
**Existing functionality MUST continue to work exactly as before!**

- ✅ Add new capabilities
- ✅ Make new parameters optional
- ✅ Provide sensible defaults
- ❌ Don't break existing usage
- ❌ Don't change existing behavior
- ❌ Don't require changes from existing consumers

### Extension Approach

#### Phase 1: Understand Existing Feature

1. **Current Functionality**
   - What does the existing feature do?
   - What are its inputs/outputs?
   - Who uses it and how?
   - What are the constraints?

2. **Extension Requirements**
   - What new capability is needed?
   - How does it relate to existing functionality?
   - Can it be optional?
   - What's the default behavior?

3. **Compatibility Analysis**
   - Will existing code break?
   - What needs to be deprecated?
   - Migration path needed?

#### Phase 2: Design Extension

1. **Extension Patterns**

   **A. Optional Parameters (Preferred)**
   ```typescript
   // Before
   findAll(filters?: Filters)

   // After - Add optional parameter
   findAll(filters?: Filters, options?: Options)
   ```

   **B. Method Overloading**
   ```typescript
   // Keep existing method
   findAll(filters?: Filters)

   // Add new variant
   findAllWithPagination(filters?: Filters, pagination?: Pagination)
   ```

   **C. Configuration Objects**
   ```typescript
   // Before
   process(data: Data, validateFirst: boolean)

   // After - Use config object
   process(data: Data, config?: {{
     validateFirst?: boolean,
     newFeature?: boolean,  // New capability
   }})
   ```

   **D. Feature Flags/Options**
   ```typescript
   // Allow opt-in to new behavior
   process(data: Data, options?: {{
     useNewFeature?: boolean,  // Default: false
   }})
   ```

2. **Default Behavior**
   - New parameters default to existing behavior
   - Explicit opt-in for new features
   - No surprises for existing users

3. **Deprecation Strategy** (if needed)
   - Mark old approach as deprecated
   - Provide migration guide
   - Support old approach for transition period
   - Clear timeline for removal

#### Phase 3: Implementation

1. **Extend Method Signature**
   - Add optional parameters (at the end)
   - Provide default values
   - Maintain return type (or make backward compatible)

2. **Implement Extension Logic**
   - Check if new feature is requested
   - Use new code path if requested
   - Fall back to existing behavior otherwise

3. **Update DTOs** (if needed)
   - Add optional fields
   - Don't make existing fields required
   - Provide defaults

4. **Update Documentation**
   - Document new parameters
   - Show examples of new usage
   - Explain backward compatibility
   - Provide migration guide if needed

### Extension Requirements

#### MANDATORY:
- ✅ Existing functionality preserved exactly
- ✅ New parameters are OPTIONAL
- ✅ Sensible defaults provided
- ✅ Backward compatible
- ✅ Existing tests still pass
- ✅ No breaking changes
- ✅ Clear documentation

#### RECOMMENDED:
- ✅ Feature flags for gradual rollout
- ✅ Metrics to track new feature usage
- ✅ A/B testing capability
- ✅ Rollback plan

#### FORBIDDEN:
- ❌ Breaking existing API contracts
- ❌ Changing existing behavior without opt-in
- ❌ Making optional parameters required
- ❌ Changing return types incompatibly
- ❌ Removing existing functionality

## Extension Patterns by Component Type
{self._generate_extension_guidance(context)}

## Testing Strategy

### 1. Backward Compatibility Tests
```typescript
describe('Backward Compatibility', () => {{
  it('should work with existing calls (no new parameters)', async () => {{
    // Test existing usage still works
    const result = await service.method(oldParams);
    expect(result).toBeDefined();
  }});

  it('should maintain existing behavior when new params not provided', async () => {{
    // Verify default behavior unchanged
  }});
}});
```

### 2. New Feature Tests
```typescript
describe('New Feature Extension', () => {{
  it('should support new optional parameter', async () => {{
    const result = await service.method(oldParams, {{ newFeature: true }});
    expect(result).toHaveNewCapability();
  }});

  it('should use new behavior when opted in', async () => {{
    // Verify new functionality works
  }});
}});
```

### 3. Edge Case Tests
```typescript
describe('Edge Cases', () => {{
  it('should handle partial new parameters', async () => {{
    // Test with some new params, some omitted
  }});

  it('should validate new parameters correctly', async () => {{
    // Test validation of new params
  }});
}});
```

## Deliverables

1. **Extended Code**
   - Updated method signatures
   - New optional parameters
   - Default values
   - Extension logic

2. **Updated DTOs** (if applicable)
   - New optional fields
   - Validation for new fields
   - Documentation

3. **Documentation**
   - What was extended
   - How to use new features
   - Backward compatibility notes
   - Migration guide (if deprecating)
   - Examples

4. **Testing Recommendations**
   - Backward compatibility tests
   - New feature tests
   - Integration tests

## Example: Feature Extension

### Scenario: Extend search to support fuzzy matching

**Before:**
```typescript
async findSurgeons(filters: SurgeonFilters): Promise<Surgeon[]> {{
  return this.repository.findAll({{
    where: {{
      specialty: filters.specialty,
      location: filters.location,
    }},
  }});
}}
```

**After (Backward Compatible Extension):**
```typescript
interface SurgeonSearchOptions {{
  fuzzyMatch?: boolean;  // NEW: Optional fuzzy matching
  matchThreshold?: number;  // NEW: How close to match (0-1)
}}

async findSurgeons(
  filters: SurgeonFilters,
  options?: SurgeonSearchOptions  // NEW: Optional parameter
): Promise<Surgeon[]> {{
  // Default behavior (existing functionality)
  if (!options?.fuzzyMatch) {{
    return this.repository.findAll({{
      where: {{
        specialty: filters.specialty,
        location: filters.location,
      }},
    }});
  }}

  // NEW: Extended behavior (opt-in)
  const threshold = options.matchThreshold ?? 0.8;  // Default
  return this.repository.findWithFuzzyMatch({{
    filters,
    threshold,
  }});
}}
```

**Usage:**
```typescript
// Existing code (unchanged, still works)
const surgeons1 = await service.findSurgeons({{ specialty: 'Cardiology' }});

// New feature (opt-in)
const surgeons2 = await service.findSurgeons(
  {{ specialty: 'Cardiology' }},
  {{ fuzzyMatch: true, matchThreshold: 0.9 }}
);
```"""

    def _generate_extension_guidance(self, context: Dict[str, Any]) -> str:
        """Generate component-specific extension guidance."""
        component_type = context.get('component_type', '').lower()

        if 'service' in component_type:
            return self._service_extension_guidance()
        elif 'controller' in component_type:
            return self._controller_extension_guidance()
        elif 'repository' in component_type:
            return self._repository_extension_guidance()
        else:
            return self._generic_extension_guidance()

    def _service_extension_guidance(self) -> str:
        """Extension guidance for services."""
        return """
**Service Extension Patterns:**

1. **Add Optional Business Logic:**
   - New validation rules (opt-in)
   - Alternative processing paths
   - Additional transformations
   - Extra calculations

2. **Example - Add Caching:**
```typescript
// Before
async getData(id: string): Promise<Data> {
  return this.repository.findById(id);
}

// After
async getData(
  id: string,
  options?: { useCache?: boolean }
): Promise<Data> {
  if (options?.useCache) {
    const cached = await this.cache.get(id);
    if (cached) return cached;
  }

  const data = await this.repository.findById(id);

  if (options?.useCache) {
    await this.cache.set(id, data);
  }

  return data;
}
```

3. **Example - Add Filtering:**
```typescript
async findAll(
  filters: Filters,
  options?: {
    includeInactive?: boolean,  // NEW
    sortBy?: string,  // NEW
  }
): Promise<Data[]> {
  // Existing behavior preserved
  let results = await this.repository.findAll(filters);

  // NEW: Optional extensions
  if (!options?.includeInactive) {
    results = results.filter(r => r.active);
  }

  if (options?.sortBy) {
    results = this.sort(results, options.sortBy);
  }

  return results;
}
```"""

    def _controller_extension_guidance(self) -> str:
        """Extension guidance for controllers."""
        return """
**Controller Extension Patterns:**

1. **Add Query Parameters:**
```typescript
// Before
@Get()
async findAll(@Query() filters: Filters) {
  return this.service.findAll(filters);
}

// After - Add optional query params
@Get()
async findAll(
  @Query() filters: Filters,
  @Query('includeInactive') includeInactive?: boolean,  // NEW
  @Query('sortBy') sortBy?: string,  // NEW
) {
  return this.service.findAll(filters, {
    includeInactive,
    sortBy,
  });
}
```

2. **Add Optional Headers:**
```typescript
@Post()
async create(
  @Body() dto: CreateDto,
  @Headers('x-feature-flag') useNewFeature?: string,  // NEW
) {
  const options = {
    useNewFeature: useNewFeature === 'true',
  };
  return this.service.create(dto, options);
}
```"""

    def _repository_extension_guidance(self) -> str:
        """Extension guidance for repositories."""
        return """
**Repository Extension Patterns:**

1. **Add Query Options:**
```typescript
// Before
async findAll(filters: Filters): Promise<Entity[]> {
  return this.prisma.entity.findMany({
    where: filters,
  });
}

// After
async findAll(
  filters: Filters,
  options?: {
    include?: string[],  // NEW: Relations to include
    select?: string[],   // NEW: Fields to select
  }
): Promise<Entity[]> {
  return this.prisma.entity.findMany({
    where: filters,
    include: this.buildInclude(options?.include),
    select: this.buildSelect(options?.select),
  });
}
```

2. **Add Pagination:**
```typescript
async findAll(
  filters: Filters,
  pagination?: { page?: number; limit?: number }  // NEW
): Promise<Entity[]> {
  const query = { where: filters };

  if (pagination) {
    query.skip = (pagination.page ?? 0) * (pagination.limit ?? 50);
    query.take = pagination.limit ?? 50;
  }

  return this.prisma.entity.findMany(query);
}
```"""

    def _generic_extension_guidance(self) -> str:
        """Generic extension guidance."""
        return """
**General Extension Patterns:**

1. **Optional Parameters:**
   - Always optional
   - Provide defaults
   - Document behavior

2. **Feature Flags:**
   - Gradual rollout
   - Easy rollback
   - Metrics collection

3. **Versioning** (if major changes):
   - Keep old version
   - Add new version
   - Deprecate gracefully"""

    def _success_criteria(self, context: Dict[str, Any]) -> str:
        """Extension-specific success criteria."""
        base_criteria = super()._success_criteria(context)

        extension_criteria = """

**Feature Extension-Specific Success:**
  - Existing functionality preserved
  - New feature works as specified
  - Backward compatible
  - All existing tests pass
  - New tests added for extension
  - Default behavior unchanged
  - Optional parameters properly defaulted
  - Documentation updated
  - No breaking changes"""

        return base_criteria + extension_criteria
