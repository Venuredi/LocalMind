# Requirements to Prompt Feature - Complete Guide

## Overview

The **Requirements to Prompt** feature transforms user requirements into context-rich prompts for AI code generation tools by leveraging the Tree Sitter code ontology.

### What It Does

1. **Analyzes your codebase** using Tree Sitter parser
2. **Extracts relevant context** based on your requirement
3. **Generates comprehensive prompts** for AI tools
4. **Includes existing patterns** so AI follows your conventions
5. **Outputs ready-to-use prompts** for Claude, GPT-4, Copilot, etc.

---

## How It Works

### Architecture

```
┌─────────────────┐
│  User Provides  │
│  Requirement    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Tree Sitter    │
│  Parses Code    │
│  → Ontology     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Analyze        │
│  Requirement    │
│  Find Relevant  │
│  Context        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Generate       │
│  AI Prompt      │
│  with Context   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  User Feeds to  │
│  Claude/GPT/etc │
│  Gets Code      │
└─────────────────┘
```

### Step-by-Step Process

#### Step 1: Parse Codebase
```python
from parsers.treesitter import TreeSitterParser

parser = TreeSitterParser("./your-repo")
results = parser.parse_repository()
```

**What happens:**
- Tree Sitter analyzes all source files
- Extracts classes, functions, imports, etc.
- Builds ontology graph of code structure
- Identifies patterns and conventions

#### Step 2: Initialize Prompt Generator
```python
from parsers.treesitter.prompt_generator import PromptGenerator

prompt_gen = PromptGenerator(results, "./your-repo")
```

**What happens:**
- Loads the ontology data
- Prepares context extraction
- Ready to analyze requirements

#### Step 3: Provide Requirement
```python
requirement = "Add user profile editing feature with avatar upload"
```

**The requirement can be:**
- New feature request
- Bug fix description
- Refactoring task
- Test requirement
- Documentation need

#### Step 4: Generate Prompt
```python
prompt = prompt_gen.generate_prompt(
    requirement=requirement,
    context_type="feature",
    constraints=[
        "Must work with existing authentication",
        "Support images up to 5MB"
    ]
)
```

**What happens:**
- Analyzes requirement keywords
- Finds relevant code entities
- Extracts similar implementations
- Identifies code patterns
- Gathers dependencies
- Formats everything into structured prompt

#### Step 5: Use with AI Tool
```python
prompt_gen.save_prompt(prompt, "./prompt.md")
# Copy content to Claude, GPT-4, Copilot, etc.
```

---

## What Gets Included in the Prompt

### 1. Project Context
- Total files and languages
- Codebase structure
- Entity counts (classes, functions, etc.)

**Example:**
```markdown
## 📁 Project Context

**Total Files:** 8
**Languages:** typescript

**Codebase Structure:**
- functions: 12
- imports: 15
```

### 2. Relevant Existing Code
- Classes related to requirement
- Functions/methods that match
- Actual source code snippets
- File locations

**Example:**
```markdown
## 📝 Relevant Existing Code

### Related Classes

#### AuthController
- **File:** `src/auth/auth.controller.ts:15`
- **Language:** typescript

```typescript
@Controller('auth')
export class AuthController {
  constructor(private authService: AuthService) {}

  @Post('login')
  async login(@Body() loginDto: LoginDto) {
    return this.authService.login(loginDto);
  }
}
```
```

### 3. Code Patterns & Conventions
- Naming patterns from your code
- Common imports used
- File structure organization

**Example:**
```markdown
## 🎨 Code Patterns & Conventions

### Naming Conventions
- **Classes:** AuthController, UserService, LoginScreen
- **Functions:** handleLogin, validateToken, refreshSession

### Common Imports
- `import { Controller, Post } from '@nestjs/common'`
- `import { AuthService } from './auth.service'`
```

### 4. Example Implementations
- Similar code from your codebase
- Demonstrates style and approach
- Shows integration patterns

### 5. Dependencies & Imports
- Required packages
- Common imports for this type of work
- Integration points

### 6. Technical Constraints
- Your specified requirements
- Must-have features
- Compatibility requirements

### 7. Task Specification
- Clear goal statement
- Step-by-step requirements
- Quality expectations

### 8. Expected Output Format
- What the AI should return
- Code structure
- File organization
- Documentation needs

---

## Usage Examples

### Example 1: New Feature

```python
from parsers.treesitter import TreeSitterParser
from parsers.treesitter.prompt_generator import PromptGenerator

# Parse codebase
parser = TreeSitterParser("./my-app")
results = parser.parse_repository()

# Generate prompt
prompt_gen = PromptGenerator(results, "./my-app")

prompt = prompt_gen.generate_prompt(
    requirement="Add password reset functionality via email",
    context_type="feature",
    constraints=[
        "Use existing email service",
        "Token expires in 1 hour",
        "Must be secure against timing attacks"
    ]
)

# Save and use
prompt_gen.save_prompt(prompt, "./prompts/password_reset.md")
```

### Example 2: Bug Fix

```python
prompt = prompt_gen.generate_prompt(
    requirement="Fix login token not persisting after page refresh",
    context_type="bugfix",
    related_files=[
        "src/auth/auth.service.ts",
        "src/hooks/useAuth.ts"
    ]
)
```

### Example 3: Refactoring

```python
prompt = prompt_gen.generate_prompt(
    requirement="Extract authentication logic into reusable hook",
    context_type="refactor",
    constraints=[
        "Maintain backward compatibility",
        "Follow React hooks best practices",
        "Improve testability"
    ]
)
```

### Example 4: Test Writing

```python
prompt = prompt_gen.generate_prompt(
    requirement="Write comprehensive tests for user authentication flow",
    context_type="test",
    related_files=["src/auth/"],
    constraints=[
        "Use Jest and React Testing Library",
        "Cover edge cases",
        "Mock external dependencies"
    ]
)
```

### Example 5: Batch Generation

```python
requirements = [
    {
        "requirement": "Add dark mode toggle",
        "context_type": "feature",
        "constraints": ["Use CSS variables", "Save to localStorage"]
    },
    {
        "requirement": "Implement rate limiting on API endpoints",
        "context_type": "feature",
        "constraints": ["100 requests per hour per user"]
    },
    {
        "requirement": "Add input validation to all forms",
        "context_type": "feature",
        "constraints": ["Use Yup schema", "Show inline errors"]
    }
]

files = prompt_gen.generate_batch_prompts(
    requirements=requirements,
    output_dir="./prompts"
)
```

---

## Using with AI Tools

### Option 1: Claude (Web or API)

1. Run prompt generation:
```bash
python3 example_prompt_generation.py
```

2. Open generated file:
```bash
cat ./data/treesitter/prompts/feature_user_profile.md
```

3. Copy entire content

4. Paste into Claude:
- Go to claude.ai
- Start new conversation
- Paste the prompt
- Claude generates code with full context

### Option 2: ChatGPT / GPT-4

Same process as Claude - copy the generated prompt and paste into ChatGPT.

### Option 3: GitHub Copilot

1. Open the generated .md file in VS Code
2. Use as reference while coding
3. Copilot will use context from open files
4. Ask Copilot specific questions referencing the prompt

### Option 4: Cursor

1. Open generated prompt in Cursor
2. Use Cmd+K or Cmd+L to chat
3. Reference the prompt sections
4. Cursor generates code matching your patterns

### Option 5: API Integration

```python
import openai

# Read generated prompt
with open("./prompts/feature.md") as f:
    prompt = f.read()

# Send to API
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "You are a code generation assistant."},
        {"role": "user", "content": prompt}
    ]
)

code = response.choices[0].message.content
print(code)
```

---

## Benefits

### 1. Context-Aware Code Generation
AI knows your:
- Existing code structure
- Naming conventions
- Common patterns
- Dependencies

### 2. Consistency
Generated code:
- Follows your style
- Matches existing patterns
- Integrates seamlessly
- Uses same libraries

### 3. Time Savings
- No manual context gathering
- Automated code analysis
- Ready-to-use prompts
- Batch generation support

### 4. Quality
- Based on actual codebase
- Includes best practices
- Shows working examples
- Specifies constraints

### 5. Flexibility
- Multiple context types (feature, bugfix, refactor, test)
- Custom constraints
- Related files specification
- Pattern inclusion control

---

## Advanced Features

### Custom Analysis

```python
# Analyze requirement first
analysis = prompt_gen._analyze_requirement(
    "Add user authentication",
    related_files=["src/auth/"]
)

print("Relevant classes:", [c[0]['name'] for c in analysis['relevant_classes']])
print("Relevant functions:", [f[0]['name'] for f in analysis['relevant_functions']])
print("Language:", analysis['language'])
```

### Selective Context

```python
# Generate without patterns
prompt = prompt_gen.generate_prompt(
    requirement="...",
    include_patterns=False,  # Skip pattern analysis
    include_examples=False   # Skip example code
)
```

### File-Specific Context

```python
# Focus on specific files
prompt = prompt_gen.generate_prompt(
    requirement="...",
    related_files=[
        "src/auth/auth.service.ts",
        "src/users/user.repository.ts"
    ]
)
```

---

## Best Practices

### 1. Clear Requirements
✅ Good:
```
"Add user profile editing with avatar upload supporting JPG/PNG up to 5MB"
```

❌ Bad:
```
"Make profile better"
```

### 2. Specify Constraints
Include:
- Technology requirements
- Performance limits
- Security requirements
- Compatibility needs

### 3. Use Appropriate Context Type
- `feature` - New functionality
- `bugfix` - Fixing issues
- `refactor` - Improving code
- `test` - Writing tests

### 4. Reference Related Files
Help the system find relevant context:
```python
related_files=[
    "src/auth/",
    "src/services/api.ts"
]
```

### 5. Review Generated Prompts
Before using with AI:
- Check included code is relevant
- Verify constraints are clear
- Ensure examples are appropriate

---

## Troubleshooting

### No Relevant Code Found

**Problem:** Prompt says "No directly related code found"

**Solution:**
- You're creating something new
- Specify related_files manually
- Look at similar features as reference

### Wrong Language Detected

**Problem:** Shows wrong language examples

**Solution:**
- Parse specific directories
- Specify language in requirement
- Use related_files to focus

### Too Much Context

**Problem:** Prompt is too long

**Solution:**
```python
prompt = prompt_gen.generate_prompt(
    requirement="...",
    include_patterns=False,
    include_examples=False
)
```

### Missing Dependencies

**Problem:** Important imports not included

**Solution:**
- Ensure related files are specified
- Check if files were parsed
- Manually add to constraints

---

## Integration with Existing System

The prompt generator integrates with the existing code intelligence system:

```python
# Use with existing index
from code_intelligence.context_builder import ContextAssembler

assembler = ContextAssembler("./data/index.json", "./repo")
context = assembler.assemble_context("Add user profile")

# Convert to Tree Sitter for prompt generation
parser = TreeSitterParser("./repo")
results = parser.parse_repository()

prompt_gen = PromptGenerator(results, "./repo")
prompt = prompt_gen.generate_prompt("Add user profile editing")
```

---

## Complete Workflow Example

```python
#!/usr/bin/env python3
"""Complete workflow: Requirement → Prompt → AI → Code"""

from parsers.treesitter import TreeSitterParser
from parsers.treesitter.prompt_generator import PromptGenerator

# 1. Define your requirement
requirement = """
Add a user dashboard with:
- Summary statistics
- Recent activity feed
- Quick action buttons
"""

constraints = [
    "Use React with TypeScript",
    "Follow existing component patterns",
    "Integrate with current API",
    "Mobile responsive design"
]

# 2. Parse codebase
print("Parsing codebase...")
parser = TreeSitterParser("./my-app")
results = parser.parse_repository()

# 3. Generate prompt
print("Generating AI prompt...")
prompt_gen = PromptGenerator(results, "./my-app")

prompt = prompt_gen.generate_prompt(
    requirement=requirement,
    context_type="feature",
    constraints=constraints,
    related_files=[
        "src/components/",
        "src/services/api.ts"
    ]
)

# 4. Save prompt
output_file = "./prompts/user_dashboard.md"
prompt_gen.save_prompt(prompt, output_file)

print(f"\n✅ Prompt ready: {output_file}")
print("\nNext steps:")
print("1. Open the prompt file")
print("2. Copy content to Claude/GPT-4")
print("3. Get your code!")
```

---

## API Reference

### PromptGenerator

```python
class PromptGenerator:
    def __init__(self, ontology_data: Dict, repo_path: str)

    def generate_prompt(
        requirement: str,
        context_type: str = "feature",
        related_files: Optional[List[str]] = None,
        constraints: Optional[List[str]] = None,
        include_patterns: bool = True,
        include_examples: bool = True
    ) -> str

    def save_prompt(prompt: str, output_path: str)

    def generate_batch_prompts(
        requirements: List[Dict],
        output_dir: str
    ) -> List[str]
```

### Parameters

- **requirement**: Description of what to implement
- **context_type**: One of: feature, bugfix, refactor, test
- **related_files**: List of file paths to focus on
- **constraints**: Technical requirements/limitations
- **include_patterns**: Include code pattern analysis
- **include_examples**: Include example implementations

---

## Summary

The **Requirements to Prompt** feature bridges the gap between:
1. Your natural language requirements
2. Your existing codebase context
3. AI code generation tools

It automates the tedious process of gathering context, ensuring AI-generated code:
- Matches your style
- Follows your patterns
- Integrates seamlessly
- Is production-ready

**Start using it now:**
```bash
python3 example_prompt_generation.py
```

The generated prompts give AI tools everything they need to write code that fits perfectly into your codebase!
