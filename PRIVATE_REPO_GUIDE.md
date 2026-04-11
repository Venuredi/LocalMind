# 🔒 Private Repository Guide

Complete guide for using Code Intelligence System with private repositories.

---

## 🎯 Quick Answer

**The system works with LOCAL repositories only.**

You need to:
1. ✅ Clone your private repo to your machine first
2. ✅ Point the system to the local directory
3. ✅ That's it!

---

## 📋 Step-by-Step Guide

### Step 1: Clone Your Private Repository

Choose your preferred authentication method:

#### **Option A: SSH (Recommended for Private Repos)**

```bash
# If you haven't set up SSH keys yet
ssh-keygen -t ed25519 -C "your_email@example.com"

# Copy your public key
cat ~/.ssh/id_ed25519.pub

# Add to GitHub/GitLab:
# GitHub: Settings → SSH and GPG keys → New SSH key
# GitLab: Preferences → SSH Keys

# Clone your private repo
cd /Users/venureddy/Downloads/
git clone git@github.com:your-org/your-private-repo.git
```

#### **Option B: Personal Access Token**

```bash
# Create token:
# GitHub: Settings → Developer settings → Tokens → Generate new token
# Permissions needed: repo (full control)

# Clone with token
cd /Users/venureddy/Downloads/
git clone https://YOUR_TOKEN@github.com/your-org/your-private-repo.git
```

#### **Option C: GitHub CLI**

```bash
# Install (macOS)
brew install gh

# Authenticate
gh auth login

# Clone
cd /Users/venureddy/Downloads/
gh repo clone your-org/your-private-repo
```

### Step 2: Index the Local Repository

**Web Interface Method:**

1. Open http://localhost:8000
2. Go to "Connect Repository" tab
3. Enter local path:
   ```
   /Users/venureddy/Downloads/your-private-repo
   ```
4. Click "Index Repository"
5. Wait for completion

**CLI Method:**

```bash
python -m code_intelligence index \
  --repo /Users/venureddy/Downloads/your-private-repo
```

### Step 3: Use It!

Once indexed, you can:
- ✅ Visualize code ontology
- ✅ Search semantically
- ✅ Generate AI prompts
- ✅ Analyze impact

---

## 🔄 Keep It Updated

### Manual Update

```bash
# Pull latest changes
cd /Users/venureddy/Downloads/your-private-repo
git pull

# Re-index
cd /Users/venureddy/Downloads/ParseCodeBase
python -m code_intelligence index \
  --repo /Users/venureddy/Downloads/your-private-repo
```

### Auto Update Script

Use the provided script:

```bash
./update_and_index.sh /Users/venureddy/Downloads/your-private-repo
```

This will:
1. Pull latest changes from git
2. Automatically re-index
3. Update the code intelligence database

---

## 🏢 Enterprise Scenarios

### Multiple Private Repos

You can index multiple repositories:

```bash
# Index repo 1
python -m code_intelligence index --repo ~/work/api-service

# Index repo 2 (overwrites previous)
python -m code_intelligence index --repo ~/work/mobile-app
```

**Note:** Currently, the system indexes one repository at a time. The last indexed repo is the active one.

### Monorepo with Multiple Apps

Perfect for monorepos:

```
my-monorepo/
├── apps/
│   ├── mobile/          # Flutter
│   ├── web/             # React
│   └── admin/           # React
├── packages/
│   ├── backend/         # NestJS
│   └── shared/          # Common code
└── infra/               # Terraform + K8s
```

Just index the root:

```bash
python -m code_intelligence index --repo ~/work/my-monorepo
```

The system will parse all layers automatically!

### Microservices Architecture

For separate service repos:

```
~/work/
├── auth-service/        # NestJS
├── payment-service/     # NestJS
├── notification-service/# NestJS
└── mobile-app/          # Flutter
```

Index each service separately, or create a parent folder:

```bash
# Option 1: Index individually
python -m code_intelligence index --repo ~/work/auth-service

# Option 2: Move all to one folder
mkdir ~/work/my-platform
mv auth-service payment-service notification-service mobile-app ~/work/my-platform/

# Index the platform
python -m code_intelligence index --repo ~/work/my-platform
```

---

## 🔐 Security Best Practices

### 1. Never Commit Credentials

The system only reads code, but ensure:

```bash
# .gitignore should include
.env
.env.local
credentials.json
secrets.yaml
*.pem
*.key
```

### 2. Local Analysis Only

- ✅ All analysis happens **locally** on your machine
- ✅ No code is sent to external servers
- ✅ Your code stays private

### 3. API Keys (Optional)

If you want semantic enrichment with LLM:

```bash
# Optional: Set OpenAI key for better semantic analysis
export OPENAI_API_KEY=your_key_here

# Start server
./start.sh
```

**Note:** The system works fine without API keys using rule-based analysis.

---

## 🌐 Remote Access (Optional)

Want to access from other machines on your network?

### Expose Locally

```bash
# Start server accessible from network
cd code-intelligence
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000
```

Now accessible at: `http://YOUR_IP:8000`

### SSH Tunnel (Secure)

```bash
# From remote machine
ssh -L 8000:localhost:8000 your-username@your-dev-machine

# Access on remote machine
http://localhost:8000
```

### Deploy to Private Server

You can deploy the system to a private server:

```bash
# On your server
git clone your-code-intelligence-repo
cd ParseCodeBase
pip install -r requirements.txt

# Run with systemd or supervisor
# Access via: https://code-intel.yourcompany.com
```

---

## 📊 Supported Repository Types

### ✅ Fully Supported

- **Flutter/Dart** - Mobile apps
- **React/TypeScript** - Web apps
- **NestJS/TypeScript** - Backend APIs
- **Terraform/HCL** - Infrastructure as code
- **Kubernetes/YAML** - Deployments

### 🔧 Partially Supported

The parsers are regex-based, so they work with:
- **Next.js** (TypeScript/React)
- **Angular** (TypeScript)
- **Vue** (TypeScript)
- **Express** (TypeScript)
- **Node.js** (TypeScript)

### 🔜 Extendable

You can add parsers for:
- Python (Django, FastAPI)
- Java (Spring Boot)
- Go
- Rust
- Any language!

---

## 💡 Real-World Examples

### Example 1: SaaS Product

```
Structure:
/Users/you/work/my-saas/
├── apps/
│   ├── mobile/           (Flutter)
│   ├── web/              (React)
│   └── admin/            (React)
├── services/
│   ├── api/              (NestJS)
│   ├── auth/             (NestJS)
│   └── billing/          (NestJS)
└── infrastructure/
    ├── terraform/
    └── k8s/

Index:
python -m code_intelligence index --repo /Users/you/work/my-saas

Result:
- All apps analyzed
- All services mapped
- Cross-layer dependencies tracked
- Infrastructure aware
```

### Example 2: Client Project

```
Structure:
/Users/you/clients/acme-corp/
├── mobile-app/           (Flutter)
└── backend/              (NestJS)

Index:
python -m code_intelligence index --repo /Users/you/clients/acme-corp

Use Case:
"Add payment processing"
→ System shows relevant code in mobile + backend
→ Generate prompt
→ Paste in Cursor
→ Implement!
```

### Example 3: Open Source Contribution

```bash
# Clone the repo you want to contribute to
git clone git@github.com:some-org/open-source-project.git

# Index it
python -m code_intelligence index --repo ./open-source-project

# Understand the codebase
# Find where to make changes
# Generate context for your PR
```

---

## 🚀 Quick Reference

### Authentication Methods

| Method | Use Case | Command |
|--------|----------|---------|
| SSH | Private repos (recommended) | `git clone git@github.com:org/repo.git` |
| HTTPS + Token | CI/CD, automation | `git clone https://token@github.com/org/repo.git` |
| GitHub CLI | Easiest setup | `gh repo clone org/repo` |

### Path Formats

| Format | Example | When to Use |
|--------|---------|-------------|
| Absolute | `/Users/you/work/project` | Always works |
| Relative | `./demo-repo` | From ParseCodeBase dir |
| Relative | `../other-project` | Sibling directory |
| Relative | `~/work/project` | Home directory |

### Common Issues

| Issue | Solution |
|-------|----------|
| "Repository not found" | Check path, use absolute path |
| "Permission denied" | Check SSH keys or token |
| "Empty index" | Repo might not have supported languages |
| "Slow indexing" | Normal for large repos (>1000 files) |

---

## 📞 Support

### For Authentication Issues

- **SSH**: https://docs.github.com/en/authentication/connecting-to-github-with-ssh
- **Tokens**: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token
- **GitHub CLI**: https://cli.github.com/manual/

### For Indexing Issues

1. Check the terminal output
2. Verify repo has supported files (.ts, .tsx, .dart, .tf, .yaml)
3. Try with demo-repo first to verify system works
4. Check `USAGE_GUIDE.md`

---

## ✅ Checklist

Before indexing your private repo:

- [ ] Repository cloned locally
- [ ] Can access repo (git pull works)
- [ ] Code Intelligence system running
- [ ] Know the full path to your repo
- [ ] Tested with demo-repo first

---

## 🎊 Summary

**Key Points:**

1. ✅ System works with LOCAL repos only
2. ✅ Clone your private repo first (SSH recommended)
3. ✅ Point system to local path
4. ✅ All analysis happens locally (private and secure)
5. ✅ Works with any repo structure
6. ✅ Update with `git pull` + re-index

**That's it!** Your private code stays private, and you get full code intelligence! 🚀

---

For more help, see:
- `FIRST_RUN_INSTRUCTIONS.md` - Getting started
- `USAGE_GUIDE.md` - Full documentation
- `QUICK_START.md` - Quick guide
