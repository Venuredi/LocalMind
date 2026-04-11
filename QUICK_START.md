# Quick Start Guide

Get the Code Intelligence System running in 3 simple steps!

## 🚀 Installation & Setup

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Start the System

#### On macOS/Linux:
```bash
./start.sh
```

#### On Windows:
```bash
start.bat
```

#### Or manually:
```bash
cd code-intelligence
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

### Step 3: Open Web Interface

Open your browser and navigate to:
```
http://localhost:8000
```

## 🎯 First-Time Usage

### 1. Index the Demo Repository

1. Go to the **"Connect Repository"** tab
2. Enter the path: `./demo-repo`
3. Click **"Index Repository"**
4. Wait for indexing to complete (30-60 seconds)

### 2. Explore the Code Ontology

1. Go to the **"Code Ontology"** tab
2. Click **"Refresh Graph"** to visualize the codebase
3. Click on nodes to see component details
4. Filter by layer to focus on specific parts

### 3. Generate AI Prompts

1. Go to the **"Requirements"** tab
2. Click on an example or enter your own requirement
3. Click **"Generate AI Prompt"**
4. Copy the prompt and paste it into Cursor or similar AI tools

## 📖 Example Workflow

### Scenario: Add Password Reset Feature

1. **Connect Repository**
   - Index your repository

2. **Input Requirement**
   - Type: "New Feature"
   - Title: "Add password reset functionality"
   - Description: "Users should be able to reset their password via email"

3. **Generate Prompt**
   - Click "Generate AI Prompt"
   - System analyzes relevant code across all layers
   - Generates comprehensive prompt with:
     - Flutter LoginScreen and AuthService
     - React LoginPage and useAuth hook
     - NestJS AuthController and AuthService
     - UserRepository and database schema
     - Environment variables and secrets
     - Impact analysis

4. **Use with Cursor**
   - Copy the generated prompt
   - Open Cursor
   - Paste the prompt
   - Let Cursor implement with full context!

## 🔧 Command Line Interface

You can also use the CLI:

```bash
# Index repository
python -m code_intelligence index --repo ./demo-repo

# Query for context
python -m code_intelligence query \
  --repo ./demo-repo \
  --query "Fix login issue"

# Get execution flow
python -m code_intelligence flow \
  --repo ./demo-repo \
  --component LoginScreen

# Impact analysis
python -m code_intelligence impact \
  --component AuthService \
  --component UserRepository

# Show statistics
python -m code_intelligence stats
```

## 📊 What Gets Indexed?

The system understands:

### 📱 **Mobile (Flutter/Dart)**
- Screens and widgets
- Services and API clients
- Navigation flows
- State management

### 🌐 **Web (React/TypeScript)**
- Pages and components
- Hooks and context
- API calls
- Routing

### ⚙️ **Backend (NestJS/TypeScript)**
- Controllers and routes
- Services and business logic
- DTOs and validation
- Repositories and entities

### 🏗️ **Infrastructure**
- Terraform resources
- Kubernetes deployments
- ConfigMaps and secrets
- Environment variables

## 🎨 Features

✅ **Cross-Layer Intelligence** - Understands relationships across all layers
✅ **Semantic Search** - Find components by meaning, not just keywords
✅ **Impact Analysis** - Know what breaks before you change it
✅ **AI-Ready Prompts** - Perfect context for Cursor, Copilot, etc.
✅ **Visual Graph** - Interactive dependency visualization
✅ **Infrastructure Aware** - Tracks env vars, secrets, configs

## 🆘 Troubleshooting

### Port Already in Use

If port 8000 is busy:
```bash
cd code-intelligence
python -m uvicorn api.main:app --port 8001
```

### Import Errors

Make sure you're in the right directory:
```bash
cd /path/to/ParseCodeBase
pip install -r requirements.txt
```

### Repository Not Found

Use absolute paths or paths relative to ParseCodeBase:
```bash
./demo-repo          # ✅ Correct
../other-repo        # ✅ Correct
/full/path/to/repo   # ✅ Correct
demo-repo            # ❌ Wrong (missing ./)
```

## 📚 Next Steps

1. **Index Your Real Repository** - Point it to your actual codebase
2. **Try Different Queries** - Explore features, bugs, refactoring
3. **Use with AI Tools** - Copy prompts to Cursor for implementation
4. **Check Impact** - Always check what's affected before changes

## 🎓 Learn More

- **Full Documentation**: See `USAGE_GUIDE.md`
- **Examples**: Check `example_usage.py`
- **API Docs**: Visit `http://localhost:8000/docs`

## 💡 Tips

1. **Better Queries = Better Context**
   - ✅ "Fix email validation in registration"
   - ❌ "Fix bug"

2. **Use Examples**
   - Click example cards in the Requirements tab
   - Modify them for your needs

3. **Check Impact First**
   - Before refactoring, use impact analysis
   - See what components depend on what you're changing

4. **Layer Filtering**
   - Focus on specific layers when visualizing
   - Reduces clutter for large codebases

## 🎉 You're Ready!

Start exploring your codebase with AI-powered intelligence!

---

**Need Help?** Check out `USAGE_GUIDE.md` or `README.md`
