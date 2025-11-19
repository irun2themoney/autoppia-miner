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
                font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'SF Pro Text', sans-serif;
                background: #f5f5f7;
                padding: 20px;
                color: #1d1d1f;
                font-size: 14px;
                line-height: 1.5;
                min-height: 100vh;
            }
            .header { 
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 24px;
                padding: 16px 0;
                background: transparent;
            }
            .header h1 { 
                font-size: 32px; 
                font-weight: 600; 
                color: #1d1d1f;
                letter-spacing: -0.5px;
            }
            .header-info { 
                font-size: 13px; 
                color: #86868b;
                display: flex;
                align-items: center;
                font-weight: 400;
            }
            .stale-warning {
                background: #fff3cd;
                border: 1px solid #ffc107;
                color: #856404;
                padding: 8px 12px;
                border-radius: 8px;
                margin-bottom: 16px;
                font-size: 13px;
                display: none;
            }
            .refresh-indicator {
                display: inline-block;
                width: 8px;
                height: 8px;
                border-radius: 50%;
                background: #34c759;
                margin-right: 8px;
                animation: pulse 2s infinite;
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
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
                gap: 12px; 
                margin-bottom: 24px; 
            }
            .card { 
                background: #ffffff;
                padding: 20px; 
                border-radius: 12px; 
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
                transition: all 0.2s ease;
            }
            .card:hover {
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
            }
            .card-title { 
                color: #86868b; 
                font-size: 13px; 
                margin-bottom: 8px;
                font-weight: 400;
            }
            .card-value { 
                font-size: 28px; 
                font-weight: 600; 
                color: #1d1d1f;
                line-height: 1.2;
                letter-spacing: -0.3px;
            }
            .card-value.good { 
                color: #34c759;
            }
            .card-value.warning { 
                color: #ff9500;
            }
            .card-value.error { 
                color: #ff3b30;
            }
            .card-sub { 
                font-size: 13px; 
                color: #86868b; 
                margin-top: 4px;
                font-weight: 400;
            }
            .section { 
                background: #ffffff;
                padding: 20px; 
                border-radius: 12px; 
                margin-bottom: 16px; 
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
                transition: all 0.2s ease;
            }
            .section:hover {
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
            }
            .section-title { 
                font-size: 17px; 
                font-weight: 600; 
                margin-bottom: 16px; 
                color: #1d1d1f;
                letter-spacing: -0.2px;
            }
            table { 
                width: 100%; 
                border-collapse: collapse; 
                font-size: 14px;
            }
            th, td { 
                padding: 12px 0; 
                text-align: left; 
                border-bottom: 1px solid #f5f5f7; 
            }
            th { 
                color: #86868b;
                font-weight: 400;
                font-size: 13px;
            }
            td { 
                color: #1d1d1f; 
                font-weight: 400;
            }
            tr:hover { 
                background: #fafafa;
            }
            .status-good { 
                color: #34c759; 
                font-weight: 400; 
            }
            .status-error { 
                color: #ff3b30; 
                font-weight: 400; 
            }
            .badge { 
                padding: 4px 10px; 
                border-radius: 6px; 
                font-size: 12px; 
                font-weight: 400; 
                display: inline-block;
            }
            .badge-success { 
                background: #34c759;
                color: white;
            }
            .badge-error { 
                background: #ff3b30;
                color: white;
            }
            .compact-row {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(90px, 1fr));
                gap: 6px;
                margin-top: 4px;
            }
            .compact-stat {
                text-align: center;
                padding: 12px;
                background: #fafafa;
                border-radius: 8px;
                transition: all 0.2s ease;
            }
            .compact-stat:hover {
                background: #f5f5f7;
            }
            .compact-stat-value {
                font-size: 20px;
                font-weight: 600;
                color: #1d1d1f;
                letter-spacing: -0.3px;
            }
            .compact-stat-label {
                font-size: 12px;
                color: #86868b;
                margin-top: 4px;
                font-weight: 400;
            }
            code { 
                background: #f5f5f7;
                padding: 2px 6px; 
                border-radius: 4px; 
                font-size: 12px; 
                font-family: 'SF Mono', 'Monaco', 'Courier New', monospace;
                color: #1d1d1f;
                font-weight: 400;
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
                color: #86868b; 
                font-size: 14px; 
                font-weight: 400;
            }
            .two-col {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 12px;
                margin-bottom: 16px;
            }
            @media (max-width: 768px) {
                .two-col {
                    grid-template-columns: 1fr;
                }
                .grid {
                    grid-template-columns: 1fr;
                }
            }
            .chart-container {
                position: relative;
                height: 300px;
                margin-top: 0;
                margin-bottom: 16px;
                background: #ffffff;
                border-radius: 12px;
                padding: 20px;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
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
        <div id="stale-data-warning" class="stale-warning"></div>
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
            <div class="card">
                <div class="card-title">💰 Wallet Balance</div>
                <div class="card-value" id="wallet-balance">-</div>
                <div class="card-sub" id="wallet-balance-detail">TAO</div>
            </div>
            <div class="card">
                <div class="card-title">📊 Total Stake</div>
                <div class="card-value" id="wallet-stake">-</div>
                <div class="card-sub" id="wallet-stake-detail">TAO (Your: <span id="your-stake">-</span> | Delegators: <span id="delegator-stake">-</span>)</div>
            </div>
            <div class="card">
                <div class="card-title">🏆 Rank</div>
                <div class="card-value" id="wallet-rank">-</div>
                <div class="card-sub" id="wallet-rank-detail">Incentive: <span id="wallet-incentive">-</span></div>
            </div>
            <div class="card">
                <div class="card-title">🔄 Current Round</div>
                <div class="card-value" id="current-round">-</div>
                <div class="card-sub" id="round-detail">Next round in: <span id="round-countdown">-</span></div>
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
                    
                    // Ensure all required sections exist with defaults
                    if (!data.overview) data.overview = {};
                    if (!data.performance) data.performance = {};
                    if (!data.caching) data.caching = {};
                    if (!data.validators) data.validators = {};
                    if (!data.wallet) data.wallet = {};
                    if (!data.round) data.round = {};
                    if (!data.vector_memory) data.vector_memory = {};
                    if (!data.mutations) data.mutations = {};
                    if (!data.task_types) data.task_types = {};
                    if (!data.errors) data.errors = {};
                    if (!data.anti_overfitting) data.anti_overfitting = {};
                    if (!data.task_diversity) data.task_diversity = {};
                    
                    // Check data freshness
                    const freshness = data.data_freshness || {};
                    if (freshness.is_stale) {
                        const staleMsg = document.getElementById('stale-data-warning');
                        if (staleMsg) {
                            staleMsg.style.display = 'block';
                            staleMsg.textContent = `⚠️ Data is ${freshness.hours_since_activity?.toFixed(1) || 'unknown'} hours old. Last activity: ${freshness.latest_activity || 'unknown'}`;
                        }
                    } else {
                        const staleMsg = document.getElementById('stale-data-warning');
                        if (staleMsg) {
                            staleMsg.style.display = 'none';
                        }
                    }
                    
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
                    
                    // Wallet info
                    const wallet = data.wallet || {};
                    const balance = parseFloat(wallet.balance_tao || 0);
                    const totalStake = parseFloat(wallet.stake_tao || 0);
                    const yourStake = parseFloat(wallet.your_stake_tao || wallet.stake_tao || 0);
                    const delegatorStake = parseFloat(wallet.delegator_stake_tao || 0);
                    const rank = parseFloat(wallet.rank || 0);
                    const incentive = parseFloat(wallet.incentive || 0);
                    const uid = wallet.uid;
                    
                    document.getElementById('wallet-balance').textContent = balance.toFixed(4);
                    document.getElementById('wallet-balance').className = 'card-value' + (balance > 0 ? ' good' : '');
                    document.getElementById('wallet-balance-detail').textContent = 'TAO | UID: ' + (uid !== null && uid !== undefined ? uid : 'N/A');
                    
                    document.getElementById('wallet-stake').textContent = totalStake.toFixed(2);
                    document.getElementById('wallet-stake').className = 'card-value' + (totalStake > 0 ? ' good' : '');
                    document.getElementById('your-stake').textContent = yourStake.toFixed(2);
                    document.getElementById('delegator-stake').textContent = delegatorStake.toFixed(2);
                    
                    document.getElementById('wallet-rank').textContent = rank.toFixed(6);
                    document.getElementById('wallet-rank').className = 'card-value' + (rank > 0 ? ' good' : '');
                    document.getElementById('wallet-incentive').textContent = incentive.toFixed(6);
                    
                    // Round info
                    const round = data.round || {};
                    const currentRound = parseInt(round.current_round || 0);
                    const secondsUntilNext = parseInt(round.seconds_until_next_round || 0);
                    const roundProgress = parseFloat(round.round_progress || 0);
                    
                    document.getElementById('current-round').textContent = currentRound > 0 ? currentRound : '-';
                    document.getElementById('current-round').className = 'card-value' + (currentRound > 0 ? ' good' : '');
                    
                    // Update countdown timer (will be updated every second)
                    if (window.roundCountdownSeconds === undefined || secondsUntilNext > 0) {
                        window.roundCountdownSeconds = secondsUntilNext;
                    }
                    
                    function formatCountdown(seconds) {
                        if (seconds <= 0) return 'Starting...';
                        const hours = Math.floor(seconds / 3600);
                        const minutes = Math.floor((seconds % 3600) / 60);
                        const secs = seconds % 60;
                        if (hours > 0) {
                            return hours + 'h ' + minutes + 'm ' + secs + 's';
                        } else if (minutes > 0) {
                            return minutes + 'm ' + secs + 's';
                        } else {
                            return secs + 's';
                        }
                    }
                    
                    document.getElementById('round-countdown').textContent = formatCountdown(window.roundCountdownSeconds);
                    document.getElementById('round-detail').innerHTML = 'Next round in: <span id="round-countdown">' + formatCountdown(window.roundCountdownSeconds) + '</span> | ' + roundProgress.toFixed(1) + '% complete';
                    
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
                        let html = '<table><tr><th>Time</th><th>IP</th><th>Status</th><th>Response Time</th></tr>';
                        validators.recent_activity.slice(-10).reverse().forEach(a => {
                            // Handle both Python boolean (True/False) and JavaScript boolean (true/false)
                            const isSuccess = a.success === true || a.success === 'True' || a.success === 'true';
                            const status = isSuccess ? '<span class="badge badge-success">OK</span>' : '<span class="badge badge-error">FAIL</span>';
                            
                            // Handle both 'time' and 'timestamp' fields
                            let timeStr = a.time || a.timestamp || '';
                            if (timeStr) {
                                // Ensure timezone indicator for proper parsing
                                if (!timeStr.endsWith('Z') && !timeStr.includes('+') && !timeStr.includes('-', 10)) {
                                    timeStr = timeStr + 'Z';
                                }
                                
                                try {
                                    const date = new Date(timeStr);
                                    // Check if date is valid
                                    if (!isNaN(date.getTime())) {
                                        const timeFormatted = date.toLocaleString('en-US', { 
                                            timeZone: 'America/Chicago',
                                            hour: '2-digit',
                                            minute: '2-digit',
                                            second: '2-digit',
                                            hour12: true,
                                            month: 'short',
                                            day: 'numeric'
                                        });
                                        const respTime = (a.response_time && a.response_time > 0) ? a.response_time.toFixed(3) + 's' : '<span style="color: #86868b;">-</span>';
                                        html += `<tr><td>${timeFormatted}</td><td><code>${a.ip || 'unknown'}</code></td><td>${status}</td><td>${respTime}</td></tr>`;
                                    } else {
                                        // Invalid date, show raw timestamp
                                        html += `<tr><td>${timeStr}</td><td><code>${a.ip || 'unknown'}</code></td><td>${status}</td><td>-</td></tr>`;
                                    }
                                } catch (e) {
                                    // Error parsing date, show raw timestamp
                                    html += `<tr><td>${timeStr}</td><td><code>${a.ip || 'unknown'}</code></td><td>${status}</td><td>-</td></tr>`;
                                }
                            } else {
                                // No timestamp, show what we have
                                html += `<tr><td>-</td><td><code>${a.ip || 'unknown'}</code></td><td>${status}</td><td>-</td></tr>`;
                            }
                        });
                        html += '</table>';
                        document.getElementById('recent-activity').innerHTML = html;
                    } else {
                        document.getElementById('recent-activity').innerHTML = '<div class="loading">Waiting for validator requests...</div>';
                    }
                    
                    // Task types
                    const taskTypes = data.task_types || {};
                    if (taskTypes && Object.keys(taskTypes).length > 0) {
                        let html = '<table><tr><th>Type</th><th>Rate</th><th>Total</th></tr>';
                        for (const [type, stats] of Object.entries(taskTypes)) {
                            const successRate = stats.success_rate || (stats.success || 0) / (stats.total || 1) * 100;
                            const cls = successRate >= 80 ? 'status-good' : 'status-error';
                            html += `<tr><td><code>${type}</code></td><td class="${cls}">${successRate.toFixed(1)}%</td><td>${stats.total || 0}</td></tr>`;
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
                    console.error('Error loading metrics:', error);
                    // Show error in all sections that might be blank
                    const sections = ['performance', 'god-tier', 'recent-activity', 'task-types', 
                                     'top-validators', 'errors', 'anti-overfitting', 'task-diversity'];
                    sections.forEach(sectionId => {
                        const el = document.getElementById(sectionId);
                        if (el && (!el.innerHTML || el.innerHTML.trim() === '' || el.innerHTML.includes('Loading...'))) {
                            el.innerHTML = '<div class="loading status-error">Error loading data</div>';
                        }
                    });
                    if (document.getElementById('last-update')) {
                        document.getElementById('last-update').textContent = 'Error: ' + error.message;
                    }
                }
            }
            
            // Round countdown timer (updates every second)
            function updateRoundCountdown() {
                if (window.roundCountdownSeconds !== undefined && window.roundCountdownSeconds > 0) {
                    window.roundCountdownSeconds--;
                    const countdownEl = document.getElementById('round-countdown');
                    if (countdownEl) {
                        const hours = Math.floor(window.roundCountdownSeconds / 3600);
                        const minutes = Math.floor((window.roundCountdownSeconds % 3600) / 60);
                        const secs = window.roundCountdownSeconds % 60;
                        let formatted = '';
                        if (hours > 0) {
                            formatted = hours + 'h ' + minutes + 'm ' + secs + 's';
                        } else if (minutes > 0) {
                            formatted = minutes + 'm ' + secs + 's';
                        } else {
                            formatted = secs + 's';
                        }
                        countdownEl.textContent = formatted;
                    }
                }
            }
            
            loadMetrics();
            setInterval(loadMetrics, 5000);
            setInterval(updateRoundCountdown, 1000);  // Update countdown every second
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


# Cache wallet info to avoid OOM issues
_wallet_info_cache = {"data": None, "timestamp": 0}
_wallet_info_cache_ttl = 60  # Cache for 60 seconds

# Cache round info to avoid OOM issues
_round_info_cache = {"data": None, "timestamp": 0}
_round_info_cache_ttl = 30  # Cache for 30 seconds

def get_round_info():
    """Get current round information from Bittensor"""
    import time
    
    # Return cached data if still valid
    current_time = time.time()
    if _round_info_cache["data"] and (current_time - _round_info_cache["timestamp"]) < _round_info_cache_ttl:
        return _round_info_cache["data"]
    
    try:
        import bittensor as bt
        from config.settings import settings
        
        subtensor = bt.subtensor(network='finney')
        
        # Get current block number
        current_block = subtensor.get_current_block()
        
        # IWA rounds are typically ~1080 blocks (1-2 hours at ~12s per block)
        # Round 37 started at block 6,912,165 (from IWA Platform data)
        # We can estimate current round based on block number
        blocks_per_round = 1080  # Approximate, based on IWA Platform data
        
        # Estimate round number (this is approximate)
        # Round 37 started at block 6,912,165
        base_round = 37
        base_block = 6912165
        
        if current_block >= base_block:
            blocks_since_base = current_block - base_block
            rounds_since_base = blocks_since_base // blocks_per_round
            estimated_round = base_round + rounds_since_base
            blocks_into_round = blocks_since_base % blocks_per_round
        else:
            # If current block is before our base, estimate backwards
            blocks_before_base = base_block - current_block
            rounds_before_base = blocks_before_base // blocks_per_round
            estimated_round = base_round - rounds_before_base
            blocks_into_round = blocks_per_round - (blocks_before_base % blocks_per_round)
        
        # Calculate time until next round
        blocks_remaining = blocks_per_round - blocks_into_round
        seconds_per_block = 12  # Bittensor block time
        seconds_until_next_round = blocks_remaining * seconds_per_block
        
        result = {
            "current_round": estimated_round,
            "current_block": int(current_block),
            "blocks_into_round": blocks_into_round,
            "blocks_per_round": blocks_per_round,
            "blocks_remaining": blocks_remaining,
            "seconds_until_next_round": seconds_until_next_round,
            "round_progress": round((blocks_into_round / blocks_per_round) * 100, 1)
        }
        
        # Cache the result
        _round_info_cache["data"] = result
        _round_info_cache["timestamp"] = current_time
        return result
        
    except Exception as e:
        # Return cached data if available
        if _round_info_cache["data"]:
            return _round_info_cache["data"]
        
        # Return default values if error
        return {
            "current_round": 0,
            "current_block": 0,
            "blocks_into_round": 0,
            "blocks_per_round": 1080,
            "blocks_remaining": 1080,
            "seconds_until_next_round": 12960,  # ~3.6 hours default
            "round_progress": 0.0,
            "error": str(e)
        }

def get_wallet_info():
    """Get wallet balance and stake information from Bittensor (cached)"""
    import time
    
    # Return cached data if still valid
    current_time = time.time()
    if _wallet_info_cache["data"] and (current_time - _wallet_info_cache["timestamp"]) < _wallet_info_cache_ttl:
        return _wallet_info_cache["data"]
    
    try:
        import bittensor as bt
        from config.settings import settings
        
        wallet = bt.wallet(name='default', hotkey='default')
        subtensor = bt.subtensor(network='finney')
        
        # Get balance (lightweight operation)
        balance = subtensor.get_balance(wallet.coldkeypub.ss58_address)
        balance_tao = float(balance.tao) if hasattr(balance, 'tao') else float(balance)
        
        # Get stake and other metrics (memory-intensive, so we cache it)
        # Note: sync parameter not available in all Bittensor versions
        try:
            metagraph = subtensor.metagraph(settings.subnet_uid, sync=False)  # Try with sync=False first
        except TypeError:
            # Fallback: sync parameter not supported, use default
            metagraph = subtensor.metagraph(settings.subnet_uid)
        uid = metagraph.hotkeys.index(wallet.hotkey.ss58_address) if wallet.hotkey.ss58_address in metagraph.hotkeys else None
        
        if uid is not None:
            total_stake = metagraph.S[uid].item() if hasattr(metagraph, 'S') and uid < len(metagraph.S) else 0
            
            # Try to get stake FROM your coldkey specifically
            your_stake = 0.0
            delegator_stake = 0.0
            try:
                # Try different method signatures
                try:
                    stake_from_you = subtensor.get_stake_for_coldkey_and_hotkey(
                        coldkey_ss58=wallet.coldkeypub.ss58_address,
                        hotkey_ss58=wallet.hotkey.ss58_address
                    )
                except TypeError:
                    # Try without netuid parameter
                    stake_from_you = subtensor.get_stake(
                        coldkey_ss58=wallet.coldkeypub.ss58_address,
                        hotkey_ss58=wallet.hotkey.ss58_address
                    )
                
                your_stake = float(stake_from_you.tao) if hasattr(stake_from_you, 'tao') else float(stake_from_you)
                delegator_stake = max(0, total_stake - your_stake)
            except Exception as e:
                # If we can't get the breakdown, we'll show total stake
                # and note that it may include delegators
                your_stake = 0.0  # Unknown - will show as 0.00
                delegator_stake = total_stake  # Assume all is delegator until we can verify
            
            rank = metagraph.R[uid].item() if hasattr(metagraph, 'R') and uid < len(metagraph.R) else 0
            trust = metagraph.T[uid].item() if hasattr(metagraph, 'T') and uid < len(metagraph.T) else 0
            incentive = metagraph.I[uid].item() if hasattr(metagraph, 'I') and uid < len(metagraph.I) else 0
            
            result = {
                "balance_tao": balance_tao,
                "stake_tao": float(total_stake),  # Total stake (for backwards compatibility)
                "your_stake_tao": float(your_stake),  # Your stake specifically
                "delegator_stake_tao": float(delegator_stake),  # Delegator stake
                "rank": float(rank),
                "trust": float(trust),
                "incentive": float(incentive),
                "uid": uid
            }
        else:
            result = {
                "balance_tao": balance_tao,
                "stake_tao": 0.0,
                "your_stake_tao": 0.0,
                "delegator_stake_tao": 0.0,
                "rank": 0.0,
                "trust": 0.0,
                "incentive": 0.0,
                "uid": None
            }
        
        # Cache the result
        _wallet_info_cache["data"] = result
        _wallet_info_cache["timestamp"] = current_time
        return result
        
    except Exception as e:
        # Return cached data if available, even if expired, to avoid showing errors
        if _wallet_info_cache["data"]:
            return _wallet_info_cache["data"]
        
        # Return zeros if there's an error and no cache
        return {
            "balance_tao": 0.0,
            "stake_tao": 0.0,
            "your_stake_tao": 0.0,
            "delegator_stake_tao": 0.0,
            "rank": 0.0,
            "trust": 0.0,
            "incentive": 0.0,
            "uid": None,
            "error": str(e)
        }


@router.get("/dashboard/metrics")
async def dashboard_metrics():
    """Get real-time metrics as JSON"""
    import subprocess
    import re
    from datetime import datetime
    
    advanced_metrics = get_advanced_metrics()
    metrics = advanced_metrics.get_comprehensive_metrics()
    # Health score will be recalculated after we update metrics from logs
    # Don't set it here as it might be based on stale data
    
    # WALLET INFO: Add wallet balance and stake information
    try:
        wallet_info = get_wallet_info()
        # Map the wallet_info keys to match what the dashboard expects
        metrics["wallet"] = {
            "balance": wallet_info.get("balance_tao", 0.0),
            "total_stake": wallet_info.get("stake_tao", 0.0),
            "your_stake": wallet_info.get("your_stake_tao", 0.0),
            "delegator_stake": wallet_info.get("delegator_stake_tao", 0.0),
            "rank": wallet_info.get("rank", 0.0),
            "trust": wallet_info.get("trust", 0.0),
            "incentive": wallet_info.get("incentive", 0.0),
            "uid": wallet_info.get("uid", None),
            # Also include original keys for backwards compatibility
            "balance_tao": wallet_info.get("balance_tao", 0.0),
            "stake_tao": wallet_info.get("stake_tao", 0.0),
            "your_stake_tao": wallet_info.get("your_stake_tao", 0.0),
            "delegator_stake_tao": wallet_info.get("delegator_stake_tao", 0.0),
        }
    except Exception as e:
        metrics["wallet"] = {
            "balance": 0.0,
            "total_stake": 0.0,
            "your_stake": 0.0,
            "delegator_stake": 0.0,
            "rank": 0.0,
            "trust": 0.0,
            "incentive": 0.0,
            "uid": None,
            "error": str(e)
        }
    
    # ROUND INFO: Add current round information
    try:
        round_info = get_round_info()
        metrics["round"] = round_info
    except Exception:
        metrics["round"] = {
            "current_round": 0,
            "seconds_until_next_round": 0,
            "round_progress": 0.0
        }
    
    # DYNAMIC ZERO: Add anti-overfitting metrics
    try:
        from api.utils.anti_overfitting import anti_overfitting
        from api.utils.task_diversity import task_diversity
        metrics["anti_overfitting"] = anti_overfitting.get_overfitting_metrics()
        metrics["task_diversity"] = task_diversity.get_diversity_metrics()
    except Exception:
        metrics["anti_overfitting"] = {}
        metrics["task_diversity"] = {}
    
    # Store current in-memory metrics (should only contain validator requests now)
    # But we'll still rebuild from logs to ensure accuracy and filter any old localhost data
    current_total_requests = metrics["overview"]["total_requests"]
    current_successful = metrics["overview"]["successful_requests"]
    current_failed = metrics["overview"]["failed_requests"]
    current_response_times = list(advanced_metrics.response_times) if hasattr(advanced_metrics, 'response_times') else []
    
    # Also get validator activity from in-memory (filters localhost)
    in_memory_validator_activity = []
    if hasattr(advanced_metrics, 'validator_activity'):
        for activity in advanced_metrics.validator_activity:
            ip = activity.get("ip", "")
            if ip and ip not in ["127.0.0.1", "localhost", "::1"]:
                if not ip.startswith("192.168.") and not ip.startswith("10.") and not ip.startswith("172.16.") and ip != "134.199.203.133":
                    in_memory_validator_activity.append(activity)
    
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
                # Try multiple regex patterns to match different log formats
                match = None
                # Pattern 1: Standard format with quotes and status code
                match = re.search(r'(\w+\s+\d+\s+\d+:\d+:\d+).*?INFO:\s+([\d.]+):\d+\s+-\s+"POST\s+/solve_task.*?"\s+(\d+)', line)
                if not match:
                    # Pattern 2: Format with "HTTP/1.1" and status code
                    match = re.search(r'(\w+\s+\d+\s+\d+:\d+:\d+).*?INFO:\s+([\d.]+):\d+\s+-\s+"POST\s+/solve_task.*?HTTP/1\.1"\s+(\d+)', line)
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
            
            # Merge with in-memory validator activity (more recent, may not be in logs yet)
            # Combine and deduplicate by time and IP, preserving response times from in-memory
            combined_activity = {}
            for activity in validator_activity + in_memory_validator_activity:
                key = f"{activity.get('ip')}_{activity.get('time', '')}"
                if key not in combined_activity:
                    combined_activity[key] = activity
                else:
                    # Keep more recent, but preserve response_time if available
                    existing = combined_activity[key]
                    new_time = activity.get("time", "")
                    existing_time = existing.get("time", "")
                    if new_time > existing_time:
                        # Newer activity - use it, but preserve response_time if existing has it and new doesn't
                        if existing.get("response_time", 0.0) > 0 and activity.get("response_time", 0.0) == 0.0:
                            activity["response_time"] = existing.get("response_time", 0.0)
                        combined_activity[key] = activity
                    elif existing.get("response_time", 0.0) == 0.0 and activity.get("response_time", 0.0) > 0:
                        # Existing has no response_time but new one does - update it
                        existing["response_time"] = activity.get("response_time", 0.0)
            
            validator_activity = list(combined_activity.values())
            
            # Sort by time (most recent first) for display
            validator_activity.sort(key=lambda x: x.get("time", x.get("timestamp", "")), reverse=True)
            
            # Use validator activity from logs as source of truth (filters out localhost)
            # In-memory metrics may include old localhost data, so we prioritize filtered validator activity
            validator_total = len(validator_activity)
            validator_successful = sum(1 for a in validator_activity if a.get("success", False) or a.get("success") == "True" or a.get("success") == "true")
            validator_failed = validator_total - validator_successful
            
            # Always use validator activity counts (filters localhost correctly)
            # In-memory may have old localhost data, so we trust the filtered logs
            metrics["overview"]["total_requests"] = validator_total
            metrics["overview"]["successful_requests"] = validator_successful
            metrics["overview"]["failed_requests"] = validator_failed
            
            # Only use in-memory if it has MORE validator requests (new requests not yet in logs)
            # But only if in-memory looks valid (not all failed, which indicates old localhost data)
            if current_total_requests > validator_total and current_successful > 0:
                # In-memory has more AND has successful requests (likely new validator requests)
                metrics["overview"]["total_requests"] = current_total_requests
                metrics["overview"]["successful_requests"] = current_successful
                metrics["overview"]["failed_requests"] = current_failed
            
            # Recalculate success rate based on updated counts
            if metrics["overview"]["total_requests"] > 0:
                metrics["overview"]["success_rate"] = round(
                    (metrics["overview"]["successful_requests"] / metrics["overview"]["total_requests"]) * 100, 2
                )
            
            # Calculate response times from in-memory data OR from validator activity
            # Priority: in-memory response_times > in-memory validator_activity > log-based validator_activity
            response_times_to_use = []
            
            # First, try in-memory response_times (most accurate)
            if current_response_times and len(current_response_times) > 0:
                response_times_to_use = list(current_response_times)
            
            # Second, try in-memory validator_activity response times
            if not response_times_to_use and in_memory_validator_activity:
                response_times_to_use = [a.get("response_time", 0.0) for a in in_memory_validator_activity if a.get("response_time", 0.0) > 0]
            
            # Third, try log-based validator_activity response times
            if not response_times_to_use:
                activity_response_times = [a.get("response_time", 0.0) for a in validator_activity if a.get("response_time", 0.0) > 0]
                if activity_response_times:
                    response_times_to_use = activity_response_times
            
            # Calculate metrics from response times
            if response_times_to_use and len(response_times_to_use) > 0:
                metrics["performance"]["avg_response_time"] = round(sum(response_times_to_use) / len(response_times_to_use), 3)
                sorted_times = sorted(response_times_to_use)
                if len(sorted_times) >= 20:
                    metrics["performance"]["p95_response_time"] = round(sorted_times[int(len(sorted_times) * 0.95)], 3)
                    metrics["performance"]["p99_response_time"] = round(sorted_times[int(len(sorted_times) * 0.99)], 3)
                elif len(sorted_times) >= 5:
                    # Use available data for p95 even if less than 20 samples
                    metrics["performance"]["p95_response_time"] = round(sorted_times[int(len(sorted_times) * 0.95)], 3)
            
            uptime_hours = metrics["overview"].get("uptime_hours", 0.0)
            # If uptime is 0, calculate it from start_time
            if uptime_hours == 0.0 and hasattr(advanced_metrics, 'start_time'):
                import time
                uptime_seconds = time.time() - advanced_metrics.start_time
                uptime_hours = max(0.01, uptime_seconds / 3600)  # At least 0.01 hours
                metrics["overview"]["uptime_hours"] = round(uptime_hours, 2)
            
            # Calculate requests per minute (only if we have requests and uptime)
            if uptime_hours > 0 and metrics["overview"]["total_requests"] > 0:
                metrics["performance"]["requests_per_minute"] = round(
                    metrics["overview"]["total_requests"] / (uptime_hours * 60), 2
                )
            elif metrics["overview"]["total_requests"] > 0:
                # If uptime is 0 but we have requests, use a default calculation
                # This handles the case where service just restarted but has historical data
                metrics["performance"]["requests_per_minute"] = 0.0
            
            # Health score should only be calculated if we have requests
            if metrics["overview"]["total_requests"] > 0:
                success_rate = metrics["overview"]["success_rate"]
                avg_response_time = metrics["performance"].get("avg_response_time", 0.0)
                # Response time score: 100% for <1s, decreasing for slower responses
                # Formula: max(0, 100 - (response_time * 10))
                # This gives: 1s = 90%, 2s = 80%, 5s = 50%, 10s = 0%
                response_time_score = max(0, min(100, 100 - (avg_response_time * 10)))
                # Uptime score: increases with uptime, capped at 100%
                # Formula: min(100, uptime_hours * 10)
                # This gives: 0.1h = 1%, 1h = 10%, 10h = 100%
                uptime_score = min(100, max(0, uptime_hours * 10))
                metrics["health_score"] = round(
                    success_rate * 0.5 + response_time_score * 0.3 + uptime_score * 0.2, 2
                )
            else:
                # No requests = no health score (can't evaluate performance)
                metrics["health_score"] = 0.0
            
            # Ensure recent_activity is sorted by time (most recent first) and limit to 20
            # (Already sorted above, but ensure it's still sorted)
            # Also ensure boolean values are properly formatted for JSON
            recent_activity_formatted = []
            for activity in validator_activity[:20]:
                formatted = {
                    "time": activity.get("time", activity.get("timestamp", "")),
                    "ip": activity.get("ip", "unknown"),
                    "success": bool(activity.get("success", False) if isinstance(activity.get("success"), bool) else str(activity.get("success", "False")).lower() == "true"),
                    "response_time": float(activity.get("response_time", 0.0)),
                    "source": activity.get("source", "validator")
                }
                recent_activity_formatted.append(formatted)
            
            metrics["validators"]["recent_activity"] = recent_activity_formatted
            metrics["validators"]["unique_validators"] = len(set(a["ip"] for a in validator_activity))
            
            from collections import Counter
            ip_counts = Counter(a["ip"] for a in validator_activity)
            metrics["validators"]["top_validators"] = [
                {"ip": ip, "requests": count} 
                for ip, count in ip_counts.most_common(5)
            ]
    except Exception:
        pass
    
    # Always recalculate health score at the end to ensure it's correct
    # This ensures health score is always calculated based on current metrics
    uptime_hours = metrics["overview"].get("uptime_hours", 0.0)
    # If uptime is 0, try to calculate it from start_time
    if uptime_hours == 0.0 and hasattr(advanced_metrics, 'start_time'):
        import time
        uptime_seconds = time.time() - advanced_metrics.start_time
        uptime_hours = max(0.01, uptime_seconds / 3600)  # At least 0.01 hours
        metrics["overview"]["uptime_hours"] = round(uptime_hours, 2)
    
    # Recalculate health score with proper bounds checking
    # Health score should be 0 if no requests have been processed
    if metrics["overview"]["total_requests"] > 0:
        success_rate = metrics["overview"].get("success_rate", 0)
        avg_response_time = metrics["performance"].get("avg_response_time", 0.0)
        # Response time score: 100% for <1s, decreasing for slower responses
        response_time_score = max(0, min(100, 100 - (avg_response_time * 10)))
        # Uptime score: increases with uptime, capped at 100%
        uptime_score = min(100, max(0, uptime_hours * 10))
        metrics["health_score"] = round(
            success_rate * 0.5 + response_time_score * 0.3 + uptime_score * 0.2, 2
        )
    else:
        # No requests = no health score (can't evaluate performance)
        metrics["health_score"] = 0.0
    
    # Add metadata about data freshness
    if validator_activity:
        latest_activity_time = validator_activity[0].get("time", "")
        if latest_activity_time:
            try:
                from datetime import datetime, timezone
                latest_dt = datetime.fromisoformat(latest_activity_time.replace('Z', '+00:00'))
                now_dt = datetime.now(timezone.utc)
                hours_since_activity = (now_dt - latest_dt).total_seconds() / 3600
                metrics["data_freshness"] = {
                    "latest_activity": latest_activity_time,
                    "hours_since_activity": round(hours_since_activity, 2),
                    "is_stale": hours_since_activity > 1.0  # Consider stale if > 1 hour
                }
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
