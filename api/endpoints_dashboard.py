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
                <div class="metric-label">Total Requests</div>
                <div class="metric-value" id="total-requests">-</div>
            </div>
            <div class="metric">
                <div class="metric-label">Unique Validators</div>
                <div class="metric-value" id="unique-validators">-</div>
            </div>
            <div class="metric">
                <div class="metric-label">Health Score</div>
                <div class="metric-value" id="health-score">-</div>
            </div>
        </div>
        
        <div class="section">
            <div class="section-title">Request Breakdown</div>
            <div id="request-breakdown" class="loading">Loading...</div>
        </div>
        
        <div class="section">
            <div class="section-title">Top Validators</div>
            <div id="top-validators" class="loading">Loading...</div>
        </div>
        
        <div class="section">
            <div class="section-title">Recent Activity (Last 10)</div>
            <div id="validator-activity" class="loading">Loading...</div>
        </div>
        
        <div class="section">
            <div class="section-title">Task Types</div>
            <div id="task-types" class="loading">Loading...</div>
        </div>
        
        <div class="section">
            <div class="section-title">Agent Performance</div>
            <div id="agent-performance" class="loading">Loading...</div>
        </div>
        
        <div class="section">
            <div class="section-title">Performance Metrics</div>
            <div id="performance-stats" class="loading">Loading...</div>
        </div>
        
        <div class="section">
            <div class="section-title">System Info</div>
            <div id="system-info" class="loading">Loading...</div>
        </div>
        
        <div class="section">
            <div class="section-title">Errors</div>
            <div id="error-summary" class="loading">Loading...</div>
        </div>
        
        <script>
            async function loadMetrics() {
                try {
                    console.log('Fetching metrics...');
                    const response = await fetch('/api/dashboard/metrics');
                    if (!response.ok) {
                        throw new Error('Failed to fetch metrics: ' + response.status);
                    }
                    const data = await response.json();
                    console.log('Metrics data:', data);
                    
                    // Update timestamp (Central Time)
                    const now = new Date();
                    document.getElementById('last-update').textContent = now.toLocaleString('en-US', { 
                        timeZone: 'America/Chicago',
                        hour: '2-digit',
                        minute: '2-digit',
                        second: '2-digit',
                        hour12: true
                    }) + ' CT';
                    
                    // Update main metrics - handle null/undefined properly
                    const overview = data.overview || {};
                    const performance = data.performance || {};
                    
                    // Update main metrics - always show values, even if 0
                    const totalRequests = parseInt(overview.total_requests || 0);
                    document.getElementById('total-requests').textContent = totalRequests.toLocaleString();
                    
                    const successRate = totalRequests > 0 ? parseFloat(overview.success_rate || 0).toFixed(1) : '0.0';
                    const successRateEl = document.getElementById('success-rate');
                    successRateEl.textContent = successRate + '%';
                    if (totalRequests > 0) {
                        successRateEl.className = 'metric-value ' + 
                            (parseFloat(successRate) >= 90 ? 'good' : parseFloat(successRate) >= 70 ? 'warning' : 'error');
                    } else {
                        successRateEl.className = 'metric-value';
                    }
                    
                    // Unique validators
                    const uniqueValidators = parseInt(data.validators?.unique_validators || 0);
                    document.getElementById('unique-validators').textContent = uniqueValidators;
                    
                    const healthScore = parseFloat(data.health_score || 0).toFixed(1);
                    const healthScoreEl = document.getElementById('health-score');
                    healthScoreEl.textContent = healthScore;
                    if (totalRequests > 0) {
                        healthScoreEl.className = 'metric-value ' + 
                            (parseFloat(healthScore) >= 90 ? 'good' : parseFloat(healthScore) >= 70 ? 'warning' : 'error');
                    } else {
                        healthScoreEl.className = 'metric-value';
                    }
                    
                    // Request breakdown
                    const successful = parseInt(overview.successful_requests || 0);
                    const failed = parseInt(overview.failed_requests || 0);
                    let breakdownHtml = '<div class="compact-row">';
                    breakdownHtml += `<div class="compact-stat">
                        <div class="compact-stat-value status-good">${successful}</div>
                        <div class="compact-stat-label">Successful</div>
                    </div>`;
                    breakdownHtml += `<div class="compact-stat">
                        <div class="compact-stat-value status-error">${failed}</div>
                        <div class="compact-stat-label">Failed</div>
                    </div>`;
                    breakdownHtml += `<div class="compact-stat">
                        <div class="compact-stat-value">${(performance.avg_response_time || 0).toFixed(3)}s</div>
                        <div class="compact-stat-label">Avg Response</div>
                    </div>`;
                    breakdownHtml += `<div class="compact-stat">
                        <div class="compact-stat-value">${(overview.uptime_hours || 0).toFixed(1)}h</div>
                        <div class="compact-stat-label">Uptime</div>
                    </div>`;
                    breakdownHtml += '</div>';
                    document.getElementById('request-breakdown').innerHTML = breakdownHtml;
                    
                    // Top validators
                    if (data.validators?.top_validators && data.validators.top_validators.length > 0) {
                        let html = '<table><tr><th>Rank</th><th>Validator IP</th><th>Requests</th></tr>';
                        data.validators.top_validators.forEach((v, idx) => {
                            html += `<tr>
                                <td>#${idx + 1}</td>
                                <td><code>${v.ip}</code></td>
                                <td>${v.requests}</td>
                            </tr>`;
                        });
                        html += '</table>';
                        document.getElementById('top-validators').innerHTML = html;
                    } else {
                        document.getElementById('top-validators').innerHTML = '<div class="loading">No validator data yet</div>';
                    }
                    
                    // Task types
                    if (data.task_types && Object.keys(data.task_types).length > 0) {
                        let html = '<table><tr><th>Task Type</th><th>Success Rate</th><th>Total</th><th>Successful</th></tr>';
                        for (const [type, stats] of Object.entries(data.task_types)) {
                            const cls = stats.success_rate >= 80 ? 'status-good' : 'status-error';
                            html += `<tr>
                                <td><code>${type}</code></td>
                                <td class="${cls}">${stats.success_rate.toFixed(1)}%</td>
                                <td>${stats.total}</td>
                                <td>${stats.success}</td>
                            </tr>`;
                        }
                        html += '</table>';
                        document.getElementById('task-types').innerHTML = html;
                    } else {
                        document.getElementById('task-types').innerHTML = '<div class="loading">No task type breakdown available yet. Task types will appear as validators send different task types.</div>';
                    }
                    
                    // Agent performance
                    if (data.agents && Object.keys(data.agents).length > 0) {
                        let html = '<table><tr><th>Agent</th><th>Success</th><th>Total</th><th>Time</th></tr>';
                        for (const [agent, stats] of Object.entries(data.agents)) {
                            if (stats.total > 0) {
                                const cls = stats.success_rate >= 80 ? 'status-good' : 'status-error';
                                html += `<tr>
                                    <td>${agent}</td>
                                    <td class="${cls}">${stats.success_rate.toFixed(1)}%</td>
                                    <td>${stats.total}</td>
                                    <td>${stats.avg_response_time.toFixed(3)}s</td>
                                </tr>`;
                            }
                        }
                        html += '</table>';
                        document.getElementById('agent-performance').innerHTML = html || '<div class="loading">Waiting for requests...</div>';
                    } else {
                        document.getElementById('agent-performance').innerHTML = '<div class="loading">Using Hybrid Agent (Enhanced Template). Performance metrics will appear as requests are processed.</div>';
                    }
                    
                    // Validator activity (only shows external validators, not localhost) - show last 10
                    if (data.validators?.recent_activity?.length > 0) {
                        let html = '<table><tr><th>Time (Central)</th><th>Validator IP</th><th>Status</th><th>Response Time</th></tr>';
                        data.validators.recent_activity.slice(-10).reverse().forEach(a => {
                            const status = a.success 
                                ? '<span class="badge badge-success">OK</span>' 
                                : '<span class="badge badge-error">FAIL</span>';
                            // Show response time if available, otherwise show "Recorded" to indicate it was logged
                            const responseTime = a.response_time > 0 ? a.response_time.toFixed(3) + 's' : '<span style="color: #999;">Recorded</span>';
                            // Convert to Central Time (America/Chicago)
                            // Ensure the timestamp is treated as UTC by appending 'Z' if not present
                            let timeStr = a.time;
                            if (!timeStr.endsWith('Z') && !timeStr.includes('+') && !timeStr.includes('-', 10)) {
                                timeStr = timeStr + 'Z'; // Treat as UTC
                            }
                            const date = new Date(timeStr);
                            const timeStrFormatted = date.toLocaleString('en-US', { 
                                timeZone: 'America/Chicago',
                                year: 'numeric',
                                month: '2-digit',
                                day: '2-digit',
                                hour: '2-digit',
                                minute: '2-digit',
                                second: '2-digit',
                                hour12: true
                            });
                            html += `<tr>
                                <td>${timeStrFormatted}</td>
                                <td><code>${a.ip}</code></td>
                                <td>${status}</td>
                                <td>${responseTime}</td>
                            </tr>`;
                        });
                        html += '</table>';
                        document.getElementById('validator-activity').innerHTML = html;
                    } else {
                        document.getElementById('validator-activity').innerHTML = '<div class="loading">Waiting for validator requests...</div>';
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
                        document.getElementById('error-summary').innerHTML = '<div class="loading status-good">✓ No errors</div>';
                    }
                    
                    // Performance stats
                    const perf = data.performance || {};
                    let perfHtml = '<div class="compact-row">';
                    const avgTime = perf.avg_response_time || 0;
                    perfHtml += `<div class="compact-stat">
                        <div class="compact-stat-value">${avgTime > 0 ? avgTime.toFixed(3) + 's' : 'N/A'}</div>
                        <div class="compact-stat-label">Avg Response</div>
                    </div>`;
                    const p95 = perf.p95_response_time || 0;
                    perfHtml += `<div class="compact-stat">
                        <div class="compact-stat-value">${p95 > 0 ? p95.toFixed(3) + 's' : 'N/A'}</div>
                        <div class="compact-stat-label">P95</div>
                    </div>`;
                    const p99 = perf.p99_response_time || 0;
                    perfHtml += `<div class="compact-stat">
                        <div class="compact-stat-value">${p99 > 0 ? p99.toFixed(3) + 's' : 'N/A'}</div>
                        <div class="compact-stat-label">P99</div>
                    </div>`;
                    const rpm = perf.requests_per_minute || 0;
                    perfHtml += `<div class="compact-stat">
                        <div class="compact-stat-value">${rpm > 0 ? rpm.toFixed(1) : '0.0'}</div>
                        <div class="compact-stat-label">Req/min</div>
                    </div>`;
                    perfHtml += `<div class="compact-stat">
                        <div class="compact-stat-value">${(data.caching?.cache_hit_rate || 0).toFixed(1)}%</div>
                        <div class="compact-stat-label">Cache Hit</div>
                    </div>`;
                    perfHtml += '</div>';
                    if (avgTime === 0 && totalRequests > 0) {
                        perfHtml += '<div style="margin-top: 10px; padding: 10px; background: #fff3cd; border-radius: 4px; font-size: 12px; color: #856404;">Note: Response times are calculated from in-memory metrics. Historical log data does not include response times.</div>';
                    }
                    document.getElementById('performance-stats').innerHTML = perfHtml;
                    
                    // System info
                    let systemHtml = '<table><tr><th>Metric</th><th>Value</th></tr>';
                    systemHtml += `<tr><td>Miner UID</td><td><code>160</code></td></tr>`;
                    systemHtml += `<tr><td>Server IP</td><td><code>134.199.203.133</code></td></tr>`;
                    systemHtml += `<tr><td>API Port</td><td><code>8080</code></td></tr>`;
                    systemHtml += `<tr><td>Axon Port</td><td><code>8091</code></td></tr>`;
                    systemHtml += `<tr><td>Uptime</td><td>${(overview.uptime_hours || 0).toFixed(2)} hours</td></tr>`;
                    systemHtml += `<tr><td>Total Requests</td><td>${totalRequests}</td></tr>`;
                    systemHtml += `<tr><td>Successful</td><td class="status-good">${successful}</td></tr>`;
                    systemHtml += `<tr><td>Failed</td><td class="status-error">${failed}</td></tr>`;
                    systemHtml += `<tr><td>Unique Validators</td><td>${uniqueValidators}</td></tr>`;
                    systemHtml += `<tr><td>Success Rate</td><td>${successRate}%</td></tr>`;
                    systemHtml += `<tr><td>Health Score</td><td>${healthScore}</td></tr>`;
                    // Last update in Central Time
                    let timestamp = data.timestamp || new Date().toISOString();
                    // Ensure timestamp is treated as UTC
                    if (typeof timestamp === 'string' && !timestamp.endsWith('Z') && !timestamp.includes('+') && !timestamp.includes('-', 10)) {
                        timestamp = timestamp + 'Z';
                    }
                    const lastUpdate = new Date(timestamp);
                    const lastUpdateStr = lastUpdate.toLocaleString('en-US', { 
                        timeZone: 'America/Chicago',
                        year: 'numeric',
                        month: '2-digit',
                        day: '2-digit',
                        hour: '2-digit',
                        minute: '2-digit',
                        second: '2-digit',
                        hour12: true
                    });
                    systemHtml += `<tr><td>Last Update</td><td>${lastUpdateStr} CT</td></tr>`;
                    systemHtml += '</table>';
                    document.getElementById('system-info').innerHTML = systemHtml;
                    
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
    import subprocess
    import re
    from datetime import datetime
    
    advanced_metrics = get_advanced_metrics()
    # Get current metrics first (may have response times)
    metrics = advanced_metrics.get_comprehensive_metrics()
    metrics["health_score"] = advanced_metrics.get_health_score()
    
    # Store current metrics before rebuilding from logs
    current_total = metrics["overview"]["total_requests"]
    current_successful = metrics["overview"]["successful_requests"]
    current_failed = metrics["overview"]["failed_requests"]
    current_avg_time = metrics["performance"]["avg_response_time"]
    current_response_times = list(advanced_metrics.response_times) if hasattr(advanced_metrics, 'response_times') else []
    
    # Rebuild metrics from logs (validator-only), but preserve response time data
    try:
        # Get successful requests from logs (last 24 hours)
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
                # Match: "Nov 18 09:06:44 ... INFO: 45.22.240.79:54712 - "POST /solve_task HTTP/1.1" 200 OK"
                # Also match: "Nov 18 17:35:00 autoppia-miner python3[136214]: INFO:     84.247.180.192:48980 - "POST /solve_task HTTP/1.1" 200 OK"
                match = re.search(r'(\w+\s+\d+\s+\d+:\d+:\d+).*?INFO:.*?([\d.]+):\d+\s+-\s+"POST\s+/solve_task.*?"\s+(\d+)', line)
                if match:
                    timestamp_str, ip, status_code = match.groups()
                    # Skip localhost (127.0.0.1) - these are local tests
                    if ip in ["127.0.0.1", "localhost", "::1"]:
                        continue
                    # Parse timestamp (format: "Nov 18 09:06:44")
                    try:
                        # Convert to ISO format
                        current_year = datetime.now().year
                        dt = datetime.strptime(f"{timestamp_str} {current_year}", "%b %d %H:%M:%S %Y")
                        historical_activity.append({
                            "time": dt.isoformat(),
                            "ip": ip,
                            "success": status_code == "200",
                            "response_time": 0.0,  # Not available from logs
                            "source": "validator"  # Mark as validator (not localhost)
                        })
                    except Exception as e:
                        # Skip lines that can't be parsed
                        pass
            
            # Add historical activity to metrics if we found any
            if historical_activity:
                # Filter to ONLY validators (exclude ALL localhost/local IPs)
                validator_activity = [
                    a for a in historical_activity 
                    if a.get("ip") not in ["127.0.0.1", "localhost", "::1"] 
                    and not a.get("ip", "").startswith("192.168.")
                    and not a.get("ip", "").startswith("10.")
                    and not a.get("ip", "").startswith("172.16.")
                    and a.get("ip") != "134.199.203.133"  # Exclude our own server IP
                ]
                
                # Only use validator activity (don't merge with current metrics that might include local tests)
                # Replace metrics with ONLY validator data, but preserve response time calculations
                if validator_activity:
                    metrics["overview"]["total_requests"] = len(validator_activity)
                    metrics["overview"]["successful_requests"] = sum(1 for a in validator_activity if a["success"])
                    metrics["overview"]["failed_requests"] = sum(1 for a in validator_activity if not a["success"])
                    
                    if metrics["overview"]["total_requests"] > 0:
                        metrics["overview"]["success_rate"] = round(
                            (metrics["overview"]["successful_requests"] / metrics["overview"]["total_requests"]) * 100, 2
                        )
                    
                    # Calculate response times from current metrics if available
                    # Use current response times if we have them (from in-memory metrics)
                    if current_response_times and len(current_response_times) > 0:
                        metrics["performance"]["avg_response_time"] = round(sum(current_response_times) / len(current_response_times), 3)
                        sorted_times = sorted(current_response_times)
                        if len(sorted_times) >= 20:
                            metrics["performance"]["p95_response_time"] = round(sorted_times[int(len(sorted_times) * 0.95)], 3)
                            metrics["performance"]["p99_response_time"] = round(sorted_times[int(len(sorted_times) * 0.99)], 3)
                    
                    # Calculate requests per minute from uptime
                    uptime_hours = metrics["overview"].get("uptime_hours", 0.02)
                    if uptime_hours > 0:
                        metrics["performance"]["requests_per_minute"] = round(
                            metrics["overview"]["total_requests"] / (uptime_hours * 60), 2
                        )
                    
                    # Recalculate health score with validator-only data
                    if metrics["overview"]["total_requests"] > 0:
                        success_rate = metrics["overview"]["success_rate"]
                        response_time_score = max(0, 100 - (metrics["performance"]["avg_response_time"] * 10))
                        uptime_score = min(100, uptime_hours * 10)
                        metrics["health_score"] = round(
                            success_rate * 0.5 + response_time_score * 0.3 + uptime_score * 0.2, 2
                        )
                    
                    # Use ONLY validator activity (no merging with potentially contaminated current metrics)
                    # Sort by time (most recent first) and take most recent 20
                    validator_activity.sort(key=lambda x: x.get("time", ""), reverse=True)
                    metrics["validators"]["recent_activity"] = validator_activity[:20]
                    metrics["validators"]["unique_validators"] = len(set(a["ip"] for a in validator_activity))
                    
                    # Update top validators from validator activity only
                    from collections import Counter
                    ip_counts = Counter(a["ip"] for a in validator_activity)
                    metrics["validators"]["top_validators"] = [
                        {"ip": ip, "requests": count} 
                        for ip, count in ip_counts.most_common(5)
                    ]
                else:
                    # No validator activity found, reset to zeros but keep structure
                    metrics["overview"]["total_requests"] = 0
                    metrics["overview"]["successful_requests"] = 0
                    metrics["overview"]["failed_requests"] = 0
                    metrics["overview"]["success_rate"] = 0
                    metrics["validators"]["recent_activity"] = []
                    metrics["validators"]["unique_validators"] = 0
                    metrics["validators"]["top_validators"] = []
                    metrics["health_score"] = 0.0
    except Exception as e:
        # If log parsing fails, just use current metrics
        pass
    
    return JSONResponse(content=metrics)

