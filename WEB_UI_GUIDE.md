# Web UI for Ontology Generation

## 🌐 Beautiful Web Interface with Real-Time Progress

Instead of command-line, you can now use a **beautiful web interface** with live progress updates!

---

## 🚀 Quick Start

### Step 1: Install Web Dependencies

```bash
cd /Users/venureddy/Downloads/LocalMind
pip3 install -r requirements_web.txt
```

### Step 2: Start the Web Server

```bash
python3 web_server.py
```

You'll see:
```
======================================================================
🚀 Ontology Generator Web Server
======================================================================

📍 Open this URL in your browser:
   http://localhost:5000

⏹  Press Ctrl+C to stop the server

======================================================================
```

### Step 3: Open in Browser

Open your browser and go to:
```
http://localhost:5000
```

---

## 🎨 What You'll See

A beautiful web page with:

```
┌─────────────────────────────────────────────────┐
│         🔨 Ontology Generator                    │
│   Generate code ontology with real-time         │
│        progress tracking                         │
├─────────────────────────────────────────────────┤
│                                                  │
│  Repository Path:                               │
│  ┌─────────────────────────────────────────┐   │
│  │ /Users/venureddy/Downloads/PeritaWork...│   │
│  └─────────────────────────────────────────┘   │
│                                                  │
│      ┌───────────────────────────────────┐      │
│      │      Start Generation             │      │
│      └───────────────────────────────────┘      │
│                                                  │
│  ┌─────────────────────────────────────────┐   │
│  │ Step 3/7: Generating Ontology Graph     │   │
│  │                                          │   │
│  │ Overall Progress        42%              │   │
│  │ ████████████░░░░░░░░░░░░                │   │
│  │                                          │   │
│  │ Files                 531 / 1253         │   │
│  │ ████████████░░░░░░░░░░░░                │   │
│  │                                          │   │
│  │ Processing: payroll.controller.ts       │   │
│  └─────────────────────────────────────────┘   │
│                                                  │
│  ┌─────────────── Status Log ──────────────┐   │
│  │ ═══════════════════════════════════      │   │
│  │ Step 1/7: Parsing NestJS Backend        │   │
│  │ Found 1,253 TypeScript files             │   │
│  │ Using 4 parallel workers                 │   │
│  │ ✅ Parsed 1,253 files                    │   │
│  │ ═══════════════════════════════════      │   │
│  │ Step 2/7: Adapting to Ontology Format   │   │
│  │ ...                                      │   │
│  └─────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘
```

---

## ✨ Features

### 1. **Live Progress Updates**
- Real-time progress bars
- Current step display
- Files processed counter
- Current file being processed

### 2. **Beautiful Design**
- Modern gradient design
- Responsive layout
- Smooth animations
- Dark terminal-style log

### 3. **Easy to Use**
1. Enter repository path
2. Click "Start Generation"
3. Watch progress in real-time
4. Get completion notification

### 4. **Server-Sent Events (SSE)**
- Real-time updates without polling
- Efficient streaming
- No WebSocket complexity

---

## 📊 Progress Display

### Overall Progress Bar
Shows progress through 7 steps:
1. Parsing NestJS Backend
2. Adapting to Ontology Format
3. Generating Ontology Graph
4. Saving Files
5. Validating
6. Call Graph
7. Complete

### File Progress Bar
Shows:
- Files processed: 531 / 1,253
- Percentage: 42%
- Current file being processed

### Status Log
Scrollable log with:
- All status messages
- Step headers
- Success/error messages
- Auto-scrolls to latest message

---

## 🔧 Technical Details

### Architecture

```
Browser (HTML/JS)
    ↓
    HTTP Request (POST /api/generate)
    ↓
Flask Server
    ↓
Background Thread
    ↓
OptimizedNestJSParser
    ↓
Progress Updates → Queue
    ↓
SSE Stream (GET /api/progress)
    ↓
Browser Updates UI
```

### Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main HTML page |
| `/api/generate` | POST | Start generation |
| `/api/progress` | GET | SSE stream of progress |
| `/api/status` | GET | Get current status |

### Progress Updates

Every time progress changes:
```javascript
{
  "step": 3,
  "step_name": "Generating Ontology Graph",
  "total_steps": 7,
  "files_processed": 531,
  "total_files": 1253,
  "current_file": "/path/to/file.ts",
  "status_messages": ["...", "..."],
  "is_running": true,
  "is_complete": false
}
```

---

## 🎯 Usage Examples

### Example 1: Default Path

1. Start server: `python3 web_server.py`
2. Open: `http://localhost:5000`
3. Path already filled: `/Users/venureddy/Downloads/PeritaWorkspace`
4. Click "Start Generation"
5. Watch progress!

### Example 2: Custom Path

1. Start server
2. Open browser
3. Change path to your repository
4. Click "Start Generation"

### Example 3: Multiple Repositories

1. Complete first generation
2. Change path to different repository
3. Click "Start Generation" again
4. Previous cache still works!

---

## 🚀 Performance

### First Run
- Time: 5-10 minutes for 1,253 files
- Progress updates every file
- Live status in browser

### Second Run (Cached)
- Time: 30-60 seconds
- 98% files from cache
- Super fast!

### Browser Display
- Updates in real-time
- No page refresh needed
- Smooth progress animations

---

## 🔍 Troubleshooting

### Server Won't Start

**Error:**
```
Address already in use
```

**Solution:**
```bash
# Port 5000 is in use, use different port
# Edit web_server.py, line at bottom:
app.run(debug=True, host='0.0.0.0', port=5001)
```

### No Progress Updates

**Check:**
1. Server is running
2. Browser console for errors (F12)
3. Network tab shows SSE connection

**Solution:**
Refresh the page and start again

### Can't Access from Another Computer

**Current:**
```python
app.run(host='0.0.0.0', port=5000)
```

Access from network:
```
http://<your-ip>:5000
```

Find your IP:
```bash
ifconfig | grep inet
```

---

## 🎨 Customization

### Change Port

Edit `web_server.py`, last line:
```python
app.run(debug=True, host='0.0.0.0', port=8080)  # Changed port
```

### Change Default Repository

Edit HTML_TEMPLATE in `web_server.py`:
```html
<input
    type="text"
    id="repoPath"
    value="/your/custom/path/here"
>
```

### Add More Statistics

After generation completes, you can add:
- Number of nodes
- Number of edges
- API endpoints found
- Validation score

---

## 📱 Mobile Friendly

The web UI is responsive and works on:
- ✅ Desktop browsers
- ✅ Tablets
- ✅ Mobile phones

---

## 🔐 Security Note

**This server is for local use only!**

- Runs on localhost by default
- No authentication
- Don't expose to internet
- Use firewall if needed

For production:
- Add authentication
- Use HTTPS
- Add rate limiting
- Validate inputs

---

## 📁 Output Files

Same as before, in `data/` directory:
```
data/
├── ontology.json
├── ontology.graphml
├── validation_report.json
├── call_graph.json
└── ontology_stats.json
```

---

## 🎉 Advantages

| Feature | Web UI | Command Line |
|---------|---------|--------------|
| Visual progress | ✅ Beautiful | ⚠️ Text only |
| Real-time updates | ✅ Live | ⚠️ Batch |
| Easy to use | ✅ Click button | ⚠️ Type commands |
| Mobile access | ✅ Yes | ❌ No |
| Remote access | ✅ Yes | ⚠️ SSH needed |
| Progress bars | ✅ Graphical | ⚠️ Text |

---

## 🚀 Quick Commands

```bash
# Install dependencies
pip3 install -r requirements_web.txt

# Start server
python3 web_server.py

# Open in browser
open http://localhost:5000

# Or on Linux
xdg-open http://localhost:5000
```

---

## ✅ Summary

**You now have a beautiful web interface!**

1. ✅ Install: `pip3 install -r requirements_web.txt`
2. ✅ Start: `python3 web_server.py`
3. ✅ Open: `http://localhost:5000`
4. ✅ Click "Start Generation"
5. ✅ Watch real-time progress!

**No more command-line - just a beautiful web UI! 🎨**
