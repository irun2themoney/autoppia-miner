// Dashboard Logic
let performanceChart = null;
const chartData = {
    labels: [],
    datasets: [
        {
            label: 'Success Rate (%)',
            data: [],
            borderColor: '#10b981',
            backgroundColor: 'rgba(16, 185, 129, 0.1)',
            borderWidth: 2,
            fill: true,
            tension: 0.4,
            yAxisID: 'y',
        },
        {
            label: 'Latency (ms)',
            data: [],
            borderColor: '#6366f1',
            backgroundColor: 'rgba(99, 102, 241, 0.1)',
            borderWidth: 2,
            fill: true,
            tension: 0.4,
            yAxisID: 'y1',
        },
        {
            label: 'Req/min',
            data: [],
            borderColor: '#f59e0b',
            backgroundColor: 'rgba(245, 158, 11, 0.1)',
            borderWidth: 2,
            fill: true,
            tension: 0.4,
            yAxisID: 'y2',
        }
    ]
};

function initChart() {
    const ctx = document.getElementById('performanceChart').getContext('2d');

    // Chart.js Dark Mode Defaults
    Chart.defaults.color = '#949ba4';
    Chart.defaults.borderColor = '#2a2e36';

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
                    display: false // Custom legend in HTML
                },
                tooltip: {
                    backgroundColor: '#181b21',
                    titleColor: '#ffffff',
                    bodyColor: '#949ba4',
                    borderColor: '#2a2e36',
                    borderWidth: 1,
                    padding: 12,
                    cornerRadius: 8,
                    displayColors: true
                }
            },
            scales: {
                x: {
                    grid: { display: false },
                    ticks: { font: { size: 11 } }
                },
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    min: 0,
                    max: 100,
                    grid: { borderDash: [4, 4] }
                },
                y1: {
                    type: 'linear',
                    display: false, // Hide axis but keep data
                    position: 'right',
                    grid: { display: false }
                },
                y2: {
                    type: 'linear',
                    display: false,
                    position: 'right',
                    grid: { display: false }
                }
            }
        }
    });
}

function updateChart(data) {
    if (!performanceChart) initChart();

    const now = new Date();
    const timeLabel = now.toLocaleTimeString('en-US', {
        hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false
    });

    const overview = data.overview || {};
    const perf = data.performance || {};

    // Add new data point
    chartData.labels.push(timeLabel);
    chartData.datasets[0].data.push(parseFloat(overview.success_rate || 0));
    chartData.datasets[1].data.push((parseFloat(perf.avg_response_time || 0) * 1000));
    chartData.datasets[2].data.push(parseFloat(perf.requests_per_minute || 0));

    // Keep last 30 points
    if (chartData.labels.length > 30) {
        chartData.labels.shift();
        chartData.datasets.forEach(d => d.data.shift());
    }

    performanceChart.update('none'); // 'none' mode for smoother animation
}

async function loadMetrics() {
    try {
        const response = await fetch('/api/dashboard/metrics');
        if (!response.ok) throw new Error('Failed to fetch metrics');
        const data = await response.json();

        updateUI(data);
        updateChart(data);

    } catch (error) {
        console.error('Error:', error);
        document.getElementById('last-update').textContent = 'Connection Lost';
        document.getElementById('last-update').style.color = '#ef4444';
    }
}

function updateUI(data) {
    // Helper to safely get nested data
    const get = (obj, path, def = '-') => {
        return path.split('.').reduce((o, i) => (o ? o[i] : undefined), obj) ?? def;
    };

    // Update Timestamp
    const now = new Date();
    document.getElementById('last-update').textContent = now.toLocaleTimeString();
    document.getElementById('last-update').style.color = 'var(--text-secondary)';

    // Overview Metrics
    const total = get(data, 'overview.total_requests', 0);
    const success = get(data, 'overview.successful_requests', 0);
    const failed = get(data, 'overview.failed_requests', 0);
    const successRate = parseFloat(get(data, 'overview.success_rate', 0)).toFixed(1);

    updateValue('success-rate', `${successRate}%`, successRate >= 90 ? 'good' : successRate >= 70 ? 'warning' : 'error');
    document.getElementById('success-detail').textContent = `${success} successful`;

    updateValue('total-requests', total.toLocaleString());
    document.getElementById('req-detail').textContent = `${failed} failed`;

    const health = parseFloat(get(data, 'health_score', 0)).toFixed(1);
    updateValue('health-score', health, health >= 90 ? 'good' : health >= 70 ? 'warning' : 'error');
    document.getElementById('health-detail').textContent = 'System Status';

    const avgTime = parseFloat(get(data, 'performance.avg_response_time', 0)).toFixed(3);
    updateValue('avg-response', `${avgTime}s`, avgTime < 1 ? 'good' : avgTime < 3 ? 'warning' : 'error');
    document.getElementById('response-detail').textContent = `P95: ${parseFloat(get(data, 'performance.p95_response_time', 0)).toFixed(3)}s`;

    // Secondary Metrics
    const cacheRate = parseFloat(get(data, 'caching.cache_hit_rate', 0)).toFixed(1);
    updateValue('cache-hit', `${cacheRate}%`);
    document.getElementById('cache-detail').textContent = `${get(data, 'caching.cache_hits', 0)} hits`;

    const validators = get(data, 'validators.unique_validators', 0);
    updateValue('validators', validators);
    document.getElementById('validator-detail').textContent = 'Active Unique';

    const balance = parseFloat(get(data, 'wallet.balance_tao', 0)).toFixed(4);
    updateValue('wallet-balance', balance, balance > 0 ? 'good' : '');

    const round = get(data, 'round.current_round', '-');
    updateValue('current-round', round);

    // Round Countdown
    const seconds = get(data, 'round.seconds_until_next_round', 0);
    document.getElementById('round-detail').textContent = `Next: ${formatTime(seconds)}`;

    // God Tier Features
    const vector = data.vector_memory || {};
    const mutations = data.mutations || {};
    document.getElementById('god-tier').innerHTML = `
        <div class="compact-stat"><div class="compact-stat-value">${cacheRate}%</div><div class="compact-stat-label">Cache</div></div>
        <div class="compact-stat"><div class="compact-stat-value">${(vector.hit_rate || 0).toFixed(1)}%</div><div class="compact-stat-label">Vector</div></div>
        <div class="compact-stat"><div class="compact-stat-value">${mutations.detected || 0}</div><div class="compact-stat-label">Mutations</div></div>
        <div class="compact-stat"><div class="compact-stat-value">${(mutations.handling_rate || 0).toFixed(1)}%</div><div class="compact-stat-label">Handled</div></div>
    `;

    // Anti-Overfitting
    const ao = data.anti_overfitting || {};
    document.getElementById('anti-overfitting').innerHTML = `
        <div class="compact-stat"><div class="compact-stat-value">${(ao.diversity_score * 100 || 0).toFixed(1)}%</div><div class="compact-stat-label">Diversity</div></div>
        <div class="compact-stat"><div class="compact-stat-value">${ao.overused_patterns || 0}</div><div class="compact-stat-label">Overused</div></div>
        <div class="compact-stat"><div class="compact-stat-value ${ao.is_overfitting ? 'error' : 'good'}">${ao.is_overfitting ? '⚠️' : '✓'}</div><div class="compact-stat-label">Status</div></div>
    `;

    // Recent Activity
    const activity = data.validators?.recent_activity || [];
    if (activity.length > 0) {
        let html = '<table><thead><tr><th>Time</th><th>IP</th><th>Status</th><th>Latency</th></tr></thead><tbody>';
        activity.slice(0, 10).forEach(a => {
            const isSuccess = String(a.success).toLowerCase() === 'true';
            const badge = isSuccess ? '<span class="badge badge-success">OK</span>' : '<span class="badge badge-error">FAIL</span>';
            const time = new Date(a.time).toLocaleTimeString();
            html += `<tr>
                <td>${time}</td>
                <td><code>${a.ip}</code></td>
                <td>${badge}</td>
                <td>${parseFloat(a.response_time).toFixed(3)}s</td>
            </tr>`;
        });
        html += '</tbody></table>';
        document.getElementById('recent-activity').innerHTML = html;
    } else {
        document.getElementById('recent-activity').innerHTML = '<div style="padding:20px;text-align:center;color:var(--text-tertiary)">No recent activity</div>';
    }

    // Top Validators
    const top = data.validators?.top_validators || [];
    if (top.length > 0) {
        let html = '<table><thead><tr><th>Rank</th><th>IP</th><th>Requests</th></tr></thead><tbody>';
        top.forEach((v, i) => {
            html += `<tr>
                <td>#${i + 1}</td>
                <td><code>${v.ip}</code></td>
                <td>${v.requests}</td>
            </tr>`;
        });
        html += '</tbody></table>';
        document.getElementById('top-validators').innerHTML = html;
    }

    // Task Types
    const tasks = data.task_types || {};
    if (Object.keys(tasks).length > 0) {
        let html = '<table><thead><tr><th>Type</th><th>Rate</th><th>Total</th></tr></thead><tbody>';
        Object.entries(tasks).forEach(([type, stats]) => {
            const rate = stats.success_rate || (stats.success / stats.total * 100);
            html += `<tr>
                <td><code>${type}</code></td>
                <td style="color:${rate >= 80 ? 'var(--accent-success)' : 'var(--accent-error)'}">${rate.toFixed(1)}%</td>
                <td>${stats.total}</td>
            </tr>`;
        });
        html += '</tbody></table>';
        document.getElementById('task-types').innerHTML = html;
    }
}

function updateValue(id, value, className = '') {
    const el = document.getElementById(id);
    if (el) {
        el.textContent = value;
        if (className) el.className = `card-value ${className}`;
        else el.className = 'card-value';
    }
}

function formatTime(seconds) {
    if (seconds <= 0) return 'Starting...';
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    if (h > 0) return `${h}h ${m}m`;
    return `${m}m ${seconds % 60}s`;
}

// Start
window.addEventListener('load', () => {
    loadMetrics();
    setInterval(loadMetrics, 5000);
});
