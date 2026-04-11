# 🚀 First Run Instructions

## ✅ System is Running!

Your Code Intelligence System is now operational at:
**http://localhost:8000**

---

## 📋 Step-by-Step Guide

### Step 1: Index the Demo Repository

1. **Go to the "Connect Repository" tab** (should be active by default)

2. **Enter the repository path:**
   ```
   ./demo-repo
   ```
   *(This is already filled in for you)*

3. **Click "🔍 Index Repository"**

4. **Wait 30-60 seconds** while the system:
   - Parses Flutter code (mobile)
   - Parses React code (web)
   - Parses NestJS code (backend)
   - Parses Terraform (infrastructure)
   - Parses Kubernetes YAML (deployment)
   - Builds dependency graph
   - Creates vector embeddings

5. **You should see:**
   ```
   ✅ Repository Indexed Successfully!
   Components: 14
   Relationships: 15
   API Endpoints: 4
   ```

---

### Step 2: Explore the Code Ontology

1. **Go to the "Code Ontology" tab**

2. **Click "🔄 Refresh Graph"**

3. **You'll see an interactive visualization with:**
   - **Red nodes** = Mobile (Flutter) components
   - **Teal nodes** = Web (React) components
   - **Blue nodes** = Backend (NestJS) services
   - **Green nodes** = Data layer
   - **Yellow nodes** = Infrastructure

4. **Click on any node** to see:
   - Component details
   - Dependencies (what it uses)
   - Dependents (what uses it)
   - Source file location

5. **Scroll down** to see components organized by layer

---

### Step 3: Generate Your First AI Prompt

1. **Go to the "Requirements" tab**

2. **Try an example** by clicking on one of the cards:
   - **Password Reset** - Add password reset feature
   - **Two-Factor Auth** - Implement 2FA
   - **Login Timeout** - Fix session timeout bug

3. **Or enter your own:**
   - **Type**: Choose from dropdown (New Feature, Bug Fix, etc.)
   - **Title**: `Add password reset functionality`
   - **Description**:
     ```
     Implement email-based password reset:
     - User enters email
     - System sends reset link (1 hour expiry)
     - User clicks link and resets password
     - Password is updated securely
     ```

4. **Click "🤖 Generate AI Prompt"**

5. **You'll get a comprehensive prompt that includes:**
   - **Mobile layer**: LoginScreen, AuthService (Flutter)
   - **Web layer**: LoginPage, useAuth hook (React)
   - **Backend layer**: AuthController, AuthService (NestJS)
   - **Data layer**: UserRepository, User entity
   - **Infrastructure**: JWT secrets, environment variables
   - **Impact analysis**: What components are affected

6. **Click "📋 Copy to Clipboard"**

7. **Paste into Cursor or any AI coding tool!**

---

### Step 4: Try Semantic Search

1. **Go to the "Search" tab**

2. **Try searching for:**
   - `authentication`
   - `login`
   - `user profile`
   - `JWT token`

3. **See all related components across all layers!**

---

### Step 5: View Statistics

1. **Go to the "Statistics" tab**

2. **See:**
   - Total components by layer
   - API endpoints count
   - Dependency relationships
   - Repository metrics

---

## 🎯 What the Demo Repository Contains

The demo shows a **realistic authentication flow** across all layers:

### 📱 Mobile (Flutter)
- `LoginScreen` - User login interface
- `ProfileScreen` - User profile display
- `AuthService` - Authentication API client
- `ApiClient` - HTTP client with auto-refresh

### 🌐 Web (React)
- `LoginPage` - Web login interface
- `ProfilePage` - Web profile display
- `useAuth` - Authentication hook
- `apiClient` - Axios client with interceptors

### ⚙️ Backend (NestJS)
- `AuthController` - API routes (login, register, profile)
- `AuthService` - Business logic (validation, JWT generation)
- `UserRepository` - Database access
- `User` entity - Database model
- DTOs for validation

### 🏗️ Infrastructure
- **Terraform**: ECS service configuration
- **Kubernetes**: Deployment with secrets and ConfigMaps

### 🔄 Full Flow Traced
```
LoginScreen (Mobile)
    ↓ API call
POST /auth/login (Backend)
    ↓ calls
AuthService.login()
    ↓ calls
UserRepository.findByEmail()
    ↓ returns
JWT Token ← ← ← ← ← ←
```

---

## 💡 Example Use Cases

### Use Case 1: Understand How Login Works

**Query:** `How does user authentication work?`

**Result:** System shows you the complete flow:
- Mobile screens that handle login
- Web pages that handle login
- Backend controllers and services
- Database entities
- JWT token generation
- Environment variables for secrets

### Use Case 2: Add a New Feature

**Requirement:** `Add "Remember Me" functionality`

**System provides:**
- All files that need modification
- Existing patterns to follow
- Related components
- Impact analysis
- Perfect AI prompt

### Use Case 3: Fix a Bug

**Bug:** `Users getting logged out too quickly`

**System shows:**
- Token expiry configuration
- Refresh token logic
- All components involved in session management
- Infrastructure settings

### Use Case 4: Safe Refactoring

**Before changing `AuthService`:**

1. Run impact analysis
2. See what depends on it:
   - LoginScreen (mobile)
   - LoginPage (web)
   - AuthController (backend)
   - 5 other components

3. Know what to test after changes

---

## 🔥 Pro Tips

### 1. Specific Queries Work Best

✅ **Good:**
- "Fix email validation in user registration"
- "Add password reset with email verification"
- "Debug JWT token expiration issue"

❌ **Bad:**
- "Fix bug"
- "Make it better"
- "Help"

### 2. Use the Graph Visualization

- Click nodes to explore
- Follow the arrows to understand flow
- Filter by layer to reduce clutter

### 3. Always Check Impact First

Before making changes:
1. Go to Requirements tab
2. Enter affected components
3. See impact analysis
4. Know what you're breaking!

### 4. Copy the ENTIRE Prompt

Don't edit the generated prompt - it's optimized for AI tools. Copy everything and paste it into Cursor.

### 5. Use Examples as Templates

Click the example cards and modify them for your needs.

---

## 🐛 Troubleshooting

### "Repository not found" error
- Make sure you entered: `./demo-repo` (with the dot-slash)
- Or use absolute path: `/Users/venureddy/Downloads/ParseCodeBase/demo-repo`

### Graph not showing
- Make sure you indexed the repository first
- Click "Refresh Graph"
- Check browser console for errors

### Slow performance
- First indexing takes 30-60 seconds (normal)
- Graph rendering can take a few seconds
- Large repos (>1000 files) will be slower

### Server errors
- Check the terminal where you ran `./start.sh`
- Look for error messages
- Server restarts automatically on code changes

---

## 📚 Next Steps

### After Exploring the Demo

1. **Index Your Real Repository**
   - Enter your actual project path
   - Wait for indexing
   - Explore your codebase!

2. **Generate Real Prompts**
   - Enter your actual requirements
   - Get context for real tasks
   - Use with Cursor for implementation

3. **Use CLI Tools**
   ```bash
   # Open a new terminal (keep server running)
   python -m code_intelligence query \
     --repo ./demo-repo \
     --query "Your question here"
   ```

4. **Read Full Documentation**
   - `USAGE_GUIDE.md` - Comprehensive guide
   - `DEPLOYMENT_COMPLETE.md` - System overview
   - `example_usage.py` - Code examples

---

## 🎊 You're All Set!

The system is:
- ✅ Running on http://localhost:8000
- ✅ Demo repository ready
- ✅ All features operational
- ✅ Ready for your repos!

**Enjoy AI-powered code intelligence!** 🚀

---

**Need help?** Check the other documentation files or the server console output.
