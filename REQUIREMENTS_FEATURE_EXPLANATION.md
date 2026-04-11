# Requirements to Prompt Feature - How It Works

## Simple Explanation

The **Requirements to Prompt** feature helps you get better AI-generated code by automatically gathering context from your codebase.

### The Problem It Solves

When you ask AI tools (Claude, GPT-4, Copilot) to generate code:
- ❌ They don't know your codebase structure
- ❌ They don't follow your naming conventions
- ❌ They don't match your existing patterns
- ❌ The generated code doesn't integrate well

### The Solution

This feature:
1. ✅ Analyzes your entire codebase using Tree Sitter
2. ✅ Finds relevant existing code
3. ✅ Identifies your patterns and conventions
4. ✅ Generates a comprehensive prompt with all context
5. ✅ You give this prompt to AI tools
6. ✅ AI generates code that fits perfectly

---

## How It Works (Visual)

```
┌─────────────────────────────────────────────────────────────┐
│ YOU: "Add user profile editing feature"                     │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ TREE SITTER PARSER                                           │
│ - Scans your entire codebase                                 │
│ - Extracts all classes, functions, imports                   │
│ - Builds ontology/knowledge graph                            │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ PROMPT GENERATOR                                             │
│ - Analyzes "profile editing" requirement                     │
│ - Finds related code: UserService, ProfileComponent          │
│ - Identifies patterns: How you name classes/functions        │
│ - Gathers examples: Similar features you already built       │
│ - Collects imports: Libraries you use                        │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ GENERATED PROMPT (Markdown File)                             │
│                                                               │
│ # Context for: Add user profile editing feature              │
│                                                               │
│ ## Project Structure                                         │
│ - TypeScript React app                                       │
│ - 45 components, 23 services                                 │
│                                                               │
│ ## Relevant Existing Code                                    │
│ ### UserService                                              │
│ ```typescript                                                │
│ class UserService {                                          │
│   async getUser() { ... }                                    │
│ }                                                            │
│ ```                                                          │
│                                                               │
│ ## Code Patterns You Follow                                  │
│ - Classes: PascalCase (UserService, ProfileComponent)        │
│ - Functions: camelCase (getUser, updateProfile)              │
│ - Common imports: React, axios, lodash                       │
│                                                               │
│ ## Task: Add profile editing                                 │
│ Requirements:                                                 │
│ 1. Follow existing UserService pattern                       │
│ 2. Use same styling as ProfileComponent                      │
│ 3. Include form validation                                   │
│                                                               │
│ ## Expected Output                                            │
│ - Complete TypeScript code                                   │
│ - Follows your conventions                                   │
│ - Integrates with existing services                          │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ YOU: Copy this prompt and paste into Claude/GPT-4            │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ AI GENERATES CODE                                            │
│ - Matches your naming: ProfileEditComponent                  │
│ - Uses your patterns: Similar to existing components         │
│ - Correct imports: Uses your libraries                       │
│ - Ready to integrate: Fits your architecture                 │
└─────────────────────────────────────────────────────────────┘
```

---

## Real Example

### Input: Your Requirement
```
"Add user profile editing feature with avatar upload"
```

### What The System Does

**Step 1: Parse Your Codebase**
```python
parser = TreeSitterParser("./my-app")
results = parser.parse_repository()

# Finds:
# - 12 TypeScript classes
# - 45 React components
# - 23 service files
# - All import statements
# - Code patterns
```

**Step 2: Analyze Requirement**
```python
# System extracts keywords: "user", "profile", "editing", "avatar", "upload"

# Searches codebase for matches:
# - Found: UserService (80% match)
# - Found: ProfileComponent (70% match)
# - Found: AvatarUpload (90% match!)
# - Found: updateUser() function (60% match)
```

**Step 3: Generate Prompt**
```python
prompt_gen = PromptGenerator(results, "./my-app")

prompt = prompt_gen.generate_prompt(
    requirement="Add user profile editing feature with avatar upload",
    context_type="feature",
    constraints=[
        "Use existing authentication",
        "Support JPG/PNG up to 5MB",
        "TypeScript with React hooks"
    ]
)
```

**Step 4: Prompt Contains**

1. **Project Overview**
   - "TypeScript React application"
   - "Uses React Hooks pattern"
   - "Has 45 components following component/service architecture"

2. **Related Code Found**
   ```typescript
   // Shows you existing AvatarUpload component
   class AvatarUpload extends Component {
     handleUpload(file: File) { ... }
   }

   // Shows you existing UserService
   class UserService {
     async updateUser(data: UserData) { ... }
   }
   ```

3. **Your Patterns**
   - Classes named: `UserService`, `ProfileComponent`, `AvatarUpload`
   - Functions named: `handleUpload`, `updateUser`, `validateForm`
   - Imports always use: `import { useState } from 'react'`

4. **Specific Task**
   ```
   Create ProfileEditComponent that:
   1. Follows the pattern in AvatarUpload
   2. Uses UserService.updateUser()
   3. Includes form validation
   4. Matches existing component style
   ```

---

## Usage (Simple)

### Quick Start

```python
# 1. Parse your code
from parsers.treesitter import TreeSitterParser, PromptGenerator

parser = TreeSitterParser("./your-app")
results = parser.parse_repository()

# 2. Generate prompt
prompt_gen = PromptGenerator(results, "./your-app")

prompt = prompt_gen.generate_prompt(
    requirement="Add dark mode toggle",
    context_type="feature"
)

# 3. Save it
prompt_gen.save_prompt(prompt, "./dark_mode_prompt.md")

# 4. Use it
# Open dark_mode_prompt.md
# Copy all text
# Paste into Claude/GPT-4
# Get perfect code!
```

### What You Get

A markdown file containing:
```markdown
# Code Generation Request

## 📁 Your Project
- TypeScript with React
- 156 files analyzed
- Uses styled-components

## 📝 Related Code
[Shows your existing theme toggle code]

## 🎨 Your Patterns
- You name components: ThemeToggle, DarkModeSwitch
- You use hooks: useTheme, useDarkMode
- You import from: 'styled-components', 'react'

## 🎯 Task
Add dark mode toggle following your existing pattern

## 📤 Output
Generate TypeScript component matching your style
```

---

## Use Cases

### 1. New Feature
```python
requirement = "Add password reset via email"
context_type = "feature"
```
→ Gets related auth code, email service examples

### 2. Bug Fix
```python
requirement = "Fix login token not persisting"
context_type = "bugfix"
related_files = ["auth.service.ts"]
```
→ Shows auth code, token handling, storage logic

### 3. Refactor
```python
requirement = "Extract validation into reusable hook"
context_type = "refactor"
```
→ Shows existing hooks, validation patterns

### 4. Tests
```python
requirement = "Write tests for auth service"
context_type = "test"
```
→ Shows testing patterns, mock examples

---

## Benefits

### Without This Feature
```
You: "Claude, add a user profile editing feature"

Claude: "Here's a generic profile editor..."
[Code doesn't match your style]
[Uses different libraries]
[Doesn't integrate with your services]
[You spend hours adapting it]
```

### With This Feature
```
You: [Paste generated prompt with full context]

Claude: "Based on your UserService and ProfileComponent patterns,
        here's ProfileEditComponent that integrates perfectly..."
[Code matches your naming]
[Uses your libraries]
[Integrates with existing services]
[Works immediately!]
```

---

## Technical Details

### What Gets Analyzed

1. **Code Structure**
   - Classes and their inheritance
   - Functions and their parameters
   - Interfaces and types
   - Imports and dependencies

2. **Patterns**
   - Naming conventions (PascalCase, camelCase)
   - File organization
   - Common imports
   - Code style

3. **Context**
   - Related existing code
   - Similar implementations
   - Dependencies
   - Integration points

### Languages Supported

All languages Tree Sitter supports:
- Python, JavaScript, TypeScript
- Java, Go, Rust
- C/C++, C#, Ruby, PHP
- And more!

### Output Format

Generated prompts are **structured Markdown** with:
- Headers for different sections
- Code blocks with syntax highlighting
- Lists for patterns and requirements
- Clear task specifications

---

## Examples

### Example 1: Simple Feature

**Input:**
```python
requirement = "Add logout button"
```

**Output Prompt Includes:**
- Your existing auth code
- How you handle logout in other places
- Your button component patterns
- Navigation patterns after logout

### Example 2: Complex Feature

**Input:**
```python
requirement = "Add multi-step form wizard for user onboarding"
constraints = [
    "Save progress between steps",
    "Validate each step",
    "Show progress indicator"
]
```

**Output Prompt Includes:**
- Your existing form components
- Your validation patterns
- Your state management approach
- Similar multi-step flows you have
- Progress indicator components

### Example 3: Bug Fix

**Input:**
```python
requirement = "Fix form not clearing after submit"
context_type = "bugfix"
related_files = ["ContactForm.tsx"]
```

**Output Prompt Includes:**
- The actual ContactForm code
- How other forms handle reset
- Your form state management
- Submit handler patterns

---

## Integration

### With Existing System

The prompt generator works alongside the existing code intelligence:

```python
# Existing: Context for understanding
from context_builder import ContextAssembler
context = assembler.assemble_context("Fix login")

# New: Prompts for code generation
from parsers.treesitter import PromptGenerator
prompt = prompt_gen.generate_prompt("Fix login")
```

### Workflow

```
1. Developer has requirement
   ↓
2. Parse codebase (once)
   ↓
3. Generate prompt (seconds)
   ↓
4. Give to AI tool
   ↓
5. Get context-aware code
   ↓
6. Integrate immediately
```

---

## Summary

The **Requirements to Prompt** feature:

✅ **Automates** context gathering from your codebase
✅ **Analyzes** code patterns and conventions
✅ **Generates** comprehensive prompts for AI tools
✅ **Ensures** generated code matches your style
✅ **Saves** hours of manual work
✅ **Works** with any AI coding tool

**Result:** AI-generated code that feels like you wrote it!

---

## Try It Now

```bash
# Run the examples
python3 example_prompt_generation.py

# Check the generated prompts
ls -la ./data/treesitter/prompts/

# Use one with Claude/GPT-4
cat ./data/treesitter/prompts/feature_user_profile.md
```

**See:** `REQUIREMENTS_TO_PROMPT_GUIDE.md` for complete documentation
