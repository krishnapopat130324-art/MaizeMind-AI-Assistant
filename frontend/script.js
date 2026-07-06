// ============================================
// API CONFIGURATION
// ============================================
const API_URL = 'http://localhost:8000';

// ============================================
// STATE
// ============================================
let network = null;
let isAnalyzing = false;
let lastData = null;

console.log('🚀 MaizeMind loaded!');
console.log('📡 API URL:', API_URL);

// ============================================
// LOAD SAMPLE
// ============================================
async function loadSample() {
    console.log('📄 Loading sample...');
    try {
        const response = await fetch(`${API_URL}/sample`);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        const data = await response.json();
        document.getElementById('inputText').value = data.sample_text;
        showStatus('✅ Sample loaded! Click "Analyze" to see the argument map.', 'success');
    } catch (error) {
        showStatus('❌ Error loading sample. Is API running?', 'error');
        console.error('Load sample error:', error);
    }
}

// ============================================
// CLEAR ALL
// ============================================
function clearAll() {
    document.getElementById('inputText').value = '';
    if (network) {
        network.destroy();
        network = null;
    }
    document.getElementById('placeholder').style.display = 'block';
    document.getElementById('stats').style.display = 'none';
    document.getElementById('detailsSection').style.display = 'none';
    document.getElementById('gapsSection').style.display = 'none';
    showStatus('🗑️ Cleared', 'info');
}

// ============================================
// SHOW STATUS
// ============================================
function showStatus(message, type) {
    const status = document.getElementById('status');
    status.textContent = message;
    status.className = 'status status-' + type;
    status.style.display = 'block';
    console.log('📢 Status:', message);
}

// ============================================
// MAIN ANALYZE FUNCTION
// ============================================
async function analyzeText() {
    console.log('🔍 Analyze clicked!');
    
    const text = document.getElementById('inputText').value.trim();
    console.log('📝 Text length:', text.length);
    
    if (text.length < 10) {
        showStatus('⚠️ Please enter at least 10 characters.', 'error');
        return;
    }
    
    if (isAnalyzing) return;
    isAnalyzing = true;
    
    const btn = document.getElementById('analyzeBtn');
    btn.disabled = true;
    btn.innerHTML = '⏳ Analyzing...';
    
    showStatus('🧠 Analyzing your text... This may take 10-30 seconds.', 'info');
    
    try {
        console.log('📡 Sending request to:', `${API_URL}/analyze`);
        
        const response = await fetch(`${API_URL}/analyze`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: text })
        });
        
        console.log('📨 Response status:', response.status);
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error('❌ Error:', errorText);
            throw new Error(`HTTP ${response.status}: ${errorText}`);
        }
        
        const data = await response.json();
        console.log('✅ Data received:', data);
        
        if (data.success) {
            // Store data
            lastData = data;
            
            // Hide placeholder
            document.getElementById('placeholder').style.display = 'none';
            
            // Render graph
            renderGraph(data.graph);
            
            // Update stats
            updateStats(data);
            
            // Show detailed breakdown
            showDetails(data);
            
            // Show gaps
            if (data.gaps && data.gaps.length > 0) {
                showGaps(data.gaps);
            } else {
                document.getElementById('gapsSection').style.display = 'none';
            }
            
            showStatus(`✅ Success! Found ${data.graph.nodes.length} nodes and ${data.graph.edges.length} relationships.`, 'success');
        } else {
            showStatus('❌ Error: ' + (data.message || 'Unknown error'), 'error');
        }
    } catch (error) {
        console.error('❌ Error:', error);
        showStatus('❌ ' + error.message, 'error');
    } finally {
        isAnalyzing = false;
        btn.disabled = false;
        btn.innerHTML = '🔍 Analyze & Visualize';
    }
}

// ============================================
// RENDER GRAPH
// ============================================
function renderGraph(graphData) {
    console.log('📊 Rendering graph with', graphData.nodes.length, 'nodes');
    
    if (network) {
        network.destroy();
        network = null;
    }
    
    if (!graphData || !graphData.nodes || graphData.nodes.length === 0) {
        showStatus('⚠️ No arguments found. Try different text.', 'error');
        return;
    }
    
    const container = document.getElementById('graph');
    
    const nodes = new vis.DataSet(graphData.nodes);
    const edges = new vis.DataSet(graphData.edges);
    
    const options = {
        layout: {
            hierarchical: {
                enabled: true,
                direction: 'LR',
                levelSeparation: 150,
                nodeSpacing: 150
            }
        },
        nodes: {
            shape: 'box',
            margin: 10,
            widthConstraint: { maximum: 200 },
            font: { size: 13, color: '#1a1a2e' }
        },
        edges: {
            arrows: 'to',
            smooth: true,
            font: { size: 10, align: 'middle' }
        },
        physics: { enabled: false },
        interaction: {
            hover: true,
            tooltipDelay: 200
        }
    };
    
    network = new vis.Network(container, { nodes, edges }, options);
    
    setTimeout(() => {
        if (network) network.fit();
    }, 300);
}

// ============================================
// UPDATE STATS
// ============================================
function updateStats(data) {
    const graph = data.graph;
    
    let claims = 0, evidence = 0;
    graph.nodes.forEach(node => {
        if (node.node_type === 'claim' || node.type === 'claim' || node.type === 'main' || node.type === 'supporting' || node.type === 'counter' || node.type === 'conclusion') {
            claims++;
        } else if (node.node_type === 'evidence' || node.type === 'evidence') {
            evidence++;
        }
    });
    
    document.getElementById('claimCount').textContent = claims || graph.nodes.length;
    document.getElementById('evidenceCount').textContent = evidence || 0;
    document.getElementById('relationCount').textContent = graph.edges.length;
    document.getElementById('gapCount').textContent = data.gaps ? data.gaps.length : 0;
    
    document.getElementById('stats').style.display = 'grid';
}

// ============================================
// SHOW DETAILED BREAKDOWN - NEW FUNCTION
// ============================================
function showDetails(data) {
    const graph = data.graph;
    const detailsSection = document.getElementById('detailsSection');
    const claimsList = document.getElementById('claimsList');
    const evidenceList = document.getElementById('evidenceList');
    const relationshipsList = document.getElementById('relationshipsList');
    
    // Clear lists
    claimsList.innerHTML = '';
    evidenceList.innerHTML = '';
    relationshipsList.innerHTML = '';
    
    // Get nodes and edges
    const nodes = graph.nodes;
    const edges = graph.edges;
    
    // Separate claims and evidence
    const claims = nodes.filter(n => n.node_type === 'claim' || n.type === 'claim' || n.type === 'main' || n.type === 'supporting' || n.type === 'counter' || n.type === 'conclusion');
    const evidences = nodes.filter(n => n.node_type === 'evidence' || n.type === 'evidence');
    
    // Display Claims
    if (claims.length === 0) {
        claimsList.innerHTML = '<div class="detail-item" style="color:#8a8aaa;">No claims found</div>';
    } else {
        claims.forEach(claim => {
            const div = document.createElement('div');
            div.className = 'detail-item';
            const typeBadge = claim.type || 'claim';
            const badgeClass = typeBadge === 'main' ? 'badge-main' : 
                              typeBadge === 'counter' ? 'badge-counter' :
                              typeBadge === 'conclusion' ? 'badge-conclusion' : 'badge-supporting';
            div.innerHTML = `
                <span class="item-id">${claim.id}</span>
                ${claim.title || claim.label}
                <span class="item-type ${badgeClass}">${typeBadge}</span>
            `;
            claimsList.appendChild(div);
        });
    }
    
    // Display Evidence
    if (evidences.length === 0) {
        evidenceList.innerHTML = '<div class="detail-item" style="color:#8a8aaa;">No evidence found</div>';
    } else {
        evidences.forEach(evidence => {
            const div = document.createElement('div');
            div.className = 'detail-item evidence';
            div.innerHTML = `
                <span class="item-id">${evidence.id}</span>
                ${evidence.title || evidence.label}
            `;
            evidenceList.appendChild(div);
        });
    }
    
    // Display Relationships
    if (edges.length === 0) {
        relationshipsList.innerHTML = '<div class="detail-item" style="color:#8a8aaa;">No relationships found</div>';
    } else {
        edges.forEach(edge => {
            const div = document.createElement('div');
            div.className = 'detail-item';
            const label = edge.label || 'supports';
            const relationClass = label === 'supports' ? 'supports' : 
                                 label === 'challenges' ? 'challenges' : '';
            div.innerHTML = `
                <span class="item-id">${edge.from}</span>
                <span class="arrow">→</span>
                <span class="${relationClass}">${label}</span>
                <span class="arrow">→</span>
                <span class="item-id">${edge.to}</span>
            `;
            relationshipsList.appendChild(div);
        });
    }
    
    // Show the details section
    detailsSection.style.display = 'block';
}

// ============================================
// SHOW GAPS
// ============================================
function showGaps(gaps) {
    const list = document.getElementById('gapsList');
    list.innerHTML = '';
    
    gaps.forEach((gap, i) => {
        const text = gap.label || gap.text || 'Unnamed claim';
        const li = document.createElement('li');
        li.innerHTML = `<strong>${i+1}. ${text}</strong> — This claim lacks supporting evidence.`;
        list.appendChild(li);
    });
    
    document.getElementById('gapsSection').style.display = 'block';
}

// ============================================
// CHECK API
// ============================================
async function checkAPI() {
    try {
        console.log('🔍 Checking API...');
        const response = await fetch(`${API_URL}/`);
        if (response.ok) {
            const data = await response.json();
            console.log('✅ API:', data);
            document.getElementById('apiStatus').textContent = '● Online';
            document.getElementById('apiStatus').className = 'status-badge online';
            showStatus('✅ Connected to API! Ready to analyze.', 'success');
            setTimeout(() => {
                document.getElementById('status').style.display = 'none';
            }, 3000);
        } else {
            document.getElementById('apiStatus').textContent = '● Offline';
            document.getElementById('apiStatus').className = 'status-badge offline';
            showStatus('⚠️ API is responding but not as expected.', 'error');
        }
    } catch (error) {
        console.error('❌ API error:', error);
        document.getElementById('apiStatus').textContent = '● Offline';
        document.getElementById('apiStatus').className = 'status-badge offline';
        showStatus('⚠️ API not running! Run: python app.py', 'error');
    }
}

// ============================================
// KEYBOARD SHORTCUT
// ============================================
document.addEventListener('keydown', function(e) {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        e.preventDefault();
        analyzeText();
    }
});

// ============================================
// INIT
// ============================================
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 MaizeMind initialized');
    checkAPI();
});

// Make functions global
window.loadSample = loadSample;
window.clearAll = clearAll;
window.analyzeText = analyzeText;