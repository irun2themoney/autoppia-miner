"""Real-time dashboard endpoints for monitoring"""
from fastapi import APIRouter
from fastapi.responses import JSONResponse, HTMLResponse
from api.utils.advanced_metrics import AdvancedMetrics
import json

router = APIRouter()
advanced_metrics = AdvancedMetrics()


@router.get("/dashboard")
async def dashboard():
    """Real-time dashboard HTML - Minimal & Compact"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Miner Dashboard</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                background: #f5f5f5;
                padding: 20px;
                color: #333;
                font-size: 14px;
            }
            .header { 
                margin-bottom: 20px;
                padding-bottom: 15px;
                border-bottom: 2px solid #ddd;
            }
            .header h1 { font-size: 24px; font-weight: 600; }
            .header p { color: #666; margin-top: 5px; font-size: 13px; }
            .metrics { 
                display: grid; 
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); 
                gap: 15px; 
                margin-bottom: 20px; 
            }
            .metric { 
                background: white;
                padding: 15px; 
                border-radius: 6px; 
                border: 1px solid #e0e0e0;
            }
            .metric-label { 
                color: #666; 
                font-size: 12px; 
                margin-bottom: 8px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            .metric-value { 
                font-size: 28px; 
                font-weight: 600; 
                color: #333;
            }
            .metric-value.good { color: #4CAF50; }
            .metric-value.warning { color: #FF9800; }
            .metric-value.error { color: #F44336; }
            .section { 
                background: white;
                padding: 15px; 
                border-radius: 6px; 
                margin-bottom: 15px; 
                border: 1px solid #e0e0e0;
            }
            .section-title { 
                font-size: 14px; 
                font-weight: 600; 
                margin-bottom: 12px; 
                color: #333;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            table { 
                width: 100%; 
                border-collapse: collapse; 
                font-size: 13px;
            }
            th, td { 
                padding: 10px; 
                text-align: left; 
                border-bottom: 1px solid #f0f0f0; 
            }
            th { 
                color: #666;
                font-weight: 600;
                font-size: 12px;
                text-transform: uppercase;
            }
            td { color: #333; }
            tr:hover { background: #f9f9f9; }
            .status-good { color: #4CAF50; font-weight: 600; }
            .status-error { color: #F44336; font-weight: 600; }
            .badge { 
                padding: 3px 8px; 
                border-radius: 3px; 
                font-size: 11px; 
                font-weight: 600; 
            }
            .badge-success { background: #e8f5e9; color: #4CAF50; }
            .badge-error { background: #ffebee; color: #F44336; }
            .loading { 
                text-align: center; 
                padding: 20px; 
                color: #999; 
                font-size: 13px; 
            }
            .compact-row {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
                gap: 10px;
                margin-top: 10px;
            }
            .compact-stat {
                text-align: center;
                padding: 10px;
                background: #f9f9f9;
                border-radius: 4px;
            }
            .compact-stat-value {
                font-size: 20px;
                font-weight: 600;
                color: #333;
            }
            .compact-stat-label {
                font-size: 11px;
                color: #666;
                margin-top: 4px;
            }
            code { 
                background: #f5f5f5; 
                padding: 2px 6px; 
                border-radius: 3px; 
                font-size: 12px; 
                font-family: 'Monaco', 'Courier New', monospace;
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Miner Dashboard</h1>
            <p>Last updated: <span id="last-update">-</span></p>
        </div>
        
        <div class="metrics">
            <div class="metric">
                <div class="metric-label">Success Rate</div>
                <div class="metric-value" id="success-rate">-</div>
            </div>
            <div class="metric">
                <div class="metric-label">Avg Response</div>
                <div class="metric-value" id="avg-time">-</div>
            </div>
            <div class="metric">
                <div class="metric-label">Total Requests</div>
                <div class="metric-value" id="total-requests">-</div>
            </div>
            <div class="metric">
                <div class="metric-label">Health Score</div>
                <div class="metric-value" id="health-score">-</div>
            </div>
        </div>
        
        <div class="section">
            <div class="section-title">Agents</div>
            <div id="agent-performance" class="loading">Loading...</div>
        </div>
        
        <div class="section">
            <div class="section-title">Recent Activity</div>
            <div id="validator-activity" class="loading">Loading...</div>
        </div>
        
        <div class="section">
            <div class="section-title">Errors</div>
            <div id="error-summary" class="loading">Loading...</div>
        </div>
        
        <div class="section">
            <div class="section-title">Performance</div>
            <div id="performance-stats" class="loading">Loading...</div>
        </div>
        
        <script>
            async function loadMetrics() {
                try {
                    const response = await fetch('/api/dashboard/metrics');
                    if (!response.ok) {
                        throw new Error('Failed to fetch metrics');
                    }
                    const data = await response.json();
                    
                    // Update timestamp
                    document.getElementById('last-update').textContent = new Date().toLocaleTimeString();
                    
                    // Update main metrics
                    const successRate = (data.overview?.success_rate || 0).toFixed(1);
                    const successRateEl = document.getElementById('success-rate');
                    successRateEl.textContent = successRate + '%';
                    successRateEl.className = 'metric-value ' + 
                        (successRate >= 90 ? 'good' : successRate >= 70 ? 'warning' : 'error');
                    
                    document.getElementById('avg-time').textContent = (data.performance?.avg_response_time || 0).toFixed(3) + 's';
                    document.getElementById('total-requests').textContent = (data.overview?.total_requests || 0).toLocaleString();
                    
                    const healthScore = (data.health_score || 0).toFixed(1);
                    const healthScoreEl = document.getElementById('health-score');
                    healthScoreEl.textContent = healthScore;
                    healthScoreEl.className = 'metric-value ' + 
                        (healthScore >= 90 ? 'good' : healthScore >= 70 ? 'warning' : 'error');
                    
                    // Agent performance
                    if (data.agents && Object.keys(data.agents).length > 0) {
                        let html = '<table><tr><th>Agent</th><th>Success</th><th>Total</th><th>Time</th></tr>';
                        for (const [agent, stats] of Object.entries(data.agents)) {
                            const cls = stats.success_rate >= 80 ? 'status-good' : 'status-error';
                            html += `<tr>
                                <td>${agent}</td>
                                <td class="${cls}">${stats.success_rate.toFixed(1)}%</td>
                                <td>${stats.total}</td>
                                <td>${stats.avg_response_time.toFixed(3)}s</td>
                            </tr>`;
                        }
                        html += '</table>';
                        document.getElementById('agent-performance').innerHTML = html;
                    } else {
                        document.getElementById('agent-performance').innerHTML = '<div class="loading">No data</div>';
                    }
                    
                    // Validator activity
                    if (data.validators?.recent_activity?.length > 0) {
                        let html = '<table><tr><th>Time</th><th>IP</th><th>Status</th><th>Time</th></tr>';
                        data.validators.recent_activity.slice(-5).reverse().forEach(a => {
                            const status = a.success 
                                ? '<span class="badge badge-success">OK</span>' 
                                : '<span class="badge badge-error">FAIL</span>';
                            html += `<tr>
                                <td>${new Date(a.time).toLocaleTimeString()}</td>
                                <td><code>${a.ip}</code></td>
                                <td>${status}</td>
                                <td>${a.response_time.toFixed(3)}s</td>
                            </tr>`;
                        });
                        html += '</table>';
                        document.getElementById('validator-activity').innerHTML = html;
                    } else {
                        document.getElementById('validator-activity').innerHTML = '<div class="loading">No activity</div>';
                    }
                    
                    // Errors
                    if (data.errors?.error_types && Object.keys(data.errors.error_types).length > 0) {
                        let html = '<table><tr><th>Type</th><th>Count</th></tr>';
                        for (const [type, count] of Object.entries(data.errors.error_types)) {
                            html += `<tr><td><code>${type}</code></td><td class="status-error">${count}</td></tr>`;
                        }
                        html += '</table>';
                        document.getElementById('error-summary').innerHTML = html;
                    } else {
                        document.getElementById('error-summary').innerHTML = '<div class="loading">No errors</div>';
                    }
                    
                    // Performance stats
                    const perf = data.performance || {};
                    let perfHtml = '<div class="compact-row">';
                    perfHtml += `<div class="compact-stat">
                        <div class="compact-stat-value">${(perf.p95_response_time || 0).toFixed(3)}s</div>
                        <div class="compact-stat-label">P95</div>
                    </div>`;
                    perfHtml += `<div class="compact-stat">
                        <div class="compact-stat-value">${(perf.p99_response_time || 0).toFixed(3)}s</div>
                        <div class="compact-stat-label">P99</div>
                    </div>`;
                    perfHtml += `<div class="compact-stat">
                        <div class="compact-stat-value">${(perf.requests_per_minute || 0).toFixed(1)}</div>
                        <div class="compact-stat-label">Req/min</div>
                    </div>`;
                    perfHtml += `<div class="compact-stat">
                        <div class="compact-stat-value">${(data.caching?.cache_hit_rate || 0).toFixed(1)}%</div>
                        <div class="compact-stat-label">Cache</div>
                    </div>`;
                    perfHtml += '</div>';
                    document.getElementById('performance-stats').innerHTML = perfHtml;
                    
                } catch (error) {
                    console.error('Error:', error);
                    document.getElementById('agent-performance').innerHTML = 
                        '<div class="loading status-error">Error: ' + error.message + '</div>';
                }
            }
            
            loadMetrics();
            setInterval(loadMetrics, 5000);
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

