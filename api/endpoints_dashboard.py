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
                background: linear-gradient(135deg, #f5f7fa 0%, #e8ecf1 100%);
                padding: 12px;
                color: #2c3e50;
                font-size: 11px;
                line-height: 1.4;
            }
            .header { 
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 12px;
                padding: 12px 16px;
                background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
                border-radius: 12px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.08);
                border: 1px solid rgba(0,0,0,0.05);
                transition: transform 0.2s ease, box-shadow 0.2s ease;
            }
            .header:hover {
                transform: translateY(-1px);
                box-shadow: 0 4px 12px rgba(0,0,0,0.12);
            }
            .header h1 { 
                font-size: 18px; 
                font-weight: 700; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }
            .header-info { 
                font-size: 11px; 
                color: #6c757d;
                display: flex;
                align-items: center;
            }
            .refresh-indicator {
                display: inline-block;
                width: 10px;
                height: 10px;
                border-radius: 50%;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                margin-right: 8px;
                animation: pulse 2s infinite, rotate 3s linear infinite;
                box-shadow: 0 0 8px rgba(102, 126, 234, 0.4);
            }
            @keyframes pulse {
                0%, 100% { opacity: 1; transform: scale(1); }
                50% { opacity: 0.6; transform: scale(1.1); }
            }
            @keyframes rotate {
                from { transform: rotate(0deg); }
                to { transform: rotate(360deg); }
            }
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(10px); }
                to { opacity: 1; transform: translateY(0); }
            }
            .grid { 
                display: grid; 
                grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); 
                gap: 10px; 
                margin-bottom: 12px; 
            }
            .card { 
                background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
                padding: 12px; 
                border-radius: 12px; 
                border: 1px solid rgba(0,0,0,0.05);
                box-shadow: 0 2px 8px rgba(0,0,0,0.06);
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                animation: fadeIn 0.5s ease-out;
                position: relative;
                overflow: hidden;
            }
            .card::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 3px;
                background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
                transform: scaleX(0);
                transition: transform 0.3s ease;
            }
            .card:hover {
                transform: translateY(-4px);
                box-shadow: 0 8px 20px rgba(0,0,0,0.12);
            }
            .card:hover::before {
                transform: scaleX(1);
            }
            .card-title { 
                color: #6c757d; 
                font-size: 9px; 
                margin-bottom: 6px;
                text-transform: uppercase;
                letter-spacing: 0.8px;
                font-weight: 600;
            }
            .card-value { 
                font-size: 24px; 
                font-weight: 700; 
                color: #2c3e50;
                line-height: 1.2;
                transition: all 0.3s ease;
            }
            .card:hover .card-value {
                transform: scale(1.05);
            }
            .card-value.good { 
                background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }
            .card-value.warning { 
                background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }
            .card-value.error { 
                background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }
            .card-sub { 
                font-size: 10px; 
                color: #868e96; 
                margin-top: 4px;
                font-weight: 500;
            }
            .section { 
                background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
                padding: 12px; 
                border-radius: 12px; 
                margin-bottom: 10px; 
                border: 1px solid rgba(0,0,0,0.05);
                box-shadow: 0 2px 8px rgba(0,0,0,0.06);
                transition: all 0.3s ease;
                animation: fadeIn 0.6s ease-out;
            }
            .section:hover {
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            }
            .section-title { 
                font-size: 11px; 
                font-weight: 700; 
                margin-bottom: 10px; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                text-transform: uppercase;
                letter-spacing: 0.8px;
            }
            table { 
                width: 100%; 
                border-collapse: collapse; 
                font-size: 10px;
            }
            th, td { 
                padding: 8px 10px; 
                text-align: left; 
                border-bottom: 1px solid rgba(0,0,0,0.05); 
            }
            th { 
                color: #6c757d;
                font-weight: 700;
                font-size: 9px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            td { 
                color: #495057; 
                font-weight: 500;
            }
            tr { 
                transition: all 0.2s ease;
            }
            tr:hover { 
                background: linear-gradient(90deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);
                transform: translateX(4px);
            }
            .status-good { 
                color: #28a745; 
                font-weight: 700; 
            }
            .status-error { 
                color: #dc3545; 
                font-weight: 700; 
            }
            .badge { 
                padding: 4px 10px; 
                border-radius: 20px; 
                font-size: 9px; 
                font-weight: 700; 
                display: inline-block;
                transition: all 0.2s ease;
            }
            .badge:hover {
                transform: scale(1.1);
            }
            .badge-success { 
                background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
                color: white;
                box-shadow: 0 2px 6px rgba(17, 153, 142, 0.3);
            }
            .badge-error { 
                background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
                color: white;
                box-shadow: 0 2px 6px rgba(250, 112, 154, 0.3);
            }
            .compact-row {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(90px, 1fr));
                gap: 8px;
                margin-top: 8px;
            }
            .compact-stat {
                text-align: center;
                padding: 10px 8px;
                background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
                border-radius: 10px;
                border: 1px solid rgba(0,0,0,0.05);
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                box-shadow: 0 2px 4px rgba(0,0,0,0.04);
            }
            .compact-stat:hover {
                transform: translateY(-3px) scale(1.02);
                box-shadow: 0 6px 12px rgba(0,0,0,0.1);
            }
            .compact-stat-value {
                font-size: 16px;
                font-weight: 700;
                color: #2c3e50;
                transition: all 0.3s ease;
            }
            .compact-stat:hover .compact-stat-value {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }
            .compact-stat-label {
                font-size: 9px;
                color: #868e96;
                margin-top: 4px;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            code { 
                background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
                padding: 3px 8px; 
                border-radius: 6px; 
                font-size: 9px; 
                font-family: 'Monaco', 'Courier New', monospace;
                color: #667eea;
                font-weight: 600;
                border: 1px solid rgba(102, 126, 234, 0.2);
                transition: all 0.2s ease;
            }
            code:hover {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                transform: scale(1.05);
            }
            .mini-chart {
                height: 40px;
                display: flex;
                align-items: flex-end;
                gap: 3px;
                margin-top: 8px;
                padding: 4px;
                background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
                border-radius: 8px;
            }
            .mini-bar {
                flex: 1;
                background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
                border-radius: 4px 4px 0 0;
                min-height: 4px;
                transition: all 0.3s ease;
                animation: growUp 0.6s ease-out;
            }
            @keyframes growUp {
                from { height: 0; }
            }
            .mini-bar:hover {
                opacity: 0.8;
                transform: scaleY(1.1);
            }
            .loading { 
                text-align: center; 
                padding: 20px; 
                color: #868e96; 
                font-size: 11px; 
                font-weight: 500;
            }
            .two-col {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 10px;
            }
            @media (max-width: 768px) {
                .two-col {
                    grid-template-columns: 1fr;
                }
            }
            .chart-container {
                position: relative;
                height: 300px;
                margin-top: 10px;
                background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
                border-radius: 12px;
                padding: 16px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.06);
            }
            .chart-wrapper {
                position: relative;
                height: 100%;
            }
        </style>
        <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/chartjs-adapter-date-fns@3.0.0/dist/chartjs-adapter-date-fns.bundle.min.js"></script>
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
        
        <div class="two-col">
            <div class="section">
                <div class="section-title">🛡️ Dynamic Zero (Anti-Overfitting)</div>
                <div id="anti-overfitting" class="loading">Loading...</div>
            </div>
            <div class="section">
                <div class="section-title">📊 Task Diversity</div>
                <div id="task-diversity" class="loading">Loading...</div>
            </div>
        </div>
        
        <div class="section">
            <div class="section-title">📈 Real-Time Performance Trends</div>
            <div class="chart-container">
                <div class="chart-wrapper">
                    <canvas id="performanceChart"></canvas>
                </div>
            </div>
        </div>
        
        <script>
            // Initialize complex performance chart
            let performanceChart = null;
            const chartData = {
                labels: [],
                datasets: [
                    {
                        label: 'Success Rate (%)',
                        data: [],
                        borderColor: 'rgb(17, 153, 142)',
                        backgroundColor: 'rgba(17, 153, 142, 0.1)',
                        borderWidth: 3,
                        fill: true,
                        tension: 0.4,
                        pointRadius: 4,
                        pointHoverRadius: 6,
                        pointBackgroundColor: 'rgb(17, 153, 142)',
                        pointBorderColor: '#fff',
                        pointBorderWidth: 2,
                        yAxisID: 'y',
                    },
                    {
                        label: 'Response Time (ms)',
                        data: [],
                        borderColor: 'rgb(102, 126, 234)',
                        backgroundColor: 'rgba(102, 126, 234, 0.1)',
                        borderWidth: 3,
                        fill: true,
                        tension: 0.4,
                        pointRadius: 4,
                        pointHoverRadius: 6,
                        pointBackgroundColor: 'rgb(102, 126, 234)',
                        pointBorderColor: '#fff',
                        pointBorderWidth: 2,
                        yAxisID: 'y1',
                    },
                    {
                        label: 'Requests/min',
                        data: [],
                        borderColor: 'rgb(250, 112, 154)',
                        backgroundColor: 'rgba(250, 112, 154, 0.1)',
                        borderWidth: 3,
                        fill: true,
                        tension: 0.4,
                        pointRadius: 4,
                        pointHoverRadius: 6,
                        pointBackgroundColor: 'rgb(250, 112, 154)',
                        pointBorderColor: '#fff',
                        pointBorderWidth: 2,
                        yAxisID: 'y2',
                    },
                    {
                        label: 'Cache Hit Rate (%)',
                        data: [],
                        borderColor: 'rgb(118, 75, 162)',
                        backgroundColor: 'rgba(118, 75, 162, 0.1)',
                        borderWidth: 3,
                        fill: true,
                        tension: 0.4,
                        pointRadius: 4,
                        pointHoverRadius: 6,
                        pointBackgroundColor: 'rgb(118, 75, 162)',
                        pointBorderColor: '#fff',
                        pointBorderWidth: 2,
                        yAxisID: 'y',
                    }
                ]
            };
            
            function initChart() {
                const ctx = document.getElementById('performanceChart').getContext('2d');
                performanceChart = new Chart(ctx, {
                    type: 'line',
                    data: chartData,
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        interaction: {
                            mode: 'index',
                            intersect: false,
                        },
                        plugins: {
                            legend: {
                                display: true,
                                position: 'top',
                                labels: {
                                    usePointStyle: true,
                                    padding: 15,
                                    font: {
                                        size: 11,
                                        weight: '600'
                                    },
                                    color: '#495057'
                                }
                            },
                            tooltip: {
                                backgroundColor: 'rgba(0, 0, 0, 0.8)',
                                padding: 12,
                                titleFont: {
                                    size: 12,
                                    weight: 'bold'
                                },
                                bodyFont: {
                                    size: 11
                                },
                                borderColor: 'rgba(255, 255, 255, 0.1)',
                                borderWidth: 1,
                                cornerRadius: 8,
                                displayColors: true,
                                callbacks: {
                                    label: function(context) {
                                        let label = context.dataset.label || '';
                                        if (label) {
                                            label += ': ';
                                        }
                                        if (context.parsed.y !== null) {
                                            if (label.includes('Time')) {
                                                label += context.parsed.y.toFixed(2) + 'ms';
                                            } else if (label.includes('Rate') || label.includes('Hit')) {
                                                label += context.parsed.y.toFixed(1) + '%';
                                            } else {
                                                label += context.parsed.y.toFixed(2);
                                            }
                                        }
                                        return label;
                                    }
                                }
                            },
                            animation: {
                                duration: 1000,
                                easing: 'easeInOutQuart'
                            }
                        },
                        scales: {
                            x: {
                                grid: {
                                    display: true,
                                    color: 'rgba(0, 0, 0, 0.05)',
                                    drawBorder: false
                                },
                                ticks: {
                                    font: {
                                        size: 10
                                    },
                                    color: '#6c757d',
                                    maxRotation: 45,
                                    minRotation: 0
                                }
                            },
                            y: {
                                type: 'linear',
                                display: true,
                                position: 'left',
                                title: {
                                    display: true,
                                    text: 'Success Rate / Cache Hit (%)',
                                    font: {
                                        size: 11,
                                        weight: '600'
                                    },
                                    color: '#495057'
                                },
                                grid: {
                                    display: true,
                                    color: 'rgba(0, 0, 0, 0.05)',
                                    drawBorder: false
                                },
                                ticks: {
                                    font: {
                                        size: 10
                                    },
                                    color: '#6c757d',
                                    callback: function(value) {
                                        return value.toFixed(0) + '%';
                                    }
                                },
                                min: 0,
                                max: 100
                            },
                            y1: {
                                type: 'linear',
                                display: true,
                                position: 'right',
                                title: {
                                    display: true,
                                    text: 'Response Time (ms)',
                                    font: {
                                        size: 11,
                                        weight: '600'
                                    },
                                    color: '#495057'
                                },
                                grid: {
                                    drawOnChartArea: false,
                                    color: 'rgba(0, 0, 0, 0.05)'
                                },
                                ticks: {
                                    font: {
                                        size: 10
                                    },
                                    color: '#6c757d',
                                    callback: function(value) {
                                        return value.toFixed(0) + 'ms';
                                    }
                                }
                            },
                            y2: {
                                type: 'linear',
                                display: true,
                                position: 'right',
                                title: {
                                    display: true,
                                    text: 'Requests/min',
                                    font: {
                                        size: 11,
                                        weight: '600'
                                    },
                                    color: '#495057'
                                },
                                grid: {
                                    drawOnChartArea: false,
                                    color: 'rgba(0, 0, 0, 0.05)'
                                },
                                ticks: {
                                    font: {
                                        size: 10
                                    },
                                    color: '#6c757d',
                                    callback: function(value) {
                                        return value.toFixed(1);
                                    }
                                },
                                offset: true
                            }
                        }
                    }
                });
            }
            
            function updateChart(data) {
                if (!performanceChart) {
                    initChart();
                }
                
                const now = new Date();
                const timeLabel = now.toLocaleTimeString('en-US', { 
                    hour: '2-digit', 
                    minute: '2-digit', 
                    second: '2-digit',
                    hour12: false
                });
                
                const overview = data.overview || {};
                const perf = data.performance || {};
                const caching = data.caching || {};
                
                // Add new data point
                chartData.labels.push(timeLabel);
                chartData.datasets[0].data.push(parseFloat(overview.success_rate || 0));
                chartData.datasets[1].data.push((parseFloat(perf.avg_response_time || 0) * 1000)); // Convert to ms
                chartData.datasets[2].data.push(parseFloat(perf.requests_per_minute || 0));
                chartData.datasets[3].data.push(parseFloat(caching.cache_hit_rate || 0));
                
                // Keep only last 30 data points for performance
                const maxPoints = 30;
                if (chartData.labels.length > maxPoints) {
                    chartData.labels.shift();
                    chartData.datasets.forEach(dataset => {
                        dataset.data.shift();
                    });
                }
                
                // Update chart with animation
                performanceChart.update('active');
            }
            
            // Initialize chart on load
            window.addEventListener('load', initChart);
            
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
                    
                    // Update performance chart
                    updateChart(data);
                    
                    // DYNAMIC ZERO: Display anti-overfitting metrics
                    if (data.anti_overfitting) {
                        const ao = data.anti_overfitting;
                        let html = '<div class="compact-row">';
                        html += `<div class="compact-stat">
                            <div class="compact-stat-value ${ao.diversity_score >= 0.5 ? 'good' : 'warning'}">${(ao.diversity_score * 100).toFixed(1)}%</div>
                            <div class="compact-stat-label">Diversity</div>
                        </div>`;
                        html += `<div class="compact-stat">
                            <div class="compact-stat-value">${ao.overused_patterns}</div>
                            <div class="compact-stat-label">Overused</div>
                        </div>`;
                        html += `<div class="compact-stat">
                            <div class="compact-stat-value">${ao.total_patterns}</div>
                            <div class="compact-stat-label">Total Patterns</div>
                        </div>`;
                        html += `<div class="compact-stat">
                            <div class="compact-stat-value ${ao.is_overfitting ? 'error' : 'good'}">${ao.is_overfitting ? '⚠️' : '✓'}</div>
                            <div class="compact-stat-label">Status</div>
                        </div>`;
                        html += '</div>';
                        if (ao.is_overfitting) {
                            html += '<div style="margin-top: 8px; padding: 8px; background: #fff3cd; border-radius: 6px; font-size: 10px; color: #856404;">⚠️ Overfitting detected - forcing pattern adaptation</div>';
                        }
                        document.getElementById('anti-overfitting').innerHTML = html;
                    } else {
                        document.getElementById('anti-overfitting').innerHTML = '<div class="loading">No data yet</div>';
                    }
                    
                    // Task diversity metrics
                    if (data.task_diversity) {
                        const td = data.task_diversity;
                        let html = '<div class="compact-row">';
                        html += `<div class="compact-stat">
                            <div class="compact-stat-value">${td.unique_task_types || 0}</div>
                            <div class="compact-stat-label">Task Types</div>
                        </div>`;
                        html += `<div class="compact-stat">
                            <div class="compact-stat-value">${td.unique_websites || 0}</div>
                            <div class="compact-stat-label">Websites</div>
                        </div>`;
                        html += `<div class="compact-stat">
                            <div class="compact-stat-value">${td.recent_tasks_count || 0}</div>
                            <div class="compact-stat-label">Recent Tasks</div>
                        </div>`;
                        html += '</div>';
                        document.getElementById('task-diversity').innerHTML = html;
                    } else {
                        document.getElementById('task-diversity').innerHTML = '<div class="loading">No data yet</div>';
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
    
    # DYNAMIC ZERO: Add anti-overfitting metrics
    try:
        from api.utils.anti_overfitting import anti_overfitting
        from api.utils.task_diversity import task_diversity
        metrics["anti_overfitting"] = anti_overfitting.get_overfitting_metrics()
        metrics["task_diversity"] = task_diversity.get_diversity_metrics()
    except Exception:
        metrics["anti_overfitting"] = {}
        metrics["task_diversity"] = {}
    
    # Store current in-memory metrics (source of truth)
    current_total_requests = metrics["overview"]["total_requests"]
    current_successful = metrics["overview"]["successful_requests"]
    current_failed = metrics["overview"]["failed_requests"]
    current_response_times = list(advanced_metrics.response_times) if hasattr(advanced_metrics, 'response_times') else []
    
    # Supplement with historical log data (for recent activity display), but don't replace in-memory counts
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
            
            # Use in-memory metrics as source of truth (they accumulate correctly)
            # Only use log data for recent activity display and validator tracking
            # Take the maximum to ensure count never decreases
            log_count = len(validator_activity)
            metrics["overview"]["total_requests"] = max(current_total_requests, log_count)
            metrics["overview"]["successful_requests"] = max(
                current_successful, 
                sum(1 for a in validator_activity if a["success"])
            )
            metrics["overview"]["failed_requests"] = max(
                current_failed,
                sum(1 for a in validator_activity if not a["success"])
            )
                
                # Recalculate success rate based on updated counts
                if metrics["overview"]["total_requests"] > 0:
                    metrics["overview"]["success_rate"] = round(
                        (metrics["overview"]["successful_requests"] / metrics["overview"]["total_requests"]) * 100, 2
                    )
                else:
                    # Fallback to in-memory metrics if no log data
                    metrics["overview"]["total_requests"] = current_total_requests
                    metrics["overview"]["successful_requests"] = current_successful
                    metrics["overview"]["failed_requests"] = current_failed
                    if current_total_requests > 0:
                        metrics["overview"]["success_rate"] = round(
                            (current_successful / current_total_requests) * 100, 2
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
    
    # Ensure proper JSON serialization
    import json
    try:
        # Validate that metrics can be serialized to JSON
        json.dumps(metrics)
        return JSONResponse(content=metrics)
    except (TypeError, ValueError) as e:
        # If serialization fails, return error
        return JSONResponse(
            content={"error": f"Metrics serialization error: {str(e)}"},
            status_code=500
        )
