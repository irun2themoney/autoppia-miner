"""Real-time dashboard endpoints for monitoring"""
from fastapi import APIRouter
from fastapi.responses import JSONResponse, HTMLResponse
import json

router = APIRouter()

# Lazy import to avoid circular dependency
def get_advanced_metrics():
    """Get the shared advanced_metrics instance"""
    from api.endpoints import advanced_metrics
    return advanced_metrics


@router.get("/dashboard")
async def dashboard():
    """Real-time dashboard HTML - Ultra Compact with Valuable Metrics"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Miner Dashboard - Live</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                background: #0a0e27;
                padding: 8px;
                color: #e0e0e0;
                font-size: 11px;
                line-height: 1.3;
            }
            .header { 
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 8px;
                padding: 6px 10px;
                background: #1a1f3a;
                border-radius: 4px;
                border: 1px solid #2a2f4a;
            }
            .header h1 { font-size: 16px; font-weight: 600; color: #4CAF50; }
            .header-info { font-size: 10px; color: #888; }
            .refresh-indicator {
                display: inline-block;
                width: 8px;
                height: 8px;
                border-radius: 50%;
                background: #4CAF50;
                margin-right: 6px;
                animation: pulse 2s infinite;
            }
            @keyframes pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.3; }
            }
            .grid { 
                display: grid; 
                grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); 
                gap: 6px; 
                margin-bottom: 8px; 
            }
            .card { 
                background: #1a1f3a;
                padding: 8px; 
                border-radius: 4px; 
                border: 1px solid #2a2f4a;
            }
            .card-title { 
                color: #888; 
                font-size: 9px; 
                margin-bottom: 4px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            .card-value { 
                font-size: 20px; 
                font-weight: 600; 
                color: #e0e0e0;
                line-height: 1.2;
            }
            .card-value.good { color: #4CAF50; }
            .card-value.warning { color: #FF9800; }
            .card-value.error { color: #F44336; }
            .card-sub { 
                font-size: 9px; 
                color: #666; 
                margin-top: 2px;
            }
            .section { 
                background: #1a1f3a;
                padding: 8px; 
                border-radius: 4px; 
                margin-bottom: 6px; 
                border: 1px solid #2a2f4a;
            }
            .section-title { 
                font-size: 10px; 
                font-weight: 600; 
                margin-bottom: 6px; 
                color: #4CAF50;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            table { 
                width: 100%; 
                border-collapse: collapse; 
                font-size: 10px;
            }
            th, td { 
                padding: 4px 6px; 
                text-align: left; 
                border-bottom: 1px solid #2a2f4a; 
            }
            th { 
                color: #888;
                font-weight: 600;
                font-size: 9px;
                text-transform: uppercase;
            }
            td { color: #e0e0e0; }
            tr:hover { background: #252a4a; }
            .status-good { color: #4CAF50; font-weight: 600; }
            .status-error { color: #F44336; font-weight: 600; }
            .badge { 
                padding: 2px 6px; 
                border-radius: 3px; 
                font-size: 9px; 
                font-weight: 600; 
            }
            .badge-success { background: #1b5e20; color: #4CAF50; }
            .badge-error { background: #b71c1c; color: #F44336; }
            .compact-row {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(80px, 1fr));
                gap: 4px;
                margin-top: 4px;
            }
            .compact-stat {
                text-align: center;
                padding: 6px 4px;
                background: #252a4a;
                border-radius: 3px;
                border: 1px solid #2a2f4a;
            }
            .compact-stat-value {
                font-size: 14px;
                font-weight: 600;
                color: #e0e0e0;
            }
            .compact-stat-label {
                font-size: 8px;
                color: #888;
                margin-top: 2px;
            }
            code { 
                background: #0a0e27; 
                padding: 1px 4px; 
                border-radius: 2px; 
                font-size: 9px; 
                font-family: 'Monaco', 'Courier New', monospace;
                color: #4CAF50;
            }
            .mini-chart {
                height: 30px;
                display: flex;
                align-items: flex-end;
                gap: 2px;
                margin-top: 4px;
            }
            .mini-bar {
                flex: 1;
                background: #4CAF50;
                border-radius: 2px 2px 0 0;
                min-height: 2px;
            }
            .loading { 
                text-align: center; 
                padding: 10px; 
                color: #666; 
                font-size: 10px; 
            }
            .two-col {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 6px;
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>⚡ Miner Dashboard</h1>
            <div class="header-info">
                <span class="refresh-indicator"></span>
                <span id="last-update">Loading...</span> | Auto-refresh: 5s
            </div>
        </div>
        
        <div class="grid">
            <div class="card">
                <div class="card-title">Success Rate</div>
                <div class="card-value" id="success-rate">-</div>
                <div class="card-sub" id="success-detail">-</div>
            </div>
            <div class="card">
                <div class="card-title">Total Requests</div>
                <div class="card-value" id="total-requests">-</div>
                <div class="card-sub" id="req-detail">-</div>
            </div>
            <div class="card">
                <div class="card-title">Health Score</div>
                <div class="card-value" id="health-score">-</div>
                <div class="card-sub" id="health-detail">-</div>
            </div>
            <div class="card">
                <div class="card-title">Avg Response</div>
                <div class="card-value" id="avg-response">-</div>
                <div class="card-sub" id="response-detail">-</div>
            </div>
            <div class="card">
                <div class="card-title">Cache Hit Rate</div>
                <div class="card-value" id="cache-hit">-</div>
                <div class="card-sub" id="cache-detail">-</div>
            </div>
            <div class="card">
                <div class="card-title">Validators</div>
                <div class="card-value" id="validators">-</div>
                <div class="card-sub" id="validator-detail">-</div>
            </div>
        </div>
        
        <div class="two-col">
            <div class="section">
                <div class="section-title">⚡ Performance</div>
                <div id="performance" class="loading">Loading...</div>
            </div>
            <div class="section">
                <div class="section-title">🏆 God-Tier Features</div>
                <div id="god-tier" class="loading">Loading...</div>
            </div>
        </div>
        
        <div class="section">
            <div class="section-title">📊 Recent Activity (Last 10)</div>
            <div id="recent-activity" class="loading">Loading...</div>
        </div>
        
        <div class="two-col">
            <div class="section">
                <div class="section-title">🎯 Task Types</div>
                <div id="task-types" class="loading">Loading...</div>
            </div>
            <div class="section">
                <div class="section-title">🔍 Top Validators</div>
                <div id="top-validators" class="loading">Loading...</div>
            </div>
        </div>
        
        <div class="section">
            <div class="section-title">❌ Errors</div>
            <div id="errors" class="loading">Loading...</div>
        </div>
        
        <script>
            async function loadMetrics() {
                try {
                    const response = await fetch('/api/dashboard/metrics');
                    if (!response.ok) throw new Error('Failed to fetch: ' + response.status);
                    const data = await response.json();
                    
                    const now = new Date();
                    document.getElementById('last-update').textContent = now.toLocaleString('en-US', { 
                        timeZone: 'America/Chicago',
                        hour: '2-digit',
                        minute: '2-digit',
                        second: '2-digit',
                        hour12: true
                    }) + ' CT';
                    
                    const overview = data.overview || {};
                    const perf = data.performance || {};
                    const caching = data.caching || {};
                    const validators = data.validators || {};
                    
                    // Main metrics
                    const total = parseInt(overview.total_requests || 0);
                    const success = parseInt(overview.successful_requests || 0);
                    const failed = parseInt(overview.failed_requests || 0);
                    const successRate = total > 0 ? parseFloat(overview.success_rate || 0).toFixed(1) : '0.0';
                    
                    document.getElementById('total-requests').textContent = total.toLocaleString();
                    document.getElementById('total-requests').className = 'card-value' + (total > 0 ? ' good' : '');
                    document.getElementById('req-detail').textContent = `${success} ✓ / ${failed} ✗`;
                    
                    const successEl = document.getElementById('success-rate');
                    successEl.textContent = successRate + '%';
                    successEl.className = 'card-value ' + 
                        (parseFloat(successRate) >= 90 ? 'good' : parseFloat(successRate) >= 70 ? 'warning' : 'error');
                    document.getElementById('success-detail').textContent = `${success} successful`;
                    
                    const health = parseFloat(data.health_score || 0).toFixed(1);
                    const healthEl = document.getElementById('health-score');
                    healthEl.textContent = health;
                    healthEl.className = 'card-value ' + 
                        (parseFloat(health) >= 90 ? 'good' : parseFloat(health) >= 70 ? 'warning' : 'error');
                    document.getElementById('health-detail').textContent = 'Overall health';
                    
                    const avgTime = (perf.avg_response_time || 0).toFixed(3);
                    document.getElementById('avg-response').textContent = avgTime + 's';
                    document.getElementById('avg-response').className = 'card-value' + 
                        (parseFloat(avgTime) < 3 ? ' good' : parseFloat(avgTime) < 5 ? ' warning' : ' error');
                    document.getElementById('response-detail').textContent = `P95: ${(perf.p95_response_time || 0).toFixed(3)}s`;
                    
                    const cacheRate = (caching.cache_hit_rate || 0).toFixed(1);
                    document.getElementById('cache-hit').textContent = cacheRate + '%';
                    document.getElementById('cache-hit').className = 'card-value' + 
                        (parseFloat(cacheRate) >= 50 ? ' good' : parseFloat(cacheRate) >= 30 ? ' warning' : '');
                    document.getElementById('cache-detail').textContent = `${caching.cache_hits || 0} hits / ${caching.cache_misses || 0} misses`;
                    
                    const uniqueValidators = parseInt(validators.unique_validators || 0);
                    document.getElementById('validators').textContent = uniqueValidators;
                    document.getElementById('validators').className = 'card-value' + (uniqueValidators > 0 ? ' good' : '');
                    document.getElementById('validator-detail').textContent = 'Unique validators';
                    
                    // Performance
                    let perfHtml = '<div class="compact-row">';
                    perfHtml += `<div class="compact-stat"><div class="compact-stat-value">${avgTime}s</div><div class="compact-stat-label">Avg</div></div>`;
                    perfHtml += `<div class="compact-stat"><div class="compact-stat-value">${(perf.p95_response_time || 0).toFixed(3)}s</div><div class="compact-stat-label">P95</div></div>`;
                    perfHtml += `<div class="compact-stat"><div class="compact-stat-value">${(perf.p99_response_time || 0).toFixed(3)}s</div><div class="compact-stat-label">P99</div></div>`;
                    perfHtml += `<div class="compact-stat"><div class="compact-stat-value">${(perf.requests_per_minute || 0).toFixed(1)}</div><div class="compact-stat-label">Req/min</div></div>`;
                    perfHtml += `<div class="compact-stat"><div class="compact-stat-value">${(overview.uptime_hours || 0).toFixed(1)}h</div><div class="compact-stat-label">Uptime</div></div>`;
                    perfHtml += '</div>';
                    document.getElementById('performance').innerHTML = perfHtml;
                    
                    // God-tier features
                    const vector = data.vector_memory || {};
                    const mutations = data.mutations || {};
                    let godHtml = '<div class="compact-row">';
                    godHtml += `<div class="compact-stat"><div class="compact-stat-value">${cacheRate}%</div><div class="compact-stat-label">Semantic Cache</div></div>`;
                    godHtml += `<div class="compact-stat"><div class="compact-stat-value">${(vector.hit_rate || 0).toFixed(1)}%</div><div class="compact-stat-label">Vector Memory</div></div>`;
                    godHtml += `<div class="compact-stat"><div class="compact-stat-value">${vector.recalls || 0}</div><div class="compact-stat-label">Recalls</div></div>`;
                    godHtml += `<div class="compact-stat"><div class="compact-stat-value">${mutations.detected || 0}</div><div class="compact-stat-label">Mutations</div></div>`;
                    godHtml += `<div class="compact-stat"><div class="compact-stat-value">${(mutations.handling_rate || 0).toFixed(1)}%</div><div class="compact-stat-label">Handled</div></div>`;
                    godHtml += '</div>';
                    document.getElementById('god-tier').innerHTML = godHtml;
                    
                    // Recent activity
                    if (validators.recent_activity && validators.recent_activity.length > 0) {
                        let html = '<table><tr><th>Time</th><th>IP</th><th>Status</th><th>Time</th></tr>';
                        validators.recent_activity.slice(-10).reverse().forEach(a => {
                            const status = a.success ? '<span class="badge badge-success">OK</span>' : '<span class="badge badge-error">FAIL</span>';
                            let timeStr = a.time;
                            if (!timeStr.endsWith('Z') && !timeStr.includes('+') && !timeStr.includes('-', 10)) {
                                timeStr = timeStr + 'Z';
                            }
                            const date = new Date(timeStr);
                            const timeFormatted = date.toLocaleString('en-US', { 
                                timeZone: 'America/Chicago',
                                hour: '2-digit',
                                minute: '2-digit',
                                second: '2-digit',
                                hour12: true
                            });
                            const respTime = a.response_time > 0 ? a.response_time.toFixed(3) + 's' : '<span style="color: #666;">-</span>';
                            html += `<tr><td>${timeFormatted}</td><td><code>${a.ip}</code></td><td>${status}</td><td>${respTime}</td></tr>`;
                        });
                        html += '</table>';
                        document.getElementById('recent-activity').innerHTML = html;
                    } else {
                        document.getElementById('recent-activity').innerHTML = '<div class="loading">Waiting for validator requests...</div>';
                    }
                    
                    // Task types
                    if (data.task_types && Object.keys(data.task_types).length > 0) {
                        let html = '<table><tr><th>Type</th><th>Rate</th><th>Total</th></tr>';
                        for (const [type, stats] of Object.entries(data.task_types)) {
                            const cls = stats.success_rate >= 80 ? 'status-good' : 'status-error';
                            html += `<tr><td><code>${type}</code></td><td class="${cls}">${stats.success_rate.toFixed(1)}%</td><td>${stats.total}</td></tr>`;
                        }
                        html += '</table>';
                        document.getElementById('task-types').innerHTML = html;
                    } else {
                        document.getElementById('task-types').innerHTML = '<div class="loading">No task types yet</div>';
                    }
                    
                    // Top validators
                    if (validators.top_validators && validators.top_validators.length > 0) {
                        let html = '<table><tr><th>Rank</th><th>IP</th><th>Requests</th></tr>';
                        validators.top_validators.forEach((v, idx) => {
                            html += `<tr><td>#${idx + 1}</td><td><code>${v.ip}</code></td><td>${v.requests}</td></tr>`;
                        });
                        html += '</table>';
                        document.getElementById('top-validators').innerHTML = html;
                    } else {
                        document.getElementById('top-validators').innerHTML = '<div class="loading">No validators yet</div>';
                    }
                    
                    // Errors
                    if (data.errors?.error_types && Object.keys(data.errors.error_types).length > 0) {
                        let html = '<table><tr><th>Type</th><th>Count</th></tr>';
                        for (const [type, count] of Object.entries(data.errors.error_types)) {
                            html += `<tr><td><code>${type}</code></td><td class="status-error">${count}</td></tr>`;
                        }
                        html += '</table>';
                        document.getElementById('errors').innerHTML = html;
                    } else {
                        document.getElementById('errors').innerHTML = '<div class="loading status-good">✓ No errors</div>';
                    }
                    
                } catch (error) {
                    console.error('Error:', error);
                    document.getElementById('recent-activity').innerHTML = 
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
    import subprocess
    import re
    from datetime import datetime
    
    advanced_metrics = get_advanced_metrics()
    metrics = advanced_metrics.get_comprehensive_metrics()
    metrics["health_score"] = advanced_metrics.get_health_score()
    
    # Store current metrics before rebuilding from logs
    current_response_times = list(advanced_metrics.response_times) if hasattr(advanced_metrics, 'response_times') else []
    
    # Rebuild metrics from logs (validator-only), but preserve response time data
    try:
        result = subprocess.run(
            ["journalctl", "-u", "autoppia-api", "--since", "24 hours ago", "--no-pager"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            log_lines = result.stdout.split('\n')
            historical_activity = []
            
            for line in log_lines:
                match = re.search(r'(\w+\s+\d+\s+\d+:\d+:\d+).*?INFO:.*?([\d.]+):\d+\s+-\s+"POST\s+/solve_task.*?"\s+(\d+)', line)
                if match:
                    timestamp_str, ip, status_code = match.groups()
                    if ip in ["127.0.0.1", "localhost", "::1"]:
                        continue
                    try:
                        current_year = datetime.now().year
                        dt = datetime.strptime(f"{timestamp_str} {current_year}", "%b %d %H:%M:%S %Y")
                        historical_activity.append({
                            "time": dt.isoformat(),
                            "ip": ip,
                            "success": status_code == "200",
                            "response_time": 0.0,
                            "source": "validator"
                        })
                    except Exception:
                        pass
            
            validator_activity = [
                a for a in historical_activity 
                if a.get("ip") not in ["127.0.0.1", "localhost", "::1"] 
                and not a.get("ip", "").startswith("192.168.")
                and not a.get("ip", "").startswith("10.")
                and not a.get("ip", "").startswith("172.16.")
                and a.get("ip") != "134.199.203.133"
            ]
            
            if validator_activity:
                metrics["overview"]["total_requests"] = len(validator_activity)
                metrics["overview"]["successful_requests"] = sum(1 for a in validator_activity if a["success"])
                metrics["overview"]["failed_requests"] = sum(1 for a in validator_activity if not a["success"])
                
                if metrics["overview"]["total_requests"] > 0:
                    metrics["overview"]["success_rate"] = round(
                        (metrics["overview"]["successful_requests"] / metrics["overview"]["total_requests"]) * 100, 2
                    )
                
                if current_response_times and len(current_response_times) > 0:
                    metrics["performance"]["avg_response_time"] = round(sum(current_response_times) / len(current_response_times), 3)
                    sorted_times = sorted(current_response_times)
                    if len(sorted_times) >= 20:
                        metrics["performance"]["p95_response_time"] = round(sorted_times[int(len(sorted_times) * 0.95)], 3)
                        metrics["performance"]["p99_response_time"] = round(sorted_times[int(len(sorted_times) * 0.99)], 3)
                
                uptime_hours = metrics["overview"].get("uptime_hours", 0.02)
                if uptime_hours > 0:
                    metrics["performance"]["requests_per_minute"] = round(
                        metrics["overview"]["total_requests"] / (uptime_hours * 60), 2
                    )
                
                if metrics["overview"]["total_requests"] > 0:
                    success_rate = metrics["overview"]["success_rate"]
                    response_time_score = max(0, 100 - (metrics["performance"]["avg_response_time"] * 10))
                    uptime_score = min(100, uptime_hours * 10)
                    metrics["health_score"] = round(
                        success_rate * 0.5 + response_time_score * 0.3 + uptime_score * 0.2, 2
                    )
                
                validator_activity.sort(key=lambda x: x.get("time", ""), reverse=True)
                metrics["validators"]["recent_activity"] = validator_activity[:20]
                metrics["validators"]["unique_validators"] = len(set(a["ip"] for a in validator_activity))
                
                from collections import Counter
                ip_counts = Counter(a["ip"] for a in validator_activity)
                metrics["validators"]["top_validators"] = [
                    {"ip": ip, "requests": count} 
                    for ip, count in ip_counts.most_common(5)
                ]
            else:
                metrics["overview"]["total_requests"] = 0
                metrics["overview"]["successful_requests"] = 0
                metrics["overview"]["failed_requests"] = 0
                metrics["overview"]["success_rate"] = 0
                metrics["validators"]["recent_activity"] = []
                metrics["validators"]["unique_validators"] = 0
                metrics["validators"]["top_validators"] = []
                metrics["health_score"] = 0.0
    except Exception:
        pass
    
    return JSONResponse(content=metrics)
