# 🚀 Quick Start Guide - Strict Mode Ontology Prompts

## 30-Second Overview

This system generates **hallucination-resistant AI prompts** from your codebase ontology with strict validation.

**Key Features**:
- ✅ Parses constructors for actual dependencies
- ✅ Detects stack automatically (NestJS/React/Flutter)
- ✅ Validates before generating prompts
- ✅ Categorizes dependencies by type
- ✅ Prevents AI from hallucinating non-existent code

---

## 🎯 Three Ways to Use

### 1. Web UI (Easiest)
1. Open `http://localhost:3000`
2. Navigate to **Prompt Builder** tab
3. Fill in:
   - **Type**: Enhancement/Bug Fix/New Feature/etc.
   - **Title**: "Enhance SurgeonsService"
   - **Description**: What you want done
   - **Components**: "SurgeonsService"
4. Click **"Generate Final Prompt"**
5. Copy prompt → Paste into Cursor/Claude

**Screenshot**:
```
┌─────────────────────────────────────────┐
│ 🛠 Prompt Builder                       │
├─────────────────────────────────────────┤
│ Type: [Enhancement ▼]                   │
│ Title: [Enhance SurgeonsService......] │
│ Description: [................]         │
│ Components: [SurgeonsService]           │
│                                         │
│ [🤖 Generate Final Prompt]              │
└─────────────────────────────────────────┘
```

---

### 2. API Endpoint (For Scripts)
```bash
curl -X POST http://localhost:8000/api/prompt/generate \
  -H "Content-Type: application/json" \
  -d '{
    "type": "enhancement",
    "title": "Enhance SurgeonsService",
    "description": "Improve performance, structure, and error handling",
    "components": ["SurgeonsService"]
  }'
```

**Response**:
```json
{
  "prompt": "======== ONTOLOGY-GUIDED ENHANCEMENT PROMPT ========\n...",
  "metadata": {
    "validation": { "valid": true, "warnings": [] },
    "constructor_dependencies": ["SurgeonsRepository"],
    "categorized_dependencies": {
      "repositories": ["SurgeonsRepository"],
      "services": []
    }
  }
}
```

---

### 3. Standalone CLI (Offline)
```bash
python3 ontology_to_prompt.py code-intelligence/data/index.json SurgeonsService
```

**Output**:
```
Loading ontology from: code-intelligence/data/index.json
✅ Loaded 415 components

Found component: SurgeonsService
Constructor dependencies: ['SurgeonsRepository']

✅ Prompt saved to: /tmp/prompt_SurgeonsService.md
```

Then:
```bash
cat /tmp/prompt_SurgeonsService.md  # View prompt
pbcopy < /tmp/prompt_SurgeonsService.md  # Copy to clipboard (macOS)
```

---

## 📋 Prompt Types Available

| Type | Description | Use Case |
|------|-------------|----------|
| `enhancement` | Improve existing code | Make it faster, cleaner, safer |
| `bug_fix` | Fix bugs | Something's broken |
| `new_feature` | Add functionality | Add bulk upload, exports, etc. |
| `refactoring` | Restructure code | Extract methods, reduce complexity |
| `analysis` | Code review | Get quality report, find issues |
| `feature_extension` | Extend existing | Add optional parameter to method |

---

## ✅ What Validation Checks

### Hard Errors (Blocks Generation)
- ❌ Stack = "unknown" → Can't determine backend vs frontend
- ❌ Duplicate dependencies → Ontology corruption

### Warnings (Allows Generation)
- ⚠️  No dependencies found → Component may be isolated
- ⚠️  Source code missing → Prompt lacks implementation details
- ⚠️  Graph relationships empty → Indexing issue

---

## 🔍 Understanding the Output

### Generated Prompt Structure
```
======================================================================
⚡ ONTOLOGY-GUIDED CODE ENHANCEMENT PROMPT (STRICT MODE)
======================================================================

🔒 SYSTEM CONTEXT
- Stack: nestjs-backend
- Architecture: Controller → Service → Repository → Database

🧠 ONTOLOGY CONTEXT
- Target: SurgeonsService
- File: .../surgeons.service.ts

🔗 DEPENDENCIES (STRICT)
Repositories:
 - SurgeonsRepository
Services:
 - None

🚫 ANTI-HALLUCINATION RULES
❌ DO NOT CREATE:
 - New services
 - New repositories
 - New DTOs

🎯 TASK
Enhance SurgeonsService with:
1. Performance improvements
2. Better structure
3. Stronger types
4. Better error handling

⚠️  HARD CONSTRAINTS
- Preserve ALL functionality
- No breaking changes
```

---

## 🛠 Troubleshooting

### Problem: "Component not found"
**Solution**: Check spelling. Component names are case-sensitive.
```bash
# Wrong
python3 ontology_to_prompt.py index.json surgeonsservice

# Correct
python3 ontology_to_prompt.py index.json SurgeonsService
```

### Problem: "Stack = unknown"
**Solution**: File path doesn't match detection rules. This is a hard error.
**Fix**: Update `detect_stack_strict()` in `context_builder.py` to include your path patterns.

### Problem: "No dependencies found"
**Solution**: This is usually OK (component is isolated) or the source code isn't available.
**Action**: Check if constructor exists in source code.

### Problem: "Validation failed"
**Solution**: Check the error message. Common causes:
- Ontology not indexed yet
- Component name typo
- Stack detection failed

---

## 🎨 Customization

### Add Custom Stack Detection
Edit `code-intelligence/prompt/context_builder.py`:
```python
def detect_stack_strict(self, file_path: str) -> str:
    file_path_lower = file_path.lower()

    # Add your pattern here
    if 'my-custom-backend' in file_path_lower:
        return 'nestjs-backend'

    # ... existing rules
```

### Add Custom Prompt Type
1. Create template: `code-intelligence/prompt/templates/my_type.py`
2. Extend `BasePromptTemplate`
3. Register in `template_engine.py`:
```python
self.templates = {
    # ... existing
    'my_type': MyTypeTemplate(),
}
```

---

## 📊 Validation Dashboard (Coming Soon)

Future enhancement will show:
- ✅ Components with valid prompts
- ⚠️  Components with warnings
- ❌ Components failing validation
- 📈 Validation statistics over time

---

## 🔗 Related Files

| File | Purpose |
|------|---------|
| `ontology_to_prompt.py` | Standalone CLI tool |
| `test_strict_validation.py` | Test suite |
| `STRICT_MODE_IMPROVEMENTS.md` | Technical details |
| `IMPLEMENTATION_COMPLETE.md` | Full documentation |

---

## 💡 Pro Tips

### Tip 1: Use Validation Warnings
Check `metadata.validation.warnings` to identify data quality issues:
```json
{
  "warnings": ["No dependencies found - verify constructor parsing"]
}
```
→ This might indicate the indexer needs updating.

### Tip 2: Categorized Dependencies
Use `metadata.categorized_dependencies` to verify architecture:
```json
{
  "repositories": ["SurgeonsRepository"],
  "services": ["NotificationService"],
  "controllers": []
}
```
→ If a service has controllers as dependencies, that's an architectural violation.

### Tip 3: Constructor Dependencies
Compare `metadata.constructor_dependencies` (truth) vs graph dependencies:
```json
{
  "constructor_dependencies": ["SurgeonsRepository", "PrismaService"],
  "dependencies_count": 0
}
```
→ Mismatch indicates graph indexing issue.

---

## 🚀 Next Steps

1. **Try it**: Generate your first prompt
2. **Validate**: Check the metadata for warnings
3. **Use it**: Copy prompt to Cursor/Claude
4. **Iterate**: Use feedback to improve prompts
5. **Customize**: Add your own templates and rules

---

## 📞 Support

**Issues**: Create ticket with:
- Component name
- Error message
- Validation metadata

**Example**:
```
Component: SurgeonsService
Error: "Stack = unknown"
Metadata: { "validation": { "errors": [...] } }
```

---

**Version**: 1.0.0
**Last Updated**: 2026-04-11
**Status**: ✅ Production Ready
