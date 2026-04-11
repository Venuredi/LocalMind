#!/usr/bin/env python3
"""
Web Server for Ontology Generation with Real-Time Progress

Start the server and open http://localhost:5001 in your browser.
"""

from flask import Flask, render_template_string, jsonify, request, Response
from flask_cors import CORS
import threading
import queue
import json
import sys
from pathlib import Path
from datetime import datetime
import time

# Add code-intelligence to path
sys.path.insert(0, str(Path(__file__).parent / "code-intelligence"))

from parsers.nestjs.optimized_nestjs_parser import OptimizedNestJSParser
from parsers.treesitter.parser_adapter import ParserAdapter
from parsers.treesitter.ontology_generator import OntologyGenerator
from validation.ontology_validator import OntologyValidator

app = Flask(__name__)
CORS(app)

# Global state for progress
progress_queue = queue.Queue()
current_status = {
    "step": 0,
    "step_name": "Waiting to start...",
    "total_steps": 7,
    "files_processed": 0,
    "total_files": 0,
    "current_file": "",
    "status_messages": [],
    "is_running": False,
    "is_complete": False,
    "success": False,
    "elapsed_seconds": 0,
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Ontology Generation Progress</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            color: #333;
        }

        .container {
            max-width: 900px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }

        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }

        .header h1 {
            font-size: 28px;
            margin-bottom: 10px;
        }

        .header p {
            opacity: 0.9;
            font-size: 14px;
        }

        .content {
            padding: 30px;
        }

        .input-section {
            margin-bottom: 30px;
        }

        .input-section label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #555;
        }

        .input-section input {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 14px;
            transition: border-color 0.3s;
        }

        .input-section input:focus {
            outline: none;
            border-color: #667eea;
        }

        .button {
            width: 100%;
            padding: 15px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }

        .button:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.4);
        }

        .button:disabled {
            background: #ccc;
            cursor: not-allowed;
            transform: none;
        }

        .progress-section {
            display: none;
            margin-top: 30px;
        }

        .progress-section.active {
            display: block;
        }

        .step-info {
            margin-bottom: 20px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }

        .step-info h3 {
            font-size: 18px;
            margin-bottom: 5px;
            color: #667eea;
        }

        .progress-bar-container {
            margin: 15px 0;
        }

        .progress-label {
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
            font-size: 13px;
            color: #666;
        }

        .progress-bar {
            width: 100%;
            height: 8px;
            background: #e0e0e0;
            border-radius: 4px;
            overflow: hidden;
        }

        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            transition: width 0.3s ease;
            border-radius: 4px;
        }

        .file-info {
            font-size: 12px;
            color: #888;
            margin-top: 10px;
            font-family: 'Courier New', monospace;
            word-break: break-all;
        }

        .status-log {
            margin-top: 20px;
            background: #1e1e1e;
            color: #d4d4d4;
            padding: 20px;
            border-radius: 8px;
            max-height: 300px;
            overflow-y: auto;
            font-family: 'Courier New', monospace;
            font-size: 12px;
            line-height: 1.6;
        }

        .status-log::-webkit-scrollbar {
            width: 8px;
        }

        .status-log::-webkit-scrollbar-track {
            background: #2d2d2d;
        }

        .status-log::-webkit-scrollbar-thumb {
            background: #667eea;
            border-radius: 4px;
        }

        .status-message {
            margin: 2px 0;
        }

        .complete-message {
            margin-top: 20px;
            padding: 20px;
            background: #d4edda;
            border: 1px solid #c3e6cb;
            border-radius: 8px;
            color: #155724;
            text-align: center;
        }

        .error-message {
            margin-top: 20px;
            padding: 20px;
            background: #f8d7da;
            border: 1px solid #f5c6cb;
            border-radius: 8px;
            color: #721c24;
            text-align: center;
        }

        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }

        .stat-card {
            background: white;
            padding: 15px;
            border-radius: 8px;
            border: 1px solid #e0e0e0;
            text-align: center;
        }

        .stat-card .value {
            font-size: 24px;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 5px;
        }

        .stat-card .label {
            font-size: 12px;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔨 Ontology Generator</h1>
            <p>Generate code ontology with real-time progress tracking</p>
        </div>

        <div class="content">
            <div class="input-section">
                <label for="repoPath">Repository Path:</label>
                <input
                    type="text"
                    id="repoPath"
                    placeholder="/Users/venureddy/Downloads/PeritaWorkspace"
                    value="/Users/venureddy/Downloads/PeritaWorkspace"
                >
            </div>

            <button class="button" id="startButton" onclick="startGeneration()">
                Start Generation
            </button>

            <div class="progress-section" id="progressSection">
                <div class="step-info">
                    <h3 id="stepTitle">Step 1/7: Initializing...</h3>

                    <div class="progress-bar-container">
                        <div class="progress-label">
                            <span>Overall Progress</span>
                            <span id="overallPercent">0%</span>
                        </div>
                        <div class="progress-bar">
                            <div class="progress-fill" id="overallProgress" style="width: 0%"></div>
                        </div>
                    </div>

                    <div class="progress-bar-container">
                        <div class="progress-label">
                            <span>Files</span>
                            <span id="fileCount">0 / 0</span>
                        </div>
                        <div class="progress-bar">
                            <div class="progress-fill" id="fileProgress" style="width: 0%"></div>
                        </div>
                    </div>

                    <div class="file-info" id="currentFile"></div>
                </div>

                <div class="stats" id="stats" style="display: none;">
                    <div class="stat-card">
                        <div class="value" id="statNodes">0</div>
                        <div class="label">Nodes</div>
                    </div>
                    <div class="stat-card">
                        <div class="value" id="statEdges">0</div>
                        <div class="label">Edges</div>
                    </div>
                    <div class="stat-card">
                        <div class="value" id="statEndpoints">0</div>
                        <div class="label">API Endpoints</div>
                    </div>
                    <div class="stat-card">
                        <div class="value" id="statScore">0%</div>
                        <div class="label">Completeness</div>
                    </div>
                </div>

                <div class="status-log" id="statusLog"></div>
            </div>
        </div>
    </div>

    <script>
        let eventSource = null;

        function startGeneration() {
            const repoPath = document.getElementById('repoPath').value;
            const button = document.getElementById('startButton');
            const progressSection = document.getElementById('progressSection');
            const statusLog = document.getElementById('statusLog');

            if (!repoPath) {
                alert('Please enter a repository path');
                return;
            }

            // Disable button
            button.disabled = true;
            button.textContent = 'Generating...';

            // Show progress section
            progressSection.classList.add('active');
            statusLog.innerHTML = '';

            // Start generation
            fetch('/api/generate', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({repo_path: repoPath})
            });

            // Connect to progress stream
            eventSource = new EventSource('/api/progress');

            eventSource.onmessage = function(event) {
                const data = JSON.parse(event.data);
                updateProgress(data);
            };

            eventSource.onerror = function(error) {
                console.error('EventSource error:', error);
            };
        }

        function updateProgress(data) {
            // Update step
            document.getElementById('stepTitle').textContent =
                `Step ${data.step}/${data.total_steps}: ${data.step_name}`;

            // Update overall progress
            const overallPercent = Math.round((data.step / data.total_steps) * 100);
            document.getElementById('overallPercent').textContent = overallPercent + '%';
            document.getElementById('overallProgress').style.width = overallPercent + '%';

            // Update file progress
            if (data.total_files > 0) {
                const filePercent = Math.round((data.files_processed / data.total_files) * 100);
                document.getElementById('fileCount').textContent =
                    `${data.files_processed} / ${data.total_files}`;
                document.getElementById('fileProgress').style.width = filePercent + '%';
            }

            // Update current file
            if (data.current_file) {
                const fileName = data.current_file.split('/').pop();
                document.getElementById('currentFile').textContent =
                    `Processing: ${fileName}`;
            }

            // Update status log
            const statusLog = document.getElementById('statusLog');
            data.status_messages.slice(-20).forEach((msg, i) => {
                if (i === data.status_messages.length - 1) {
                    const msgDiv = document.createElement('div');
                    msgDiv.className = 'status-message';
                    msgDiv.textContent = msg;
                    statusLog.appendChild(msgDiv);
                    statusLog.scrollTop = statusLog.scrollHeight;
                }
            });

            // Check if complete
            if (data.is_complete) {
                document.getElementById('startButton').textContent = 'Start Generation';
                document.getElementById('startButton').disabled = false;

                if (data.success) {
                    showStats(data);
                }

                if (eventSource) {
                    eventSource.close();
                }
            }
        }

        function showStats(data) {
            const statsDiv = document.getElementById('stats');
            statsDiv.style.display = 'grid';

            // These would come from the actual results
            // For now, just show completion
            document.getElementById('statScore').textContent = '100%';
        }
    </script>
</body>
</html>
"""


def generate_ontology_background(repo_path: str):
    """Generate ontology in background thread."""
    global current_status

    try:
        current_status["is_running"] = True
        current_status["is_complete"] = False
        start_time = datetime.now()

        def add_status(msg):
            current_status["status_messages"].append(msg)
            progress_queue.put(current_status.copy())

        # Step 1
        current_status["step"] = 1
        current_status["step_name"] = "Parsing NestJS Backend"
        add_status("="*60)
        add_status("Step 1/7: Parsing NestJS Backend")
        add_status("="*60)

        def progress_callback(message):
            if message.endswith(".ts"):
                current_status["files_processed"] += 1
                current_status["current_file"] = message
            else:
                add_status(message)
            progress_queue.put(current_status.copy())

        parser = OptimizedNestJSParser(
            repo_path,
            progress_callback=progress_callback,
            max_workers=4,
            use_cache=True
        )

        # Find files
        ts_files = [
            f for f in Path(repo_path).rglob("*.ts")
            if not parser._is_excluded(f)
        ]
        current_status["total_files"] = len(ts_files)
        add_status(f"Found {len(ts_files)} TypeScript files")

        # Parse
        nestjs_data = parser.parse()
        stats = parser.get_stats()
        add_status(f"✅ Parsed {stats['processed_files']} files")

        # Step 2
        current_status["step"] = 2
        current_status["step_name"] = "Adapting to Ontology Format"
        add_status("\n" + "="*60)
        add_status("Step 2/7: Adapting to Ontology Format")
        add_status("="*60)

        adapter = ParserAdapter()
        ontology_data = adapter.adapt("nestjs", nestjs_data)
        add_status("✅ Adapted to ontology format")

        # Step 3
        current_status["step"] = 3
        current_status["step_name"] = "Generating Ontology Graph"
        add_status("\n" + "="*60)
        add_status("Step 3/7: Generating Ontology Graph")
        add_status("="*60)

        generator = OntologyGenerator(ontology_data)
        graph = generator.build_ontology()
        add_status(f"✅ Graph created: {graph.number_of_nodes()} nodes, {graph.number_of_edges()} edges")

        # Step 4
        current_status["step"] = 4
        current_status["step_name"] = "Saving Files"
        add_status("\n" + "="*60)
        add_status("Step 4/7: Saving Files")
        add_status("="*60)

        output_dir = Path(__file__).parent / "data"
        output_dir.mkdir(exist_ok=True)

        generator.save_ontology(str(output_dir / "ontology.json"), format="json")
        add_status(f"✅ Saved: ontology.json")

        # Step 5
        current_status["step"] = 5
        current_status["step_name"] = "Validating"
        add_status("\n" + "="*60)
        add_status("Step 5/7: Validating")
        add_status("="*60)

        validator = OntologyValidator(graph)
        results = validator.validate_coverage()
        add_status(f"✅ Validation complete: {results['cross_layer_paths']['coverage_percent']}%")

        # Step 6
        current_status["step"] = 6
        current_status["step_name"] = "Call Graph"
        add_status("\n" + "="*60)
        add_status("Step 6/7: Call Graph")
        add_status("="*60)

        call_graph = generator.get_call_graph()
        add_status(f"✅ Call graph: {call_graph.number_of_nodes()} nodes")

        # Step 7
        current_status["step"] = 7
        current_status["step_name"] = "Complete"
        add_status("\n" + "="*60)
        add_status("✅ COMPLETE!")
        add_status("="*60)

        current_status["is_complete"] = True
        current_status["success"] = True
        current_status["elapsed_seconds"] = (datetime.now() - start_time).total_seconds()
        progress_queue.put(current_status.copy())

    except Exception as e:
        current_status["is_complete"] = True
        current_status["success"] = False
        current_status["status_messages"].append(f"❌ Error: {str(e)}")
        progress_queue.put(current_status.copy())


@app.route('/')
def index():
    """Serve the main page."""
    return render_template_string(HTML_TEMPLATE)


@app.route('/api/generate', methods=['POST'])
def api_generate():
    """Start ontology generation."""
    global current_status

    data = request.json
    repo_path = data.get('repo_path')

    if not repo_path:
        return jsonify({"error": "repo_path required"}), 400

    # Reset status
    current_status = {
        "step": 0,
        "step_name": "Starting...",
        "total_steps": 7,
        "files_processed": 0,
        "total_files": 0,
        "current_file": "",
        "status_messages": [],
        "is_running": False,
        "is_complete": False,
        "success": False,
        "elapsed_seconds": 0,
    }

    # Start in background thread
    thread = threading.Thread(
        target=generate_ontology_background,
        args=(repo_path,),
        daemon=True
    )
    thread.start()

    return jsonify({"status": "started"})


@app.route('/api/progress')
def api_progress():
    """Stream progress updates."""
    def generate():
        while True:
            try:
                # Get latest status
                status = progress_queue.get(timeout=1)
                yield f"data: {json.dumps(status)}\n\n"

                if status.get("is_complete"):
                    break
            except queue.Empty:
                # Send heartbeat
                yield f"data: {json.dumps(current_status)}\n\n"

    return Response(generate(), mimetype='text/event-stream')


@app.route('/api/status')
def api_status():
    """Get current status."""
    return jsonify(current_status)


if __name__ == '__main__':
    print("\n" + "="*70)
    print("🚀 Ontology Generator Web Server")
    print("="*70)
    print("\n📍 Open this URL in your browser:")
    print("   http://localhost:5001")
    print("\n⏹  Press Ctrl+C to stop the server\n")
    print("="*70 + "\n")

    app.run(debug=False, host='0.0.0.0', port=5001, threaded=True)
