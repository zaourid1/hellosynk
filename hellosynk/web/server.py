"""
FastAPI Web Server for HelloSynk Operating System UI
"""

import asyncio
from typing import Optional, List, Dict, Any
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from hellosynk import HelloSynk
from hellosynk.core.llm import LLMProvider
from hellosynk.skills import SkillRegistry


app = FastAPI(title="HelloSynk OS", version="0.1.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Allow iframe embedding
@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    # Remove X-Frame-Options to allow iframe embedding
    response.headers.pop("X-Frame-Options", None)
    # Use Content-Security-Policy to allow embedding from any origin
    response.headers["Content-Security-Policy"] = "frame-ancestors *;"
    return response

# Global HelloSynk instance
hellosynk_instance: Optional[HelloSynk] = None
skill_registry: Optional[SkillRegistry] = None


class ChatRequest(BaseModel):
    message: str
    provider: Optional[str] = "openai"
    model: Optional[str] = None
    api_key: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    executions: list
    intent: Optional[str] = None
    reasoning: Optional[str] = None


@app.on_event("startup")
async def startup():
    """Initialize HelloSynk on startup"""
    global hellosynk_instance, skill_registry
    try:
        hellosynk_instance = HelloSynk()
        await hellosynk_instance.initialize()
        skill_registry = SkillRegistry()
        await skill_registry.load_skills()
    except Exception as e:
        print(f"Warning: HelloSynk initialization failed: {e}")


@app.get("/", response_class=HTMLResponse)
async def get_index():
    """Serve the HelloSynk OS interface"""
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HelloSynk OS</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        :root {
            --bg-primary: #0a0e27;
            --bg-secondary: #151b3d;
            --bg-tertiary: #1e2746;
            --accent-primary: #667eea;
            --accent-secondary: #764ba2;
            --text-primary: #ffffff;
            --text-secondary: #a0aec0;
            --border-color: #2d3748;
            --success: #48bb78;
            --warning: #ed8936;
            --error: #f56565;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            height: 100vh;
            overflow: hidden;
            display: flex;
            flex-direction: column;
        }
        
        /* Top Bar */
        .top-bar {
            background: var(--bg-secondary);
            border-bottom: 1px solid var(--border-color);
            padding: 12px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            height: 50px;
        }
        
        .logo {
            display: flex;
            align-items: center;
            gap: 10px;
            font-size: 18px;
            font-weight: 600;
        }
        
        .system-status {
            display: flex;
            gap: 20px;
            align-items: center;
        }
        
        .status-item {
            display: flex;
            align-items: center;
            gap: 6px;
            font-size: 12px;
            color: var(--text-secondary);
        }
        
        .status-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: var(--success);
        }
        
        .status-dot.warning {
            background: var(--warning);
        }
        
        .status-dot.error {
            background: var(--error);
        }
        
        /* Main Container */
        .main-container {
            display: flex;
            flex: 1;
            overflow: hidden;
        }
        
        /* Sidebar */
        .sidebar {
            width: 250px;
            background: var(--bg-secondary);
            border-right: 1px solid var(--border-color);
            display: flex;
            flex-direction: column;
            overflow-y: auto;
        }
        
        .nav-section {
            padding: 20px;
        }
        
        .nav-title {
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: var(--text-secondary);
            margin-bottom: 10px;
        }
        
        .nav-item {
            padding: 12px 16px;
            margin: 4px 0;
            border-radius: 8px;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 12px;
            transition: all 0.2s;
            color: var(--text-secondary);
        }
        
        .nav-item:hover {
            background: var(--bg-tertiary);
            color: var(--text-primary);
        }
        
        .nav-item.active {
            background: linear-gradient(135deg, var(--accent-primary) 0%, var(--accent-secondary) 100%);
            color: var(--text-primary);
        }
        
        .nav-icon {
            width: 20px;
            text-align: center;
        }
        
        /* Content Area */
        .content-area {
            flex: 1;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        
        .view {
            display: none;
            flex: 1;
            padding: 30px;
            overflow-y: auto;
        }
        
        .view.active {
            display: flex;
            flex-direction: column;
        }
        
        .view-header {
            margin-bottom: 24px;
        }
        
        .view-title {
            font-size: 28px;
            font-weight: 600;
            margin-bottom: 8px;
        }
        
        .view-subtitle {
            color: var(--text-secondary);
            font-size: 14px;
        }
        
        /* Dashboard */
        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .stat-card {
            background: var(--bg-secondary);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 20px;
        }
        
        .stat-label {
            font-size: 12px;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 8px;
        }
        
        .stat-value {
            font-size: 32px;
            font-weight: 600;
            color: var(--accent-primary);
        }
        
        .stat-description {
            font-size: 12px;
            color: var(--text-secondary);
            margin-top: 8px;
        }
        
        /* Skills Grid */
        .skills-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 16px;
        }
        
        .skill-card {
            background: var(--bg-secondary);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 16px;
            cursor: pointer;
            transition: all 0.2s;
        }
        
        .skill-card:hover {
            border-color: var(--accent-primary);
            transform: translateY(-2px);
        }
        
        .skill-name {
            font-weight: 600;
            margin-bottom: 4px;
        }
        
        .skill-description {
            font-size: 12px;
            color: var(--text-secondary);
            margin-bottom: 8px;
        }
        
        .skill-meta {
            display: flex;
            justify-content: space-between;
            font-size: 11px;
            color: var(--text-secondary);
        }
        
        .skill-status {
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 10px;
        }
        
        .skill-status.enabled {
            background: rgba(72, 187, 120, 0.2);
            color: var(--success);
        }
        
        .skill-status.disabled {
            background: rgba(245, 101, 101, 0.2);
            color: var(--error);
        }
        
        /* Terminal/Chat */
        .terminal-container {
            background: var(--bg-secondary);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            display: flex;
            flex-direction: column;
            height: 600px;
            overflow: hidden;
        }
        
        .terminal-header {
            background: var(--bg-tertiary);
            padding: 12px 16px;
            border-bottom: 1px solid var(--border-color);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .terminal-title {
            font-size: 12px;
            font-weight: 600;
        }
        
        .terminal-body {
            flex: 1;
            padding: 20px;
            overflow-y: auto;
            font-family: 'Monaco', 'Menlo', 'Courier New', monospace;
            font-size: 13px;
            line-height: 1.6;
        }
        
        .terminal-input-area {
            padding: 16px;
            border-top: 1px solid var(--border-color);
            display: flex;
            gap: 10px;
        }
        
        .terminal-input {
            flex: 1;
            background: var(--bg-tertiary);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 12px 16px;
            color: var(--text-primary);
            font-family: 'Monaco', 'Menlo', 'Courier New', monospace;
            font-size: 13px;
            outline: none;
        }
        
        .terminal-input:focus {
            border-color: var(--accent-primary);
        }
        
        .terminal-button {
            background: linear-gradient(135deg, var(--accent-primary) 0%, var(--accent-secondary) 100%);
            border: none;
            border-radius: 8px;
            padding: 12px 24px;
            color: var(--text-primary);
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s;
        }
        
        .terminal-button:hover:not(:disabled) {
            transform: translateY(-2px);
        }
        
        .terminal-button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        
        .message {
            margin-bottom: 16px;
        }
        
        .message.user {
            color: var(--accent-primary);
        }
        
        .message.assistant {
            color: var(--text-primary);
        }
        
        .message.system {
            color: var(--text-secondary);
            font-style: italic;
        }
        
        .message-time {
            color: var(--text-secondary);
            font-size: 11px;
            margin-left: 8px;
        }
        
        .execution-result {
            margin-top: 8px;
            padding: 8px 12px;
            background: var(--bg-tertiary);
            border-left: 3px solid var(--accent-primary);
            border-radius: 4px;
            font-size: 12px;
        }
        
        /* Memory Graph */
        .memory-stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin-bottom: 24px;
        }
        
        /* Scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: var(--bg-secondary);
        }
        
        ::-webkit-scrollbar-thumb {
            background: var(--bg-tertiary);
            border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: var(--border-color);
        }
        
        /* Loading */
        .loading {
            display: inline-flex;
            gap: 4px;
        }
        
        .loading-dot {
            width: 6px;
            height: 6px;
            background: var(--accent-primary);
            border-radius: 50%;
            animation: bounce 1.4s infinite ease-in-out both;
        }
        
        .loading-dot:nth-child(1) { animation-delay: -0.32s; }
        .loading-dot:nth-child(2) { animation-delay: -0.16s; }
        
        @keyframes bounce {
            0%, 80%, 100% { transform: scale(0); }
            40% { transform: scale(1); }
        }
    </style>
</head>
<body>
    <!-- Top Bar -->
    <div class="top-bar">
        <div class="logo">
            <span>🤖</span>
            <span>HelloSynk OS</span>
        </div>
        <div class="system-status">
            <div class="status-item">
                <div class="status-dot" id="systemStatus"></div>
                <span>System</span>
            </div>
            <div class="status-item">
                <div class="status-dot" id="llmStatus"></div>
                <span>LLM</span>
            </div>
            <div class="status-item">
                <span id="skillCount">0 Skills</span>
            </div>
            <div class="status-item">
                <span id="memoryNodes">0 Nodes</span>
            </div>
        </div>
    </div>
    
    <!-- Main Container -->
    <div class="main-container">
        <!-- Sidebar -->
        <div class="sidebar">
            <div class="nav-section">
                <div class="nav-title">Navigation</div>
                <div class="nav-item active" data-view="dashboard">
                    <span class="nav-icon">📊</span>
                    <span>Dashboard</span>
                </div>
                <div class="nav-item" data-view="skills">
                    <span class="nav-icon">🔌</span>
                    <span>Skills</span>
                </div>
                <div class="nav-item" data-view="memory">
                    <span class="nav-icon">🧠</span>
                    <span>Memory</span>
                </div>
                <div class="nav-item" data-view="terminal">
                    <span class="nav-icon">💻</span>
                    <span>Terminal</span>
                </div>
            </div>
        </div>
        
        <!-- Content Area -->
        <div class="content-area">
            <!-- Dashboard View -->
            <div class="view active" id="dashboard">
                <div class="view-header">
                    <div class="view-title">System Dashboard</div>
                    <div class="view-subtitle">Overview of your HelloSynk operating system</div>
                </div>
                <div class="dashboard-grid" id="dashboardGrid">
                    <!-- Stats will be populated by JavaScript -->
                </div>
            </div>
            
            <!-- Skills View -->
            <div class="view" id="skills">
                <div class="view-header">
                    <div class="view-title">Installed Skills</div>
                    <div class="view-subtitle">Manage your system capabilities</div>
                </div>
                <div class="skills-grid" id="skillsGrid">
                    <!-- Skills will be populated by JavaScript -->
                </div>
            </div>
            
            <!-- Memory View -->
            <div class="view" id="memory">
                <div class="view-header">
                    <div class="view-title">Memory Graph</div>
                    <div class="view-subtitle">Structured knowledge representation</div>
                </div>
                <div class="memory-stats" id="memoryStats">
                    <!-- Memory stats will be populated by JavaScript -->
                </div>
            </div>
            
            <!-- Terminal View -->
            <div class="view" id="terminal">
                <div class="view-header">
                    <div class="view-title">Terminal</div>
                    <div class="view-subtitle">Interact with HelloSynk agents</div>
                </div>
                <div class="terminal-container">
                    <div class="terminal-header">
                        <div class="terminal-title">HelloSynk Terminal</div>
                    </div>
                    <div class="terminal-body" id="terminalBody">
                        <div class="message system">
                            HelloSynk OS v0.1.0 initialized. Type a command or question to begin.
                            <span class="message-time"></span>
                        </div>
                    </div>
                    <div class="terminal-input-area">
                        <input type="text" class="terminal-input" id="terminalInput" placeholder="Enter command or question..." autocomplete="off" />
                        <button class="terminal-button" id="terminalSend">Send</button>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // Navigation
        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', () => {
                document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
                document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
                item.classList.add('active');
                document.getElementById(item.dataset.view).classList.add('active');
            });
        });
        
        // System Status
        async function updateSystemStatus() {
            try {
                const response = await fetch('/api/system/status');
                const data = await response.json();
                
                document.getElementById('systemStatus').className = 
                    'status-dot' + (data.system_ready ? '' : ' error');
                document.getElementById('llmStatus').className = 
                    'status-dot' + (data.llm_configured ? '' : ' warning');
                document.getElementById('skillCount').textContent = 
                    `${data.skills_count} Skills`;
                document.getElementById('memoryNodes').textContent = 
                    `${data.memory_nodes} Nodes`;
            } catch (error) {
                console.error('Failed to update system status:', error);
            }
        }
        
        // Dashboard
        async function loadDashboard() {
            try {
                const response = await fetch('/api/system/status');
                const data = await response.json();
                
                const grid = document.getElementById('dashboardGrid');
                grid.innerHTML = `
                    <div class="stat-card">
                        <div class="stat-label">System Status</div>
                        <div class="stat-value">${data.system_ready ? '✓' : '✗'}</div>
                        <div class="stat-description">${data.system_ready ? 'Operational' : 'Initializing'}</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">Installed Skills</div>
                        <div class="stat-value">${data.skills_count}</div>
                        <div class="stat-description">${data.skills_enabled} enabled</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">Memory Nodes</div>
                        <div class="stat-value">${data.memory_nodes}</div>
                        <div class="stat-description">Knowledge graph size</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">LLM Provider</div>
                        <div class="stat-value">${data.llm_provider || 'N/A'}</div>
                        <div class="stat-description">${data.llm_configured ? 'Configured' : 'Not configured'}</div>
                    </div>
                `;
            } catch (error) {
                console.error('Failed to load dashboard:', error);
            }
        }
        
        // Skills
        async function loadSkills() {
            try {
                const response = await fetch('/api/skills');
                const data = await response.json();
                
                const grid = document.getElementById('skillsGrid');
                grid.innerHTML = data.skills.map(skill => `
                    <div class="skill-card">
                        <div class="skill-name">${skill.name}</div>
                        <div class="skill-description">${skill.description}</div>
                        <div class="skill-meta">
                            <span>v${skill.version}</span>
                            <span class="skill-status ${skill.enabled ? 'enabled' : 'disabled'}">
                                ${skill.enabled ? 'Enabled' : 'Disabled'}
                            </span>
                        </div>
                    </div>
                `).join('');
            } catch (error) {
                console.error('Failed to load skills:', error);
            }
        }
        
        // Memory
        async function loadMemory() {
            try {
                const response = await fetch('/api/memory/stats');
                const data = await response.json();
                
                const stats = document.getElementById('memoryStats');
                stats.innerHTML = `
                    <div class="stat-card">
                        <div class="stat-label">Total Nodes</div>
                        <div class="stat-value">${data.total_nodes}</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">Total Edges</div>
                        <div class="stat-value">${data.total_edges}</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">Node Types</div>
                        <div class="stat-value">${data.node_types || 0}</div>
                    </div>
                `;
            } catch (error) {
                console.error('Failed to load memory stats:', error);
            }
        }
        
        // Terminal
        const terminalBody = document.getElementById('terminalBody');
        const terminalInput = document.getElementById('terminalInput');
        const terminalSend = document.getElementById('terminalSend');
        
        function addMessage(text, type = 'system') {
            const message = document.createElement('div');
            message.className = `message ${type}`;
            const time = new Date().toLocaleTimeString();
            message.innerHTML = `${text} <span class="message-time">${time}</span>`;
            terminalBody.appendChild(message);
            terminalBody.scrollTop = terminalBody.scrollHeight;
        }
        
        async function sendMessage() {
            const message = terminalInput.value.trim();
            if (!message) return;
            
            terminalInput.value = '';
            terminalSend.disabled = true;
            
            addMessage(`> ${message}`, 'user');
            addMessage('Processing<span class="loading"><span class="loading-dot"></span><span class="loading-dot"></span><span class="loading-dot"></span></span>', 'system');
            
            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: message }),
                });
                
                const data = await response.json();
                
                // Remove loading message
                terminalBody.removeChild(terminalBody.lastChild);
                
                addMessage(data.response, 'assistant');
                
                if (data.executions && data.executions.length > 0) {
                    const execDiv = document.createElement('div');
                    execDiv.className = 'execution-result';
                    execDiv.innerHTML = '<strong>Executed Skills:</strong><br>' +
                        data.executions.map(e => 
                            `${e.status === 'success' ? '✓' : '✗'} ${e.skill}: ${e.status}`
                        ).join('<br>');
                    terminalBody.appendChild(execDiv);
                }
            } catch (error) {
                terminalBody.removeChild(terminalBody.lastChild);
                addMessage(`Error: ${error.message}`, 'system');
            } finally {
                terminalSend.disabled = false;
                terminalInput.focus();
            }
        }
        
        terminalSend.addEventListener('click', sendMessage);
        terminalInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
        
        // View switching
        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', () => {
                const view = item.dataset.view;
                if (view === 'dashboard') loadDashboard();
                else if (view === 'skills') loadSkills();
                else if (view === 'memory') loadMemory();
            });
        });
        
        // Initial load
        updateSystemStatus();
        loadDashboard();
        setInterval(updateSystemStatus, 5000);
    </script>
</body>
</html>
"""
    return html_content


@app.get("/api/system/status")
async def get_system_status():
    """Get system status information"""
    global hellosynk_instance, skill_registry
    
    try:
        skills_count = 0
        skills_enabled = 0
        if skill_registry:
            skills = skill_registry.list_skills()
            skills_count = len(skills)
            skills_enabled = sum(1 for s in skills if s.get("enabled", False))
        
        memory_nodes = 0
        if hellosynk_instance and hellosynk_instance.memory:
            memory_nodes = len(hellosynk_instance.memory.graph.nodes())
        
        llm_configured = hellosynk_instance is not None and hellosynk_instance.llm_client is not None
        llm_provider = None
        if hellosynk_instance and hellosynk_instance.llm_client:
            llm_provider = hellosynk_instance.llm_provider.value if hasattr(hellosynk_instance.llm_provider, 'value') else str(hellosynk_instance.llm_provider)
        
        return {
            "system_ready": hellosynk_instance is not None,
            "llm_configured": llm_configured,
            "llm_provider": llm_provider,
            "skills_count": skills_count,
            "skills_enabled": skills_enabled,
            "memory_nodes": memory_nodes,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/skills")
async def get_skills():
    """Get list of installed skills"""
    global skill_registry
    
    if not skill_registry:
        return {"skills": []}
    
    try:
        skills = skill_registry.list_skills()
        return {"skills": skills}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/memory/stats")
async def get_memory_stats():
    """Get memory graph statistics"""
    global hellosynk_instance
    
    if not hellosynk_instance or not hellosynk_instance.memory:
        return {
            "total_nodes": 0,
            "total_edges": 0,
            "node_types": 0,
        }
    
    try:
        graph = hellosynk_instance.memory.graph
        return {
            "total_nodes": len(graph.nodes()),
            "total_edges": len(graph.edges()),
            "node_types": len(set(n.get("type") for n in graph.nodes(data=True) if n)),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Handle chat messages"""
    global hellosynk_instance
    
    if not hellosynk_instance:
        try:
            hellosynk_instance = HelloSynk(
                llm_provider=LLMProvider(request.provider) if request.provider else LLMProvider.OPENAI,
                llm_model=request.model,
                llm_api_key=request.api_key,
            )
            await hellosynk_instance.initialize()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to initialize HelloSynk: {str(e)}")
    
    try:
        result = await hellosynk_instance.process(request.message)
        
        return ChatResponse(
            response=result.get("response", ""),
            executions=result.get("executions", []),
            intent=result.get("intent"),
            reasoning=result.get("reasoning"),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
