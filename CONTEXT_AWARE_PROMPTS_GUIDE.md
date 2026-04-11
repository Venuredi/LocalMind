# Context-Aware Prompt Generation Guide

## Overview

LocalMind now generates **context-rich AI prompts** that include not just the target file, but also all related components, dependencies, APIs, and data models from your codebase.

## What's Included in Generated Prompts

### 1. **Target Source Code**
The complete source code of the file you want to work with.

**Example:**
```typescript
// Full AssetListGrid.tsx component (162 lines)
export function AssetListGrid({...}) {
  // Complete implementation
}
```

### 2. **Related Components**
All components that the target uses or depends on:
- **Hooks** (e.g., `useAssetListGridState`)
- **Child components** (e.g., `LocationDisplay`, `AssetStatusChip`)
- **Utility functions** (e.g., `buildAssetColumns`, `getLocationAndTimestamp`)
- **Helper components** (e.g., `ErrorOverlay`, `NoRowsOverlay`)

**Each includes:**
- Full source code (up to 30 lines) or preview
- File path and location
- Type information

### 3. **API Context** (for enhance/feature/bugfix)
Relevant API endpoints that the component uses:
```
GET  /api/assets                   → AssetsController.findAll
POST /api/assets/search            → AssetsController.search
GET  /api/locations/:id            → LocationsController.findOne
```

### 4. **Data Models** (for enhance/feature/bugfix)
Prisma models and types used:
- `AssetEntity`
- `AssetType`
- `Location`
- `AssetHistory`

### 5. **Task-Specific Instructions**

Based on intent, includes:

#### Analyze
- Code quality checklist
- Performance analysis points
- Type safety review
- Best practices check

#### Enhance
- Implementation guidelines
- Performance considerations (useMemo, useCallback)
- UX requirements (loading states, error handling)
- Type safety requirements
- Testing suggestions

#### Refactor
- Clarity and maintainability goals
- Performance optimization
- Modularity improvements
- Modern React patterns

#### Bug Fix
- Root cause analysis
- Minimal fix approach
- Validation steps
- Prevention strategies

#### Feature
- Design approach
- Implementation requirements
- Integration points
- Quality standards

---

## How to Use

### Method 1: Interactive CLI

```bash
cd /Users/venureddy/Downloads/LocalMind
python3 generate_prompt.py
```

Follow the prompts:
1. Select intent (analyze, enhance, refactor, bugfix, feature)
2. Specify target file/component
3. Describe what you want
4. Choose context depth (5, 10, or 20 components)

**Output:** A markdown file ready to paste into any AI tool.

### Method 2: Programmatic

```python
from context_builder.context_assembler import ContextAssembler
from parsers.treesitter.context_aware_prompt_generator import ContextAwarePromptGenerator

# Setup
assembler = ContextAssembler("code-intelligence/data/index.json", "/path/to/repo")

# Get context
context = assembler.assemble_context(
    query="Add pagination to AssetListGrid",
    target_files=["AssetListGrid.tsx"],
    intent="enhance",
    max_components=15
)

# Generate prompt
generator = ContextAwarePromptGenerator(context, "/path/to/repo")
prompt = generator.generate(
    user_description="Add pagination to AssetListGrid",
    intent="enhance"
)

print(prompt)
```

---

## Example Prompts

### Example 1: Enhancement
**User Input:** "Add virtualization to AssetListGrid to handle 10,000+ rows"

**Generated Prompt Includes:**
- ✅ Full AssetListGrid.tsx source (162 lines)
- ✅ useAssetListGridState hook source (120 lines)
- ✅ Related column builders
- ✅ MUI DataGrid configuration
- ✅ Task: Specific instructions for adding virtualization with performance considerations

**Size:** ~8KB, 285 lines, 4 code blocks

### Example 2: Analysis
**User Input:** "Analyze LocationDisplay for performance issues"

**Generated Prompt Includes:**
- ✅ Full LocationDisplay.tsx source (59 lines)
- ✅ getLocationAndTimestamp utility
- ✅ AssetEntity type definition
- ✅ Task: Performance analysis checklist with React-specific points

**Size:** ~5.3KB, 177 lines, 4 code blocks

### Example 3: Refactoring
**User Input:** "Refactor useAssetListGridState to use React Query"

**Generated Prompt Includes:**
- ✅ Full useAssetListGridState hook (120 lines)
- ✅ useAssets hook (API client)
- ✅ useCaseSchedulePaginated hook (example pattern)
- ✅ Related API clients
- ✅ Task: Refactoring guidelines for React Query migration

**Size:** ~12KB, 427 lines, 4 code blocks

---

## Use Cases

### 1. **Code Review / Analysis**
```bash
Intent: analyze
Target: LocationDisplay.tsx
Description: Check for performance issues and optimization opportunities
```

**AI will analyze:**
- Component structure
- Hook usage patterns
- Memoization opportunities
- Re-render triggers
- Type safety

### 2. **Adding Features**
```bash
Intent: enhance
Target: AssetListGrid.tsx
Description: Add column filtering and sorting persistence
```

**AI will provide:**
- Implementation approach
- Integration with existing state management
- Type-safe implementation
- UX considerations (loading states, etc.)

### 3. **Performance Optimization**
```bash
Intent: enhance
Target: AssetListGrid.tsx
Description: Add virtualization for 10,000+ rows
```

**AI will suggest:**
- Virtualization libraries (react-window, react-virtualized)
- Integration with MUI DataGrid
- Performance benchmarks
- Testing approach

### 4. **Refactoring**
```bash
Intent: refactor
Target: useAssetListGridState
Description: Migrate to React Query for better caching and state management
```

**AI will plan:**
- Migration strategy
- API integration changes
- State management updates
- Testing migration

### 5. **Bug Fixes**
```bash
Intent: bugfix
Target: AssetListGrid.tsx
Description: Fix pagination reset on filter change
```

**AI will:**
- Identify root cause from source
- Suggest minimal fix
- Explain validation approach
- Recommend tests

---

## Prompt Quality

### ✅ What Makes These Prompts High Quality

1. **Complete Context**
   - Target file + all dependencies
   - No missing pieces for AI to guess

2. **Real Code**
   - Actual source code from your repo
   - Not generic examples

3. **Related Components**
   - Shows patterns from your codebase
   - AI learns your coding style

4. **API Awareness**
   - Knows which endpoints exist
   - Can suggest correct API calls

5. **Type Information**
   - Full TypeScript types
   - Better type-safe suggestions

6. **Task-Specific Instructions**
   - Tailored guidance for each intent
   - Best practices for React/TypeScript

### 📊 Metrics

| Prompt Type | Avg Size | Avg Components | Avg Lines | Code Blocks |
|-------------|----------|----------------|-----------|-------------|
| Analyze     | 5-6 KB   | 5-8            | 150-200   | 3-4         |
| Enhance     | 8-10 KB  | 8-12           | 250-350   | 4-6         |
| Refactor    | 10-15 KB | 10-15          | 350-500   | 5-8         |
| Feature     | 12-18 KB | 15-20          | 400-600   | 6-10        |

---

## Comparison: Before vs After

### Before (Without Context)
```
User: "Add pagination to AssetListGrid"

AI Response:
"Here's a generic pagination implementation..."
[Generic React pagination code]
[Doesn't match your codebase patterns]
[Uses wrong state management]
[Missing type definitions]
```

### After (With Context)
```
User: "Add pagination to AssetListGrid"

LocalMind Generates:
- Full AssetListGrid source
- useAssetListGridState hook
- Existing pagination patterns
- MUI DataGrid configuration
- AssetEntity types

AI Response:
"Based on your existing useAssetListGridState hook and
MUI DataGrid Premium setup, here's how to enhance the
pagination..."
[Code that matches your patterns]
[Uses your state management]
[Integrates with existing types]
[Follows your conventions]
```

---

## Tips for Best Results

### 1. **Be Specific**
❌ "Improve AssetListGrid"
✅ "Add virtualization to AssetListGrid to handle 10,000+ rows efficiently"

### 2. **Choose Right Intent**
- **analyze**: Understand existing code
- **enhance**: Add features to existing code
- **refactor**: Restructure/improve existing code
- **bugfix**: Fix a specific issue
- **feature**: Build something new

### 3. **Adjust Context Depth**
- **Minimal (5)**: Quick analysis, small changes
- **Normal (10)**: Most tasks, balanced context
- **Comprehensive (20)**: Complex features, major refactors

### 4. **Target Naming**
Works with:
- File names: `AssetListGrid.tsx`
- Component names: `AssetListGrid`
- Partial names: `AssetGrid`, `LocationDisplay`
- Paths: `asset-list-grid/cells/LocationDisplay`

---

## Integration with AI Tools

### Claude Code
```bash
# Generate prompt
python3 generate_prompt.py

# Copy output file
# Paste into Claude Code chat
```

### Cursor
```bash
# Generate prompt
python3 generate_prompt.py

# Copy content
# Use Cmd+K or Cmd+L in Cursor
# Paste prompt
```

### GitHub Copilot Chat
```bash
# Generate prompt
python3 generate_prompt.py

# Open Copilot Chat
# Paste full prompt
```

### ChatGPT / Claude Web
```bash
# Generate prompt
python3 generate_prompt.py

# Copy markdown file
# Paste into chat
```

---

## Advanced Usage

### Custom Context Assembly

```python
# Include more backend components
context = assembler.assemble_context(
    query="Add caching to asset API",
    target_files=["AssetsController.ts"],
    intent="enhance",
    max_components=25  # More context
)
```

### Multiple Target Files

```python
context = assembler.assemble_context(
    query="Refactor asset display logic",
    target_files=[
        "AssetListGrid.tsx",
        "AssetCard.tsx",
        "AssetStatusChip.tsx"
    ],
    intent="refactor",
    max_components=20
)
```

---

## Troubleshooting

### "Target file not found"
- Check file name spelling
- Try partial name (e.g., "AssetGrid" instead of "AssetListGrid.tsx")
- Ensure file was indexed

### "No context assembled"
- Run indexing first: `python3 -m code_intelligence index`
- Check repo path is correct
- Verify index.json exists

### "Too much/little context"
- Adjust `max_components` parameter
- Use 5 for quick tasks
- Use 20 for complex refactors

---

## Next Steps

1. **Try It Out**
   ```bash
   python3 generate_prompt.py
   ```

2. **Use with Your AI Tool**
   - Copy generated .md file
   - Paste into Claude, Cursor, Copilot, etc.

3. **Iterate**
   - Adjust context depth
   - Try different intents
   - Refine descriptions

4. **Share Feedback**
   - What works well?
   - What's missing?
   - Improvement ideas?

---

## Summary

✅ **Context-aware prompts** include target file + dependencies + APIs + types
✅ **Task-specific instructions** tailored to analyze/enhance/refactor/bugfix/feature
✅ **Real codebase patterns** so AI matches your style
✅ **Ready for any AI tool** (Claude, Cursor, Copilot, ChatGPT)
✅ **5-20 components** of context (configurable)
✅ **Generated in seconds** from indexed ontology

**Result:** Better AI suggestions that actually work with your codebase!
