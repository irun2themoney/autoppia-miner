"""Real-time dashboard endpoints for monitoring"""
from fastapi import APIRouter
from fastapi.responses import JSONResponse, HTMLResponse
from ..utils.advanced_metrics import AdvancedMetrics
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
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #1a1a1a; color: #fff; }
            .container { max-width: 1400px; margin: 0 auto; }
            .header { text-align: center; margin-bottom: 30px; }
            .metrics-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }
            .metric-card { background: #2a2a2a; padding: 20px; border-radius: 8px; border: 1px solid #444; }
            .metric-value { font-size: 2em; font-weight: bold; color: #4CAF50; }
            .metric-label { color: #aaa; margin-top: 5px; }
            .section { background: #2a2a2a; padding: 20px; border-radius: 8px; margin-bottom: 20px; border: 1px solid #444; }
            .section-title { font-size: 1.5em; margin-bottom: 15px; color: #4CAF50; }
            table { width: 100%; border-collapse: collapse; }
            th, td { padding: 10px; text-align: left; border-bottom: 1px solid #444; }
            th { color: #4CAF50; }
            .status-good { color: #4CAF50; }
            .status-warning { color: #FFC107; }
            .status-error { color: #F44336; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚀 Autoppia Miner - Real-Time Dashboard</h1>
                <p>Live performance monitoring</p>
            </div>
            
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-value" id="success-rate">-</div>
                    <div class="metric-label">Success Rate</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value" id="avg-time">-</div>
                    <div class="metric-label">Avg Response Time</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value" id="total-requests">-</div>
                    <div class="metric-label">Total Requests</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value" id="health-score">-</div>
                    <div class="metric-label">Health Score</div>
                </div>
            </div>
            
            <div class="section">
                <div class="section-title">Agent Performance</div>
                <div id="agent-performance">Loading...</div>
            </div>
            
            <div class="section">
                <div class="section-title">Recent Validator Activity</div>
                <div id="validator-activity">Loading...</div>
            </div>
            
            <div class="section">
                <div class="section-title">Error Summary</div>
                <div id="error-summary">Loading...</div>
            </div>
        </div>
        
        <script>
            async function loadMetrics() {
                try {
                    const response = await fetch('/api/dashboard/metrics');
                    const data = await response.json();
                    
                    // Update metrics
                    document.getElementById('success-rate').textContent = data.overview.success_rate + '%';
                    document.getElementById('avg-time').textContent = data.performance.avg_response_time + 's';
                    document.getElementById('total-requests').textContent = data.overview.total_requests;
                    document.getElementById('health-score').textContent = data.health_score;
                    
                    // Agent performance
                    let agentHtml = '<table><tr><th>Agent</th><th>Success Rate</th><th>Total</th><th>Avg Time</th></tr>';
                    for (const [agent, stats] of Object.entries(data.agents)) {
                        agentHtml += `<tr>
                            <td>${agent}</td>
                            <td class="status-good">${stats.success_rate.toFixed(2)}%</td>
                            <td>${stats.total}</td>
                            <td>${stats.avg_response_time.toFixed(3)}s</td>
                        </tr>`;
                    }
                    agentHtml += '</table>';
                    document.getElementById('agent-performance').innerHTML = agentHtml;
                    
                    // Validator activity
                    let validatorHtml = '<table><tr><th>Time</th><th>IP</th><th>Status</th><th>Response Time</th></tr>';
                    data.validators.recent_activity.slice(-10).reverse().forEach(activity => {
                        const status = activity.success ? '<span class="status-good">✓</span>' : '<span class="status-error">✗</span>';
                        validatorHtml += `<tr>
                            <td>${new Date(activity.time).toLocaleTimeString()}</td>
                            <td>${activity.ip}</td>
                            <td>${status}</td>
                            <td>${activity.response_time.toFixed(3)}s</td>
                        </tr>`;
                    });
                    validatorHtml += '</table>';
                    document.getElementById('validator-activity').innerHTML = validatorHtml;
                    
                    // Error summary
                    let errorHtml = '<table><tr><th>Error Type</th><th>Count</th></tr>';
                    for (const [errorType, count] of Object.entries(data.errors.error_types)) {
                        errorHtml += `<tr><td>${errorType}</td><td class="status-error">${count}</td></tr>`;
                    }
                    errorHtml += '</table>';
                    document.getElementById('error-summary').innerHTML = errorHtml;
                } catch (error) {
                    console.error('Error loading metrics:', error);
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

