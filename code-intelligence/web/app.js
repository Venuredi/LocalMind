// API Base URL
const API_BASE = 'http://localhost:8000';

// Global state
let currentGraph = null;
let indexData = null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupTabs();
    checkSystemStatus();
});

// Tab Navigation
function setupTabs() {
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            // Remove active class from all
            tabBtns.forEach(b => b.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));

            // Add active class to clicked
            btn.classList.add('active');
            const tabId = btn.getAttribute('data-tab');
            document.getElementById(tabId).classList.add('active');

            // Load data if needed
            if (tabId === 'ontology') {
                loadGraph();
            } else if (tabId === 'stats') {
                loadStats();
            }
        });
    });
}

// Check System Status
async function checkSystemStatus() {
    try {
        const response = await axios.get(`${API_BASE}/`);
        if (response.data.indexed) {
            document.getElementById('systemStatus').style.display = 'block';
            document.getElementById('statusContent').innerHTML = `
                <div style="color: green;">✅ System is indexed and ready</div>
            `;
            loadStats();
        }
    } catch (error) {
        console.error('Error checking status:', error);
    }
}

// Index Repository with Real-Time Progress
let indexEventSource = null;
let stepsCompleted = 0;

async function indexRepository() {
    const repoPath = document.getElementById('repoPath').value.trim();

    if (!repoPath) {
        showToast('Please enter a repository path', 'error');
        return;
    }

    // Show loading on button
    document.getElementById('indexBtnText').style.display = 'none';
    document.getElementById('indexSpinner').style.display = 'inline-block';

    // Show progress modal
    showProgressModal();

    try {
        // Start indexing
        const response = await axios.post(`${API_BASE}/api/index`, {
            repo_path: repoPath
        });

        if (response.data.status !== 'started') {
            throw new Error('Failed to start indexing');
        }

        // Connect to progress stream
        indexEventSource = new EventSource(`${API_BASE}/api/index/progress`);

        indexEventSource.onopen = function() {
            console.log('SSE connection opened');
        };

        indexEventSource.onmessage = function(event) {
            console.log('SSE message received:', event.data);
            try {
                const data = JSON.parse(event.data);
                updateIndexProgress(data);
            } catch (e) {
                console.error('Error parsing SSE data:', e);
            }
        };

        indexEventSource.onerror = function(error) {
            console.error('EventSource error:', error);
            console.log('EventSource readyState:', indexEventSource.readyState);

            // Don't close immediately - let it retry unless it's a fatal error
            if (indexEventSource.readyState === EventSource.CLOSED) {
                console.log('SSE connection closed');
                indexEventSource.close();

                // Fall back to polling if SSE fails
                console.log('Falling back to status polling...');
                pollIndexStatus();
            }
        };

    } catch (error) {
        document.getElementById('indexProgress').innerHTML = '❌ Indexing failed';
        document.getElementById('indexResult').style.display = 'block';
        document.getElementById('indexResult').innerHTML = `
            <h4 style="color: red;">❌ Error</h4>
            <p>${error.response?.data?.detail || error.message}</p>
        `;
        showToast('Indexing failed', 'error');
        document.getElementById('indexBtnText').style.display = 'inline';
        document.getElementById('indexSpinner').style.display = 'none';
    }
}

// Fallback: Poll status endpoint if SSE fails
let statusPollInterval = null;

async function pollIndexStatus() {
    statusPollInterval = setInterval(async () => {
        try {
            const response = await axios.get(`${API_BASE}/api/index/status`);
            updateIndexProgress(response.data);

            if (response.data.is_complete) {
                clearInterval(statusPollInterval);
                statusPollInterval = null;
            }
        } catch (error) {
            console.error('Error polling status:', error);
            clearInterval(statusPollInterval);
            statusPollInterval = null;
        }
    }, 500); // Poll every 500ms
}

function updateIndexProgress(data) {
    // Update step title
    const stepTitle = document.getElementById('stepTitle');
    if (stepTitle) {
        stepTitle.textContent = `Step ${data.step}/${data.total_steps}: ${data.step_name}`;
    }

    // Update overall progress
    const overallPercent = Math.round((data.step / data.total_steps) * 100);
    const overallPercentEl = document.getElementById('overallPercent');
    const overallProgressEl = document.getElementById('overallProgress');
    if (overallPercentEl) overallPercentEl.textContent = overallPercent + '%';
    if (overallProgressEl) overallProgressEl.style.width = overallPercent + '%';

    // Update file progress
    if (data.total_files > 0) {
        const filePercent = Math.round((data.files_processed / data.total_files) * 100);
        const fileCountEl = document.getElementById('fileCount');
        const fileProgressEl = document.getElementById('fileProgress');
        if (fileCountEl) fileCountEl.textContent = `${data.files_processed} / ${data.total_files}`;
        if (fileProgressEl) fileProgressEl.style.width = filePercent + '%';
    }

    // Update current file
    if (data.current_file) {
        const currentFileEl = document.getElementById('currentFile');
        if (currentFileEl) {
            const fileName = data.current_file.split('/').pop();
            currentFileEl.textContent = `Processing: ${fileName}`;
        }
    }

    // Update status log
    const statusLog = document.getElementById('statusLog');
    if (statusLog && data.status_messages) {
        const lastMessages = data.status_messages.slice(-10);
        statusLog.innerHTML = lastMessages.map(msg => `<div class="log-message">${msg}</div>`).join('');
        statusLog.scrollTop = statusLog.scrollHeight;
    }

    // ========== MODAL UPDATES ==========
    // Update modal step title
    const modalStepTitle = document.getElementById('modalStepTitle');
    if (modalStepTitle) {
        modalStepTitle.textContent = `Step ${data.step}/${data.total_steps}: ${data.step_name}`;
    }

    // Update modal overall progress
    const modalOverallPercent = document.getElementById('modalOverallPercent');
    const modalOverallProgress = document.getElementById('modalOverallProgress');
    if (modalOverallPercent) modalOverallPercent.textContent = overallPercent + '%';
    if (modalOverallProgress) modalOverallProgress.style.width = overallPercent + '%';

    // Update modal current activity
    if (data.current_file) {
        const fileName = data.current_file.split('/').pop();
        const modalCurrentActivity = document.getElementById('modalCurrentActivity');
        if (modalCurrentActivity) {
            modalCurrentActivity.textContent = `Processing: ${fileName}`;
        }
    } else if (data.step_name) {
        const modalCurrentActivity = document.getElementById('modalCurrentActivity');
        if (modalCurrentActivity) {
            modalCurrentActivity.textContent = data.step_name;
        }
    }

    // Display status messages in modal (backend uses rolling buffer of last 100)
    if (data.status_messages && data.status_messages.length > 0) {
        const lastMessage = data.status_messages[data.status_messages.length - 1];
        const stepsLog = document.getElementById('modalStepsLog');
        const currentLogText = stepsLog ? stepsLog.textContent : '';

        // Only add if this message isn't already in the log
        if (!currentLogText.includes(lastMessage)) {
            let type = 'info';
            if (lastMessage.includes('✅') || lastMessage.includes('complete') || lastMessage.includes('Successfully')) {
                type = 'success';
            } else if (lastMessage.includes('❌') || lastMessage.includes('Error') || lastMessage.includes('Failed')) {
                type = 'error';
            } else if (lastMessage.includes('⚠️') || lastMessage.includes('Warning')) {
                type = 'warning';
            }
            addStepToLog(lastMessage, type);
        }
    }

    // Check if complete
    if (data.is_complete) {
        // Cleanup
        if (statusPollInterval) {
            clearInterval(statusPollInterval);
            statusPollInterval = null;
        }

        document.getElementById('indexBtnText').style.display = 'inline';
        document.getElementById('indexSpinner').style.display = 'none';

        if (data.success) {
            document.getElementById('indexResult').style.display = 'block';
            document.getElementById('indexResult').innerHTML = `
                <h4>✅ Repository Indexed Successfully!</h4>
                <p><strong>Components:</strong> ${data.stats.components || 0}</p>
                <p><strong>Relationships:</strong> ${data.stats.relationships || 0}</p>
                <p><strong>API Endpoints:</strong> ${data.stats.apis || 0}</p>
                <p><strong>Time:</strong> ${data.stats.elapsed_seconds?.toFixed(1) || 0}s</p>
                <p style="margin-top: 15px; color: #28a745;">You can now explore the ontology, search, and generate AI prompts!</p>
            `;
            showToast('Repository indexed successfully!', 'success');
            checkSystemStatus();

            // Update modal with completion
            addStepToLog('✅ Repository indexed successfully!', 'success');

            // Update current activity to show completion
            const modalCurrentActivity = document.getElementById('modalCurrentActivity');
            if (modalCurrentActivity) {
                modalCurrentActivity.textContent = '✅ Indexing complete! Successfully indexed repository.';
            }

            const modalStats = document.getElementById('modalStats');
            if (modalStats) {
                modalStats.style.display = 'block';
                modalStats.innerHTML = `
                    <h4>📊 Indexing Complete</h4>
                    <div class="stats-grid">
                        <div class="stat-item">
                            <span class="stat-value">${data.stats.components || 0}</span>
                            <span class="stat-label">Components</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-value">${data.stats.relationships || 0}</span>
                            <span class="stat-label">Relationships</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-value">${data.stats.apis || 0}</span>
                            <span class="stat-label">API Endpoints</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-value">${data.stats.elapsed_seconds?.toFixed(1) || 0}s</span>
                            <span class="stat-label">Time</span>
                        </div>
                    </div>
                `;
            }
        } else {
            document.getElementById('indexResult').style.display = 'block';
            document.getElementById('indexResult').innerHTML = `
                <h4 style="color: red;">❌ Indexing Failed</h4>
                <p>Check the status log above for details.</p>
            `;
            showToast('Indexing failed', 'error');
            addStepToLog('❌ Indexing failed', 'error');

            // Update current activity to show failure
            const modalCurrentActivity = document.getElementById('modalCurrentActivity');
            if (modalCurrentActivity) {
                modalCurrentActivity.textContent = '❌ Indexing failed. Check the log for details.';
            }
        }

        // Enable "Close" button at bottom
        const modalActionBtn = document.getElementById('modalActionBtn');
        if (modalActionBtn) modalActionBtn.style.display = 'inline-block';

        if (indexEventSource) {
            indexEventSource.close();
            indexEventSource = null;
        }
    }
}

// Load Graph
async function loadGraph() {
    try {
        const response = await axios.get(`${API_BASE}/api/graph`);
        const graphData = response.data;
        
        // Save for filtering
        window.allGraphNodes = graphData.nodes;
        window.allGraphEdges = graphData.edges;

        // Populate datalist for search
        const datalist = document.getElementById('graphNodeList');
        if (datalist) {
            datalist.innerHTML = window.allGraphNodes
                .map(n => `<option value="${n.id}">${n.name || n.id}</option>`)
                .join('');
        }

        // Create vis.js network
        const container = document.getElementById('graphContainer');

        const nodes = new vis.DataSet(
            graphData.nodes.map(node => ({
                id: node.id,
                label: node.name || node.id,
                title: `${node.type}\n${node.file_path || ''}`,
                color: getLayerColor(node.layer),
                shape: getNodeShape(node.type)
            }))
        );

        const edges = new vis.DataSet(
            graphData.edges.map((edge, idx) => ({
                id: idx,
                from: edge.from,
                to: edge.to,
                arrows: 'to',
                label: edge.type,
                color: edge.layer_crossing ? '#ff6b6b' : '#95a5a6'
            }))
        );

        const data = { nodes, edges };

        const options = {
            nodes: {
                font: { size: 14 },
                borderWidth: 2,
                shadow: true
            },
            edges: {
                font: { size: 10, align: 'middle' },
                smooth: { type: 'cubicBezier' }
            },
            physics: {
                enabled: true,
                stabilization: { iterations: 100 }
            },
            interaction: {
                hover: true,
                tooltipDelay: 100
            }
        };

        currentGraph = new vis.Network(container, data, options);

        // Handle node click
        currentGraph.on('click', async (params) => {
            if (params.nodes.length > 0) {
                const nodeId = params.nodes[0];
                await showNodeDetails(nodeId);
            }
        });

        // Load layer view (Removed)

        showToast('Graph loaded successfully', 'success');

    } catch (error) {
        console.error('Error loading graph:', error);
        showToast('Error loading graph', 'error');
    }
}

// Get layer color
function getLayerColor(layer) {
    const colors = {
        'frontend-mobile': '#FF6B6B',
        'frontend-web': '#4ECDC4',
        'backend': '#45B7D1',
        'data': '#96CEB4',
        'infrastructure': '#FFEAA7',
        'deployment': '#DFE6E9'
    };
    return colors[layer] || '#95a5a6';
}

// Get node shape
function getNodeShape(type) {
    const shapes = {
        'screen': 'box',
        'page': 'box',
        'controller': 'diamond',
        'service': 'ellipse',
        'repository': 'database',
        'entity': 'database',
        'component': 'box',
        'hook': 'triangle'
    };
    return shapes[type] || 'dot';
}

// Show node details
async function showNodeDetails(nodeId) {
    try {
        // URL encode the nodeId to handle special characters like :: in component IDs
        const response = await axios.get(`${API_BASE}/api/components/${encodeURIComponent(nodeId)}`);
        const component = response.data.component;

        document.getElementById('nodeDetails').style.display = 'block';
        document.getElementById('nodeDetailsContent').innerHTML = `
            <p><strong>Name:</strong> ${component.name}</p>
            <p><strong>Type:</strong> ${component.type}</p>
            <p><strong>Layer:</strong> ${component.layer}</p>
            <p><strong>File:</strong> <code>${component.file_path}:${component.line_start}</code></p>
            ${component.description ? `<p><strong>Description:</strong> ${component.description}</p>` : ''}

            <h4>Dependencies (${response.data.dependencies.length})</h4>
            <ul>
                ${response.data.dependencies.map(dep => `<li>${dep.name} (${dep.type})</li>`).join('') || '<li>None</li>'}
            </ul>

            <h4>Used By (${response.data.dependents.length})</h4>
            <ul>
                ${response.data.dependents.map(dep => `<li>${dep.name} (${dep.type})</li>`).join('') || '<li>None</li>'}
            </ul>
        `;
    } catch (error) {
        console.error('Error loading component details:', error);
    }
}

// Load layer view
async function loadLayerView() {
    try {
        const response = await axios.get(`${API_BASE}/api/components`);
        const components = response.data.components;

        // Group by layer
        const byLayer = {};
        components.forEach(comp => {
            const layer = comp.layer || 'unknown';
            if (!byLayer[layer]) byLayer[layer] = [];
            byLayer[layer].push(comp);
        });

        let html = '';
        for (const [layer, comps] of Object.entries(byLayer)) {
            html += `
                <div class="layer-section">
                    <h4>🔷 ${layer.toUpperCase()} (${comps.length})</h4>
                    <div class="component-list">
                        ${comps.slice(0, 10).map(comp => `
                            <div class="component-item" onclick="showNodeDetails('${comp.id}')">
                                <div>
                                    <div class="name">${comp.name}</div>
                                    <div class="type">${comp.type}</div>
                                </div>
                                <div style="font-size: 12px; color: #6c757d;">${comp.file_path}</div>
                            </div>
                        `).join('')}
                        ${comps.length > 10 ? `<p style="text-align: center; color: #6c757d;">... and ${comps.length - 10} more</p>` : ''}
                    </div>
                </div>
            `;
        }

        document.getElementById('layerView').innerHTML = html;

    } catch (error) {
        console.error('Error loading layer view:', error);
    }
}

// Filter graph
function filterGraph() {
    const layer = document.getElementById('layerFilter').value;
    
    if (!currentGraph || !window.allGraphNodes) return;
    
    // Filter nodes by layer (or show all if no layer selected)
    const filteredNodes = window.allGraphNodes.filter(n => !layer || n.layer === layer);
    
    // Only keep edges where both source and target are in our filtered nodes set
    const validNodeIds = new Set(filteredNodes.map(n => n.id));
    const filteredEdges = window.allGraphEdges.filter(e => validNodeIds.has(e.from) && validNodeIds.has(e.to));
    
    // Create new DataSets for vis.js
    const nodes = new vis.DataSet(
        filteredNodes.map(node => ({
            id: node.id,
            label: node.name || node.id,
            title: `${node.type}\n${node.file_path || ''}`,
            color: getLayerColor(node.layer),
            shape: getNodeShape(node.type)
        }))
    );

    const edges = new vis.DataSet(
        filteredEdges.map((edge, idx) => ({
            id: idx,
            from: edge.from,
            to: edge.to,
            arrows: 'to',
            label: edge.type,
            color: edge.layer_crossing ? '#ff6b6b' : '#95a5a6'
        }))
    );

    // Update the graph without losing the network instance
    currentGraph.setData({ nodes, edges });
    showToast('Filtering by: ' + (layer || 'All Layers'), 'success');
}

// Export graph as JSON
async function exportGraph() {
    if (!currentGraph) {
        showToast('No graph to export. Please index a repository first.', 'error');
        return;
    }

    try {
        showToast('Preparing export...', 'success');

        // Fetch the ontology from the backend
        const response = await fetch(`${API_BASE}/api/export/ontology`);

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || 'Export failed');
        }

        // Extract suggested filename from Content-Disposition header, fallback to timestamped name
        const disposition = response.headers.get('Content-Disposition') || '';
        const match = disposition.match(/filename="([^"]+)"/);
        const filename = match ? match[1] : `ontology_${new Date().toISOString().replace(/[:.]/g, '-')}.json`;

        // Stream blob and trigger browser download
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        showToast(`✅ Exported as ${filename}`, 'success');
    } catch (error) {
        console.error('Export error:', error);
        showToast(`Export failed: ${error.message}`, 'error');
    }
}

// Graph Controls
function zoomIn() {
    if (currentGraph) {
        const scale = currentGraph.getScale();
        currentGraph.moveTo({ scale: scale * 1.2, animation: { duration: 300 } });
    }
}

function zoomOut() {
    if (currentGraph) {
        const scale = currentGraph.getScale();
        currentGraph.moveTo({ scale: scale / 1.2, animation: { duration: 300 } });
    }
}

function toggleFullscreen() {
    const container = document.getElementById('graphContainer');
    if (!document.fullscreenElement) {
        if (container.requestFullscreen) {
            container.requestFullscreen();
        } else if (container.mozRequestFullScreen) { // Firefox
            container.mozRequestFullScreen();
        } else if (container.webkitRequestFullscreen) { // Chrome, Safari and Opera
            container.webkitRequestFullscreen();
        } else if (container.msRequestFullscreen) { // IE/Edge
            container.msRequestFullscreen();
        }
        
        // Add white background when in fullscreen so we can see nodes
        container.style.backgroundColor = '#ffffff';
    } else {
        if (document.exitFullscreen) {
            document.exitFullscreen();
        } else if (document.mozCancelFullScreen) {
            document.mozCancelFullScreen();
        } else if (document.webkitExitFullscreen) {
            document.webkitExitFullscreen();
        } else if (document.msExitFullscreen) {
            document.msExitFullscreen();
        }
        
        // Remove background color when exiting fullscreen
        container.style.backgroundColor = '';
    }
}

// ─────────────────────────────────────────────────────────────
// Utility: extract explicit file names from free text
// e.g. "enhance AssetListGrid.tsx" → ["AssetListGrid.tsx"]
// ─────────────────────────────────────────────────────────────
function extractFileTargets(text) {
    // Match filenames with common code extensions
    const filePattern = /\b[\w.-]+\.(tsx?|jsx?|py|dart|java|go|rs|cs|php|rb|vue|svelte|kt|swift)\b/gi;
    const matches = text.match(filePattern) || [];
    return [...new Set(matches)]; // dedupe
}

// ─────────────────────────────────────────────────────────────
// Utility: extract PascalCase component/service/class names
// e.g. "Enhance RedisService" → ["RedisService"]
// ─────────────────────────────────────────────────────────────
const _COMMON_WORDS = new Set([
    'The', 'This', 'That', 'What', 'How', 'When', 'Where', 'Which', 'Who',
    'Please', 'Add', 'Fix', 'Get', 'Set', 'Use', 'Run', 'Make', 'Build',
    'Create', 'Update', 'Delete', 'Remove', 'Show', 'Hide', 'Load', 'Save',
    'Send', 'Read', 'Write', 'Parse', 'Find', 'Search', 'Check', 'Test',
    'Move', 'Copy', 'Open', 'Close', 'Start', 'Stop', 'Enable', 'Disable',
]);

function extractComponentNames(text) {
    const matches = text.match(/\b[A-Z][a-zA-Z0-9]{2,}\b/g) || [];
    return [...new Set(matches.filter(m => !_COMMON_WORDS.has(m)))];
}

// ─────────────────────────────────────────────────────────────
// Utility: infer intent from free-text title + description
// Returns the inferred intent string or null if no match
// ─────────────────────────────────────────────────────────────
function inferIntent(title, description) {
    const combined = `${title} ${description}`.toLowerCase();

    const intentMap = [
        // Meta must come first (most specific)
        { intent: 'meta',    triggers: ['give me prompt', 'give me the prompt', 'required prompt', 'cursor prompt', 'generate prompt', 'the prompt'] },
        { intent: 'bugfix',  triggers: ['fix', 'bug', 'broken', 'error', 'issue', 'not working', 'failing', 'crash'] },
        { intent: 'enhance', triggers: ['enhance', 'improve', 'optimise', 'optimize', 'upgrade', 'performance', 'better', 'faster'] },
        { intent: 'analyse', triggers: ['analyse', 'analyze', 'review', 'understand', 'explain', 'show me'] },
        { intent: 'refactor',triggers: ['refactor', 'restructure', 'extract', 'clean up', 'cleanup', 'reorganize'] },
        { intent: 'feature', triggers: ['add', 'implement', 'create', 'new feature', 'build'] },
    ];

    for (const { intent, triggers } of intentMap) {
        if (triggers.some(t => combined.includes(t))) {
            return intent;
        }
    }
    return null;
}

let currentContextData = null;

function goToPromptStep(step) {
    // Hide all steps
    document.querySelectorAll('.wizard-content').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.wizard-step').forEach(el => el.classList.remove('active'));

    // Show target step
    document.getElementById(`prompt-step-${step}`).classList.add('active');
    
    // Update indicators up to current step
    for(let i = 1; i <= step; i++) {
        document.getElementById(`step${i}-indicator`).classList.add('active');
    }
}

function startNewPrompt() {
    document.getElementById('requirementTitle').value = '';
    document.getElementById('requirementDescription').value = '';
    document.getElementById('affectedComponents').value = '';
    document.getElementById('contextSelectionArea').innerHTML = '';
    document.getElementById('impactAnalysis').innerHTML = '';
    currentContextData = null;
    goToPromptStep(1);
}

// Analyze Context
async function analyzeContext() {
    const title = document.getElementById('requirementTitle').value.trim();
    const description = document.getElementById('requirementDescription').value.trim();
    const affectedComponents = document.getElementById('affectedComponents').value.trim();

    if (!title || !description) {
        showToast('Please fill in title and description', 'error');
        return;
    }

    const dropdownType = document.getElementById('requirementType').value;
    const inferredIntent = inferIntent(title, description);
    const resolvedIntent = inferredIntent || dropdownType;

    const intentNote = document.getElementById('intentInferredNote');
    if (inferredIntent && inferredIntent !== dropdownType) {
        document.getElementById('requirementType').value = inferredIntent;
        intentNote.style.display = 'block';
    } else {
        intentNote.style.display = 'none';
    }

    const fileTargets = extractFileTargets(`${title} ${description}`);
    // Fall back to PascalCase component/service names if no explicit file extensions found
    const componentTargets = fileTargets.length === 0 ? extractComponentNames(title) : [];
    const targetFiles = fileTargets.length > 0 ? fileTargets : componentTargets;

    document.getElementById('analyzeBtnText').style.display = 'none';
    document.getElementById('analyzeSpinner').style.display = 'inline-block';

    try {
        const query = `${resolvedIntent}: ${title}. ${description}`;
        const response = await axios.post(`${API_BASE}/api/query`, {
            query: query,
            max_components: targetFiles.length > 0 ? 5 : 20,
            target_files: targetFiles.length > 0 ? targetFiles : null,
            intent: resolvedIntent,
        }, {
            timeout: 60000  // 60 seconds timeout
        });

        currentContextData = response.data;
        currentContextData.resolvedIntent = resolvedIntent;
        currentContextData.title = title;
        currentContextData.description = description;

        populateContextSelection(currentContextData);
        goToPromptStep(2);
        
        // Load impact analysis into the final view if components exist
        if (affectedComponents) {
            const componentIds = affectedComponents.split(',').map(c => c.trim());
            showImpactAnalysis(componentIds); // We call it in background, visible on Step 3
        }

    } catch (error) {
        console.error('Error analyzing context:', error);
        showToast('Error analyzing context', 'error');
    } finally {
        document.getElementById('analyzeBtnText').style.display = 'inline';
        document.getElementById('analyzeSpinner').style.display = 'none';
    }
}

function populateContextSelection(data) {
    const area = document.getElementById('contextSelectionArea');
    area.innerHTML = '';

    const layers = data.context?.layers || {};
    let hasComponents = false;

    for (const [layer, components] of Object.entries(layers)) {
        if (components && components.length > 0) {
            hasComponents = true;
            const layerDiv = document.createElement('div');
            layerDiv.className = 'context-layer';
            
            const title = document.createElement('h4');
            title.textContent = `🔷 ${layer.toUpperCase()}`;
            title.style.marginTop = '0';
            layerDiv.appendChild(title);

            components.forEach(comp => {
                const itemDiv = document.createElement('div');
                itemDiv.className = 'context-item';

                itemDiv.innerHTML = `
                    <input type="checkbox" id="ctx_${comp.name}" data-layer="${layer}" data-id="${comp.id || comp.name}" checked>
                    <div>
                        <strong>${comp.name}</strong> <span style="color:#666; font-size:12px;">(${comp.type})</span>
                        <div style="font-size:12px; color:#888;">${comp.file_path}</div>
                    </div>
                `;
                layerDiv.appendChild(itemDiv);
            });
            area.appendChild(layerDiv);
        }
    }

    if (!hasComponents) {
        area.innerHTML = '<p>No relevant components found. You can proceed to generate an AI prompt without repository context.</p>';
    }
}

// Generate Prompt
async function generatePrompt() {
    if (!currentContextData) {
        showToast('Please analyze context first', 'error');
        return;
    }

    try {
        // Get selected component IDs from checkboxes
        const checkboxes = document.querySelectorAll('#contextSelectionArea input[type="checkbox"]');
        const selectedNames = Array.from(checkboxes).filter(cb => cb.checked).map(cb => cb.getAttribute('data-id'));

        if (selectedNames.length === 0) {
            showToast('Please select at least one component', 'error');
            return;
        }

        // Get selected generation method
        const generationMethod = document.querySelector('input[name="generationMethod"]:checked')?.value || 'llm';

        // Map old intent types to new prompt types
        const intentToPromptTypeMap = {
            'feature': 'new_feature',
            'extension': 'feature_extension',
            'enhance': 'enhancement',
            'bugfix': 'bug_fix',
            'refactor': 'refactoring',
            'analyse': 'analysis'
        };

        const promptType = intentToPromptTypeMap[currentContextData.resolvedIntent] || 'enhancement';

        // Show loading state and go to step 3
        goToPromptStep(3);
        const promptContentEl = document.getElementById('promptContent');
        promptContentEl.innerHTML = '<div style="color: #666; font-style: italic;">🔄 Initializing...</div>';

        // Use streaming endpoint for real-time feedback
        const response = await fetch(`${API_BASE}/api/prompt/generate/stream`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                type: promptType,
                title: currentContextData.title,
                description: currentContextData.description,
                components: selectedNames,
                generation_method: generationMethod
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let accumulatedPrompt = '';
        let buffer = '';

        while (true) {
            const {done, value} = await reader.read();

            if (done) break;

            // Decode chunk
            buffer += decoder.decode(value, {stream: true});

            // Process complete SSE messages
            const lines = buffer.split('\n');
            buffer = lines.pop(); // Keep incomplete line in buffer

            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    try {
                        const data = JSON.parse(line.substring(6));

                        if (data.type === 'status') {
                            // Show status message
                            promptContentEl.innerHTML = `<div style="color: #2196F3; font-style: italic;">⏳ ${data.message}</div>`;
                        } else if (data.type === 'chunk') {
                            // Append chunk to accumulated prompt
                            accumulatedPrompt += data.content;
                            promptContentEl.innerHTML = `<pre style="white-space: pre-wrap; margin: 0;">${accumulatedPrompt}<span style="animation: blink 1s infinite;">▊</span></pre>`;
                        } else if (data.type === 'complete') {
                            // Final prompt received
                            const finalPrompt = data.full_prompt || accumulatedPrompt;
                            promptContentEl.innerHTML = `<pre style="white-space: pre-wrap; margin: 0;">${finalPrompt}</pre>`;

                            const methodBadge = data.method === 'llm'
                                ? '<span style="background: #4CAF50; color: white; padding: 2px 8px; border-radius: 3px; font-size: 12px;">✨ Phi3 Enhanced</span>'
                                : '<span style="background: #2196F3; color: white; padding: 2px 8px; border-radius: 3px; font-size: 12px;">📝 Template</span>';

                            const metadataHtml = `
                                <div style="background: #f0f8ff; padding: 15px; border-radius: 5px; margin-top: 15px;">
                                    <h4 style="margin-top: 0;">📊 Prompt Metadata</h4>
                                    <p><strong>Generation Method:</strong> ${methodBadge}</p>
                                    <p><strong>Components Analyzed:</strong> ${selectedNames.length}</p>
                                    <p><strong>Prompt Type:</strong> ${promptType}</p>
                                </div>
                            `;
                            promptContentEl.innerHTML += metadataHtml;

                            showToast('Prompt generated successfully!', 'success');
                        } else if (data.type === 'error') {
                            throw new Error(data.message);
                        }
                    } catch (parseError) {
                        console.warn('Failed to parse SSE message:', line, parseError);
                    }
                }
            }
        }
    } catch (error) {
        console.error('Error generating prompt:', error);
        document.getElementById('promptContent').textContent = 'Error generating prompt. Please try again.';
        showToast(`Error: ${error.message}`, 'error');
    }
}

// Generate AI Prompt
function generateAIPrompt(type, title, description, context, targetFiles = []) {
    const typeEmojis = {
        'feature':  '🆕',
        'extension':'📈',
        'bugfix':   '🐛',
        'refactor': '♻️',
        'enhance':  '⚡',
        'analyse':  '🔍',
        'meta':     '📋',
    };

    const typeLabels = {
        'feature':  'New Feature',
        'extension':'Feature Extension',
        'bugfix':   'Bug Fix',
        'refactor': 'Refactoring',
        'enhance':  'Enhancement',
        'analyse':  'Code Analysis',
        'meta':     'Prompt Generation',
    };

    // ── Pre-process context for all intents ──────────────────
    const affectedComponents = [];
    const selectedWithCode = [];
    const selectedNames = [];
    
    const layers = context.context?.layers || {};
    Object.keys(layers).forEach(layer => {
        layers[layer].forEach(comp => {
            affectedComponents.push(`- ${comp.name} (${comp.type}) - \`${comp.file_path}\``);
            selectedNames.push(comp.name);
            if (comp.source_code) {
                selectedWithCode.push(comp);
            }
        });
    });

    // Determine effective target — prefer explicit file/component targets, then
    // extract a PascalCase name from the title, and only as a last resort use
    // the first selected component (never dump all 20 names as "Target File(s)").
    let effectiveTarget = targetFiles.length > 0 ? targetFiles.join(', ') : '';
    if (!effectiveTarget || effectiveTarget === 'the target component' || effectiveTarget === 'the codebase' || effectiveTarget === 'the target file') {
        const titleComponents = extractComponentNames(title);
        effectiveTarget = titleComponents.length > 0
            ? titleComponents[0]
            : (selectedNames.length > 0 ? selectedNames[0] : 'the selected components');
    }

    // Build consolidated code blocks
    let codeBlocks = "";
    if (selectedWithCode.length > 0) {
        selectedWithCode.forEach(comp => {
            codeBlocks += `### ${comp.name} (\`${comp.file_path}\`)\n\`\`\`\n${comp.source_code}\n\`\`\`\n\n`;
        });
    } else {
        codeBlocks = `// Source code not found in index. Please paste the relevant blocks here.`;
    }

    // ── META intent: output a ready-to-paste prompt ───────────
    if (type === 'meta') {
        return `Here is the prompt you can paste into Cursor / Claude:

${'─'.repeat(60)}
# ${title || `Enhance ${effectiveTarget}`}

${description}

**Target File(s):** \`${effectiveTarget}\`

## Review Affected Components
${affectedComponents.join('\n')}

## Instructions
1. Performance — add memoization where beneficial; consider virtualisation for large lists
2. UX — add proper loading state, empty state, and error handling UI
3. Code structure — extract reusable sub-components; move business logic into custom hooks
4. Type safety — improve TypeScript types and eliminate any implicit \`any\`
5. Maintain all existing functionality and styling conventions

## Current Implementation
${codeBlocks}

## Expected Output
- The fully updated \`${effectiveTarget}\` component code
- A brief comment above each changed section explaining what was improved and why
${'─'.repeat(60)}`;
    }

    // ── ANALYSE intent ────────────────────────────────────────
    if (type === 'analyse') {
        return `🔍 Code Analysis Request: ${title}

## What to Analyse
${description}

**Target File(s):** \`${effectiveTarget}\`

## Affected Components
${affectedComponents.join('\n')}

## Source Code
${codeBlocks}

## Analysis Tasks
1. Summarise what this code does and its role in the codebase
2. Identify any code smells, anti-patterns, or bugs
3. Flag performance concerns
4. Note type-safety issues
5. Suggest specific improvements with rationale

---
Generated by LocalMind Code Intelligence`;
    }

    // ── ENHANCE intent ────────────────────────────────────────
    if (type === 'enhance') {

        return `⚡ Enhancement: ${title}

## What to Enhance
${description}

**Target File(s):** \`${effectiveTarget}\`

## Review Affected Components
${affectedComponents.join('\n')}

## Current Implementation
${codeBlocks}

## Enhancement Goals
1. Improve performance — memoization, lazy loading, avoid unnecessary re-renders
2. Improve UX — loading/empty/error states, responsiveness
3. Improve structure — extract hooks, split oversized components
4. Improve type safety — tighten TypeScript types
5. Maintain all existing functionality and styling

## Deliverables
- Fully updated source code for \`${effectiveTarget}\`
- Detailed explanation of each enhancement made with rationale

---
Generated by LocalMind Code Intelligence`;
    }

    // Intent-specific guidance
    let specificGuidance = "";
    if (type === 'refactor') {
        specificGuidance = `
1. Optimize performance — check for unnecessary re-renders and add memoization (\`useMemo\`, \`useCallback\`, \`React.memo\`) where beneficial
2. Improve code structure — extract reusable logic into custom hooks; split oversized components if needed
3. Improve readability — simplify complex state management (e.g. pagination) and use clear variables
4. Ensure robustness — add proper error handling and strict type safety avoiding \`any\``;
    } else if (type === 'feature') {
        specificGuidance = `
1. Follow the existing architecture and code patterns from the context
2. Build for performance from the start — implement proper loading and empty states
3. Ensure strict type safety and proper error boundaries
4. Document the new functionality and update or write new tests`;
    } else {
        specificGuidance = `
1. Follow the existing code style and architectural patterns
2. Maintain strict type safety and add proper error handling
3. Consider the impact on dependent components and avoid regressions
4. Document any significant changes inline`;
    }

    let prompt = `${typeEmojis[type] || '📋'} ${typeLabels[type] || type}: ${title}

## Requirement
${description}

## Relevant Context (System and Component)
${context.formatted_context}

## Task
${ type === 'feature'   ? 'Implement this new feature following the existing code patterns provided in the context.' : ''}
${ type === 'extension' ? 'Extend the existing functionality while strictly maintaining backward compatibility.' : ''}
${ type === 'bugfix'    ? 'Identify and fix the bug while ensuring no side effects or regressions in related code.' : ''}
${ type === 'refactor'  ? `Refactor the provided code focusing on performance, structure, and readability while maintaining identical functionality.` : ''}

## Guidelines
${specificGuidance}

## Required Output Structure
Please provide your response following this exact structure to ensure quality:

### 1. Analysis & Issues Identified
- Explain your understanding of the component's role based on the context
- List what needs to be improved/fixed

### 2. Implementation Plan
- Step-by-step breakdown of exactly what you will change

### 3. Updated Code
- Provide the FULL updated source code (do not omit parts for brevity)
- Include inline comments explaining complex changes

### 4. Summary of Changes
- A brief bulleted list explaining the key improvements made

---
Generated by LocalMind Code Intelligence
`;

    return prompt;
}

// Show Impact Analysis
async function showImpactAnalysis(componentIds) {
    try {
        const response = await axios.post(`${API_BASE}/api/impact`, {
            component_ids: componentIds
        });

        const impact = response.data;

        document.getElementById('impactAnalysis').innerHTML = `
            <h4>⚠️ Impact Analysis</h4>
            <p><strong>Changed Components:</strong> ${impact.changed_components.length}</p>
            <p><strong>Affected Components:</strong> ${impact.affected_components.length}</p>

            ${impact.affected_components.length > 0 ? `
                <details>
                    <summary>View Affected Components</summary>
                    <ul>
                        ${impact.affected_components.map(comp =>
                            `<li>${comp.name} (${comp.type}) in ${comp.layer}</li>`
                        ).join('')}
                    </ul>
                </details>
            ` : ''}

            ${impact.affected_apis.length > 0 ? `
                <p><strong>Affected APIs:</strong> ${impact.affected_apis.length}</p>
                <ul>
                    ${impact.affected_apis.map(api =>
                        `<li>${api.method} ${api.endpoint}</li>`
                    ).join('')}
                </ul>
            ` : ''}
        `;

    } catch (error) {
        console.error('Error loading impact analysis:', error);
    }
}

// Copy prompt to clipboard
function copyPrompt() {
    const promptElement = document.getElementById('promptContent');
    // Try to get just the prompt text from the <pre> tag if it exists
    const preElement = promptElement.querySelector('pre');
    const prompt = preElement ? preElement.textContent : promptElement.textContent;

    navigator.clipboard.writeText(prompt).then(() => {
        showToast('Copied to clipboard!', 'success');
    }).catch(() => {
        showToast('Failed to copy', 'error');
    });
}

// Download prompt
function downloadPrompt() {
    const promptElement = document.getElementById('promptContent');
    // Try to get just the prompt text from the <pre> tag if it exists
    const preElement = promptElement.querySelector('pre');
    const prompt = preElement ? preElement.textContent : promptElement.textContent;

    const blob = new Blob([prompt], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'ai-prompt.md';
    a.click();
    URL.revokeObjectURL(url);
    showToast('Prompt downloaded!', 'success');
}

// Load example
function loadExample(exampleType) {
    const examples = {
        'password-reset': {
            type: 'feature',
            title: 'Add Password Reset Functionality',
            description: `Implement email-based password reset functionality:

1. User requests password reset by entering email
2. System sends email with secure reset link (valid for 1 hour)
3. User clicks link and enters new password
4. Password is validated and updated
5. User is notified of successful password change

Requirements:
- Use secure token generation
- Email template should match existing design
- Add rate limiting to prevent abuse
- Update both mobile and web apps
- Add appropriate error messages`,
            components: 'AuthService, UserRepository'
        },
        '2fa': {
            type: 'feature',
            title: 'Implement Two-Factor Authentication',
            description: `Add 2FA with SMS verification:

1. User enables 2FA in profile settings
2. Phone number is verified via SMS code
3. On login, after password, user receives SMS code
4. User enters 6-digit code to complete login
5. Option to remember device for 30 days

Requirements:
- Integrate with SMS provider (Twilio)
- Store phone numbers encrypted
- Add backup codes for account recovery
- Update login flow in mobile and web apps`,
            components: 'AuthController, AuthService, LoginScreen, LoginPage'
        },
        'login-bug': {
            type: 'bugfix',
            title: 'Fix Login Timeout Issue on Mobile',
            description: `Users report getting logged out unexpectedly on mobile app:

Issue:
- Session expires after 5 minutes of inactivity
- Should expire after 30 minutes
- Happens only on mobile, web works fine

Investigation needed:
- Check JWT token expiry settings
- Verify mobile app token refresh logic
- Check if API interceptor is working correctly

Expected fix:
- Token should be refreshed automatically
- Session should last 30 minutes of inactivity
- User should not lose data when session refreshes`,
            components: 'AuthService, ApiClient, LoginScreen'
        }
    };

    const example = examples[exampleType];
    if (example) {
        document.getElementById('requirementType').value = example.type;
        document.getElementById('requirementTitle').value = example.title;
        document.getElementById('requirementDescription').value = example.description;
        document.getElementById('affectedComponents').value = example.components;

        // Switch to requirements tab
        document.querySelector('[data-tab="requirements"]').click();

        showToast('Example loaded!', 'success');
    }
}

// Search Components
async function searchComponents() {
    const query = document.getElementById('searchQuery').value.trim();

    if (!query) {
        showToast('Please enter a search query', 'error');
        return;
    }

    try {
        const response = await axios.get(`${API_BASE}/api/search`, {
            params: { q: query, limit: 20 }
        });

        const results = response.data.results;

        if (results.length === 0) {
            document.getElementById('searchResults').innerHTML = `
                <p style="text-align: center; color: #6c757d; padding: 40px;">
                    No results found for "${query}"
                </p>
            `;
            return;
        }

        let html = `<h3>Found ${results.length} results</h3>`;

        results.forEach(result => {
            html += `
                <div class="search-result" onclick="showNodeDetails('${result.id}')">
                    <h4>${result.name}</h4>
                    <div class="meta">
                        <span>${result.type}</span> •
                        <span>${result.layer}</span> •
                        <span>${result.file_path}</span>
                    </div>
                    ${result.description ? `<div class="description">${result.description}</div>` : ''}
                </div>
            `;
        });

        document.getElementById('searchResults').innerHTML = html;

    } catch (error) {
        console.error('Error searching:', error);
        showToast('Search failed', 'error');
    }
}

// Search node in graph
async function searchGraphNode() {
    const query = document.getElementById('graphSearchInput').value.trim().toLowerCase();
    if (!query) return;

    if (!currentGraph || !window.allGraphNodes) {
        showToast('Graph not loaded', 'error');
        return;
    }

    // Try to find exact match first
    let foundNode = window.allGraphNodes.find(n => (n.name && n.name.toLowerCase() === query) || n.id.toLowerCase() === query);
    
    // If no exact match, find partial match
    if (!foundNode) {
        foundNode = window.allGraphNodes.find(n => (n.name && n.name.toLowerCase().includes(query)) || n.id.toLowerCase().includes(query));
    }

    if (foundNode) {
        // Clear layer filter if it's hiding our search result
        const currentLayer = document.getElementById('layerFilter').value;
        if (currentLayer && foundNode.layer !== currentLayer) {
            document.getElementById('layerFilter').value = '';
            filterGraph();
        }

        currentGraph.selectNodes([foundNode.id]);
        currentGraph.focus(foundNode.id, {
            scale: 1.2,
            animation: {
                duration: 500,
                easingFunction: 'easeInOutQuad'
            }
        });
        await showNodeDetails(foundNode.id);
        showToast(`Found node: ${foundNode.name || foundNode.id}`, 'success');
    } else {
        showToast('Node not found in graph', 'error');
    }
}

// Load Statistics
async function loadStats() {
    try {
        const response = await axios.get(`${API_BASE}/api/stats`);
        const stats = response.data;

        // Totals
        document.getElementById('statsContent').innerHTML = `
            <h3>Overview</h3>
            <p><strong>Total Components:</strong> ${stats.totals.components}</p>
            <p><strong>Total Relationships:</strong> ${stats.totals.relationships}</p>
            <p><strong>API Endpoints:</strong> ${stats.totals.apis}</p>
            <p><strong>Infrastructure Components:</strong> ${stats.totals.infrastructure}</p>
        `;

        // Stats grid
        let gridHtml = '';

        // By layer
        for (const [layer, count] of Object.entries(stats.by_layer)) {
            gridHtml += `
                <div class="stat-card">
                    <div class="number">${count}</div>
                    <div class="label">${layer}</div>
                </div>
            `;
        }

        document.getElementById('statsGrid').innerHTML = gridHtml;

    } catch (error) {
        console.error('Error loading stats:', error);
        document.getElementById('statsContent').innerHTML = `
            <p class="loading">Error loading statistics. Please index a repository first.</p>
        `;
    }
}

// Show Toast
function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast ${type}`;
    toast.classList.add('show');

    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

// Progress Modal Functions
function showProgressModal() {
    const modal = document.getElementById('progressModal');
    if (!modal) {
        console.error('Progress modal not found in DOM');
        return;
    }

    modal.classList.add('show');

    // Reset modal state
    stepsCompleted = 0;
    document.getElementById('modalStepTitle').textContent = 'Initializing...';
    document.getElementById('modalOverallPercent').textContent = '0%';
    document.getElementById('modalOverallProgress').style.width = '0%';
    document.getElementById('modalCurrentActivity').textContent = 'Starting indexing process...';
    document.getElementById('modalStepsLog').innerHTML = '';
    document.getElementById('stepsCount').textContent = '0 steps completed';
    document.getElementById('modalStats').style.display = 'none';
    document.getElementById('modalActionBtn').style.display = 'none';

    // Show close button immediately so user can dismiss modal anytime
    const modalClose = document.querySelector('.modal-close');
    if (modalClose) modalClose.style.display = 'block';
}

function closeProgressModal() {
    const modal = document.getElementById('progressModal');
    modal.classList.remove('show');
    
    // Reset button state
    document.getElementById('indexBtnText').style.display = 'inline';
    document.getElementById('indexSpinner').style.display = 'none';
}

function addStepToLog(message, type) {
    const stepsLog = document.getElementById('modalStepsLog');
    if (!stepsLog) return;
    
    const timestamp = new Date().toLocaleTimeString();
    
    const stepItem = document.createElement('div');
    stepItem.className = 'step-item ' + type;
    
    const icons = {
        'success': '✓',
        'info': '→',
        'warning': '⚠',
        'error': '✗'
    };
    
    const icon = icons[type] || '→';
    
    stepItem.innerHTML = '<span class="step-icon">' + icon + '</span><span class="step-text">[' + timestamp + '] ' + message + '</span>';
    
    stepsLog.appendChild(stepItem);
    
    // Auto-scroll to bottom
    stepsLog.scrollTop = stepsLog.scrollHeight;
    
    // Update step count
    if (type === 'success' || message.includes('✅')) {
        stepsCompleted++;
        document.getElementById('stepsCount').textContent = stepsCompleted + ' steps completed';
    }
}
