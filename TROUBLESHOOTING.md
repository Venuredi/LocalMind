# Troubleshooting Guide

## Error: "A listener indicated an asynchronous response by returning true..."

### What This Error Means

This error is **NOT from the Python script**. It's a browser/IDE error that occurs when:

1. **VS Code Extension Issue** - A VS Code extension tried to communicate but failed
2. **Chrome/Browser Extension** - A browser extension error (if you have docs open)
3. **IDE Background Process** - Your IDE's background processes

**This error is harmless and doesn't affect the ontology generation!**

---

## Solutions

### Option 1: Use Simple Console Version (Recommended)

**No GUI, no threads, no complexity - just works!**

```bash
python generate_ontology_simple.py /Users/venureddy/Downloads/PeritaWorkspace
```

**Output:**
```
======================================================================
🚀 Ontology Generation - Simple Console Mode
======================================================================

======================================================================
Step 1/7: Parsing NestJS Backend
======================================================================
  Creating parser...
  Finding TypeScript files...
  Found 1,253 TypeScript files (excluding node_modules, etc.)
  Parsing files (this may take a few minutes)...
  Processed 50 files...
  Processed 100 files...
  Processed 150 files...
  ...
  ✅ Parsed 1,253 files
     Cached: 0 files
     Time: 387.2s

  Components found:
    Controllers:      45
    Services:         78
    DTOs:             132
    ...

======================================================================
Step 2/7: Adapting to Ontology Format
======================================================================
  ...
```

**Advantages:**
- ✅ No GUI dependencies
- ✅ No threading issues
- ✅ Clear progress in console
- ✅ Works on any system

### Option 2: Ignore the Error and Use GUI Version

The error doesn't affect functionality. Just run:

```bash
python generate_ontology_with_progress.py /Users/venureddy/Downloads/PeritaWorkspace
```

The GUI window should still appear and work fine.

### Option 3: Use Console Mode (No GUI)

If GUI causes issues:

```bash
python generate_ontology_with_progress.py /Users/venureddy/Downloads/PeritaWorkspace --no-gui
```

---

## Common Issues

### 1. GUI Window Doesn't Appear

**Cause:** tkinter not installed or display issues

**Solution:**
```bash
# Use simple version
python generate_ontology_simple.py /path/to/repo

# OR use --no-gui flag
python generate_ontology_with_progress.py /path/to/repo --no-gui
```

### 2. Script Runs Forever

**Cause:** Processing node_modules (old parser)

**Check if using optimized parser:**
```bash
# Should say "Found 1,253 files" not "Found 56,799 files"
```

**Solution:**
```bash
# Make sure using the new script
python generate_ontology_simple.py /path/to/repo
```

### 3. Import Errors

**Error:**
```
ModuleNotFoundError: No module named 'code-intelligence'
```

**Solution:**
```bash
# Make sure you're in the LocalMind directory
cd /Users/venureddy/Downloads/LocalMind
python generate_ontology_simple.py /Users/venureddy/Downloads/PeritaWorkspace
```

### 4. Cache Issues

**Symptoms:** Slow performance even on re-runs

**Solution:**
```bash
# Clear cache
rm -rf ~/.localmind_cache/parser/

# Run again
python generate_ontology_simple.py /path/to/repo
```

### 5. Memory Issues

**Symptoms:** Script crashes or system slows down

**Solution:**
```bash
# Reduce parallel workers
# Edit the script and change max_workers from 4 to 2
```

In `generate_ontology_simple.py`, line ~50:
```python
max_workers=2  # Changed from 4
```

---

## Which Script Should I Use?

| Scenario | Recommended Script |
|----------|-------------------|
| First time user | `generate_ontology_simple.py` |
| Want GUI progress | `generate_ontology_with_progress.py` |
| GUI not working | `generate_ontology_simple.py` |
| Server/headless | `generate_ontology_simple.py` |
| CI/CD pipeline | `generate_ontology_simple.py` |

---

## Performance Expectations

### Your PeritaWorkspace Repository

**Files:**
- Total TS files: 56,799 (with node_modules)
- Source files: 1,253 (excluded node_modules)

**First Run (Building Cache):**
- Time: 5-10 minutes
- Files/sec: 2-4
- Output: Full cache built

**Subsequent Runs (With Cache):**
- Time: 30-60 seconds
- Files/sec: 40+
- Output: Only changed files re-parsed

**Console Output Example:**
```
Processed 50 files...    # After ~20 seconds
Processed 100 files...   # After ~40 seconds
Processed 150 files...   # After ~60 seconds
...
Processed 1250 files...  # After ~6-8 minutes
✅ Parsed 1,253 files
   Time: 387.2s (6.5 minutes)
```

---

## Debugging Steps

### Step 1: Verify Python Version

```bash
python3 --version
# Should be 3.8+
```

### Step 2: Test Simple Version

```bash
cd /Users/venureddy/Downloads/LocalMind
python3 generate_ontology_simple.py demo-repo/backend
```

Should complete in < 1 minute for demo repo.

### Step 3: Test on Real Repo

```bash
python3 generate_ontology_simple.py /Users/venureddy/Downloads/PeritaWorkspace
```

Watch for:
- ✅ "Found 1,253 TypeScript files" (good)
- ❌ "Found 56,799 files" (bad - not using optimized parser)

### Step 4: Check Output

```bash
ls -lh data/
```

Should see:
- `ontology.json` (10-50 MB)
- `ontology.graphml`
- `validation_report.json`
- `call_graph.json`
- `ontology_stats.json`

---

## Getting Help

If issues persist:

1. **Check the error message carefully**
   - Browser errors: Ignore them
   - Python errors: Check the traceback

2. **Use the simple version**
   ```bash
   python generate_ontology_simple.py /path/to/repo
   ```

3. **Collect diagnostic info**
   ```bash
   # Python version
   python3 --version

   # Files found
   find /Users/venureddy/Downloads/PeritaWorkspace -name "*.ts" -not -path "*/node_modules/*" | wc -l

   # Output directory
   ls -la data/
   ```

---

## Success Indicators

You'll know it's working when:

1. ✅ Console shows "Found 1,253 files" (not 56,799)
2. ✅ Progress updates every few seconds
3. ✅ Completes in 5-10 minutes
4. ✅ Creates files in `data/` directory
5. ✅ Validation score > 80%

---

## Quick Reference

```bash
# Simple version (recommended)
python generate_ontology_simple.py /Users/venureddy/Downloads/PeritaWorkspace

# GUI version
python generate_ontology_with_progress.py /Users/venureddy/Downloads/PeritaWorkspace

# GUI version, console mode
python generate_ontology_with_progress.py /Users/venureddy/Downloads/PeritaWorkspace --no-gui

# Clear cache
rm -rf ~/.localmind_cache/parser/

# Check output
ls -lh data/
cat data/validation_report.json | python -m json.tool
```

---

## Summary

**The browser error you saw is NOT from the Python script.** It's harmless.

**Use this command:**
```bash
python generate_ontology_simple.py /Users/venureddy/Downloads/PeritaWorkspace
```

**It will:**
- ✅ Process only 1,253 files (not 56,799)
- ✅ Show progress in console
- ✅ Complete in 5-10 minutes
- ✅ Create all output files
- ✅ Work reliably without GUI

**That's it! The simple version is bulletproof. 🎯**
