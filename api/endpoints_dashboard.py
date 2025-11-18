"""Real-time dashboard endpoints for monitoring"""
from fastapi import APIRouter
from fastapi.responses import JSONResponse, HTMLResponse
from api.utils.advanced_metrics import AdvancedMetrics
import json

router = APIRouter()
advanced_metrics = AdvancedMetrics()


@router.get("/dashboard")
async def dashboard():
    """Real-time dashboard HTML"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Autoppia Miner Dashboard</title>
        <meta http-equiv="refresh" content="5">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            
            body { 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
                color: #fff;
            }
            
            .container { 
                max-width: 1600px; 
                margin: 0 auto; 
            }
            
            .header { 
                text-align: center; 
                margin-bottom: 40px;
                padding: 30px;
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                border-radius: 20px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            }
            
            .header h1 { 
                font-size: 2.5em; 
                margin-bottom: 10px;
                background: linear-gradient(45deg, #fff, #f0f0f0);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }
            
            .header p { 
                font-size: 1.2em; 
                opacity: 0.9;
            }
            
            .metrics-grid { 
                display: grid; 
                grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); 
                gap: 25px; 
                margin-bottom: 30px; 
            }
            
            .metric-card { 
                background: rgba(255, 255, 255, 0.15);
                backdrop-filter: blur(10px);
                padding: 30px; 
                border-radius: 20px; 
                border: 1px solid rgba(255, 255, 255, 0.2);
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
                transition: transform 0.3s ease, box-shadow 0.3s ease;
                position: relative;
                overflow: hidden;
            }
            
            .metric-card::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 4px;
                background: linear-gradient(90deg, #4CAF50, #8BC34A);
            }
            
            .metric-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 12px 40px rgba(0, 0, 0, 0.2);
            }
            
            .metric-icon {
                font-size: 2.5em;
                margin-bottom: 15px;
                opacity: 0.9;
            }
            
            .metric-value { 
                font-size: 3em; 
                font-weight: 700; 
                color: #fff;
                margin-bottom: 10px;
                text-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
            }
            
            .metric-label { 
                color: rgba(255, 255, 255, 0.8); 
                font-size: 1.1em;
                text-transform: uppercase;
                letter-spacing: 1px;
                font-weight: 500;
            }
            
            .section { 
                background: rgba(255, 255, 255, 0.15);
                backdrop-filter: blur(10px);
                padding: 30px; 
                border-radius: 20px; 
                margin-bottom: 25px; 
                border: 1px solid rgba(255, 255, 255, 0.2);
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            }
            
            .section-title { 
                font-size: 1.8em; 
                margin-bottom: 20px; 
                color: #fff;
                font-weight: 600;
                display: flex;
                align-items: center;
                gap: 10px;
            }
            
            .section-title::before {
                content: '▸';
                color: #4CAF50;
                font-size: 1.2em;
            }
            
            table { 
                width: 100%; 
                border-collapse: collapse; 
                background: rgba(255, 255, 255, 0.05);
                border-radius: 10px;
                overflow: hidden;
            }
            
            th, td { 
                padding: 15px; 
                text-align: left; 
                border-bottom: 1px solid rgba(255, 255, 255, 0.1); 
            }
            
            th { 
                color: #fff;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                font-size: 0.9em;
                background: rgba(255, 255, 255, 0.1);
            }
            
            td {
                color: rgba(255, 255, 255, 0.9);
            }
            
            tr:hover {
                background: rgba(255, 255, 255, 0.1);
            }
            
            .status-good { 
                color: #4CAF50; 
                font-weight: 600;
            }
            
            .status-warning { 
                color: #FFC107; 
                font-weight: 600;
            }
            
            .status-error { 
                color: #F44336; 
                font-weight: 600;
            }
            
            .badge {
                display: inline-block;
                padding: 5px 12px;
                border-radius: 20px;
                font-size: 0.85em;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            
            .badge-success {
                background: rgba(76, 175, 80, 0.3);
                color: #4CAF50;
                border: 1px solid rgba(76, 175, 80, 0.5);
            }
            
            .badge-error {
                background: rgba(244, 67, 54, 0.3);
                color: #F44336;
                border: 1px solid rgba(244, 67, 54, 0.5);
            }
            
            .loading {
                text-align: center;
                padding: 40px;
                color: rgba(255, 255, 255, 0.7);
                font-size: 1.2em;
            }
            
            .pulse {
                animation: pulse 2s infinite;
            }
            
            @keyframes pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.5; }
            }
            
            .stats-row {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
                margin-top: 15px;
            }
            
            .stat-item {
                background: rgba(255, 255, 255, 0.1);
                padding: 15px;
                border-radius: 10px;
                text-align: center;
            }
            
            .stat-value {
                font-size: 1.8em;
                font-weight: 700;
                color: #fff;
            }
            
            .stat-label {
                font-size: 0.9em;
                color: rgba(255, 255, 255, 0.7);
                margin-top: 5px;
            }
            
            @media (max-width: 768px) {
                .header h1 { font-size: 1.8em; }
                .metric-value { font-size: 2em; }
                .metrics-grid { grid-template-columns: 1fr; }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚀 Autoppia Miner Dashboard</h1>
                <p>Real-Time Performance Monitoring</p>
            </div>
            
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-icon">📊</div>
                    <div class="metric-value" id="success-rate">-</div>
                    <div class="metric-label">Success Rate</div>
                </div>
                <div class="metric-card">
                    <div class="metric-icon">⚡</div>
                    <div class="metric-value" id="avg-time">-</div>
                    <div class="metric-label">Avg Response Time</div>
                </div>
                <div class="metric-card">
                    <div class="metric-icon">📈</div>
                    <div class="metric-value" id="total-requests">-</div>
                    <div class="metric-label">Total Requests</div>
                </div>
                <div class="metric-card">
                    <div class="metric-icon">❤️</div>
                    <div class="metric-value" id="health-score">-</div>
                    <div class="metric-label">Health Score</div>
                </div>
            </div>
            
            <div class="section">
                <div class="section-title">Agent Performance</div>
                <div id="agent-performance" class="loading pulse">Loading...</div>
            </div>
            
            <div class="section">
                <div class="section-title">Recent Validator Activity</div>
                <div id="validator-activity" class="loading pulse">Loading...</div>
            </div>
            
            <div class="section">
                <div class="section-title">Error Summary</div>
                <div id="error-summary" class="loading pulse">Loading...</div>
            </div>
            
            <div class="section">
                <div class="section-title">Performance Stats</div>
                <div id="performance-stats" class="loading pulse">Loading...</div>
            </div>
        </div>
        
        <script>
            async function loadMetrics() {
                try {
                    const response = await fetch('/api/dashboard/metrics');
                    const data = await response.json();
                    
                    // Update main metrics
                    document.getElementById('success-rate').textContent = (data.overview.success_rate || 0).toFixed(1) + '%';
                    document.getElementById('avg-time').textContent = (data.performance.avg_response_time || 0).toFixed(3) + 's';
                    document.getElementById('total-requests').textContent = (data.overview.total_requests || 0).toLocaleString();
                    document.getElementById('health-score').textContent = (data.health_score || 0).toFixed(1);
                    
                    // Color code success rate
                    const successRateEl = document.getElementById('success-rate');
                    const successRate = data.overview.success_rate || 0;
                    if (successRate >= 90) {
                        successRateEl.style.color = '#4CAF50';
                    } else if (successRate >= 70) {
                        successRateEl.style.color = '#FFC107';
                    } else {
                        successRateEl.style.color = '#F44336';
                    }
                    
                    // Color code health score
                    const healthScoreEl = document.getElementById('health-score');
                    const healthScore = data.health_score || 0;
                    if (healthScore >= 90) {
                        healthScoreEl.style.color = '#4CAF50';
                    } else if (healthScore >= 70) {
                        healthScoreEl.style.color = '#FFC107';
                    } else {
                        healthScoreEl.style.color = '#F44336';
                    }
                    
                    // Agent performance
                    if (Object.keys(data.agents || {}).length > 0) {
                        let agentHtml = '<table><tr><th>Agent</th><th>Success Rate</th><th>Total Requests</th><th>Avg Time</th></tr>';
                        for (const [agent, stats] of Object.entries(data.agents)) {
                            const successClass = stats.success_rate >= 80 ? 'status-good' : stats.success_rate >= 60 ? 'status-warning' : 'status-error';
                            agentHtml += `<tr>
                                <td><strong>${agent.charAt(0).toUpperCase() + agent.slice(1)}</strong></td>
                                <td class="${successClass}">${stats.success_rate.toFixed(2)}%</td>
                                <td>${stats.total.toLocaleString()}</td>
                                <td>${stats.avg_response_time.toFixed(3)}s</td>
                            </tr>`;
                        }
                        agentHtml += '</table>';
                        document.getElementById('agent-performance').innerHTML = agentHtml;
                    } else {
                        document.getElementById('agent-performance').innerHTML = '<div class="loading">No agent data yet</div>';
                    }
                    
                    // Validator activity
                    if (data.validators && data.validators.recent_activity && data.validators.recent_activity.length > 0) {
                        let validatorHtml = '<table><tr><th>Time</th><th>IP Address</th><th>Status</th><th>Response Time</th></tr>';
                        data.validators.recent_activity.slice(-10).reverse().forEach(activity => {
                            const status = activity.success 
                                ? '<span class="badge badge-success">✓ Success</span>' 
                                : '<span class="badge badge-error">✗ Failed</span>';
                            validatorHtml += `<tr>
                                <td>${new Date(activity.time).toLocaleTimeString()}</td>
                                <td><code>${activity.ip}</code></td>
                                <td>${status}</td>
                                <td>${activity.response_time.toFixed(3)}s</td>
                            </tr>`;
                        });
                        validatorHtml += '</table>';
                        document.getElementById('validator-activity').innerHTML = validatorHtml;
                    } else {
                        document.getElementById('validator-activity').innerHTML = '<div class="loading">No validator activity yet</div>';
                    }
                    
                    // Error summary
                    if (data.errors && data.errors.error_types && Object.keys(data.errors.error_types).length > 0) {
                        let errorHtml = '<table><tr><th>Error Type</th><th>Count</th></tr>';
                        for (const [errorType, count] of Object.entries(data.errors.error_types)) {
                            errorHtml += `<tr>
                                <td><code>${errorType}</code></td>
                                <td class="status-error">${count}</td>
                            </tr>`;
                        }
                        errorHtml += '</table>';
                        document.getElementById('error-summary').innerHTML = errorHtml;
                    } else {
                        document.getElementById('error-summary').innerHTML = '<div class="loading">No errors! 🎉</div>';
                    }
                    
                    // Performance stats
                    const perfStats = data.performance || {};
                    let perfHtml = '<div class="stats-row">';
                    perfHtml += `<div class="stat-item">
                        <div class="stat-value">${(perfStats.p95_response_time || 0).toFixed(3)}s</div>
                        <div class="stat-label">P95 Response Time</div>
                    </div>`;
                    perfHtml += `<div class="stat-item">
                        <div class="stat-value">${(perfStats.p99_response_time || 0).toFixed(3)}s</div>
                        <div class="stat-label">P99 Response Time</div>
                    </div>`;
                    perfHtml += `<div class="stat-item">
                        <div class="stat-value">${(perfStats.requests_per_minute || 0).toFixed(1)}</div>
                        <div class="stat-label">Requests/Min</div>
                    </div>`;
                    perfHtml += `<div class="stat-item">
                        <div class="stat-value">${(data.caching?.cache_hit_rate || 0).toFixed(1)}%</div>
                        <div class="stat-label">Cache Hit Rate</div>
                    </div>`;
                    perfHtml += '</div>';
                    document.getElementById('performance-stats').innerHTML = perfHtml;
                    
                } catch (error) {
                    console.error('Error loading metrics:', error);
                    document.getElementById('agent-performance').innerHTML = '<div class="loading status-error">Error loading data</div>';
                }
            }
            
            loadMetrics();
            setInterval(loadMetrics, 5000); // Update every 5 seconds
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@router.get("/dashboard/metrics")
async def dashboard_metrics():
    """Get real-time metrics as JSON"""
    metrics = advanced_metrics.get_comprehensive_metrics()
    metrics["health_score"] = advanced_metrics.get_health_score()
    return JSONResponse(content=metrics)

