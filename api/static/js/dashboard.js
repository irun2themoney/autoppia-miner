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
    // Chart removed in simplified dashboard - comment out to reduce load
    // if (!performanceChart) initChart();
    // const now = new Date();
    // const timeLabel = now.toLocaleTimeString('en-US', {
    //     hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false
    // });
    // const overview = data.overview || {};
    // const perf = data.performance || {};
    // chartData.labels.push(timeLabel);
    // chartData.datasets[0].data.push(parseFloat(overview.success_rate || 0));
    // chartData.datasets[1].data.push((parseFloat(perf.avg_response_time || 0) * 1000));
    // chartData.datasets[2].data.push(parseFloat(perf.requests_per_minute || 0));
    // if (chartData.labels.length > 30) {
    //     chartData.labels.shift();
    //     chartData.datasets.forEach(d => d.data.shift());
    // }
    // performanceChart.update('none');
}

async function loadMetrics() {
    try {
        // Add timeout to fetch to prevent hanging
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 5000); // 5 second timeout
        
        const response = await fetch('/api/dashboard/metrics', {
            signal: controller.signal,
            headers: {
                'Accept': 'application/json',
            }
        });
        
        clearTimeout(timeoutId);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();

        // Check if we got an error response
        if (data.error && !data.overview) {
            throw new Error(data.error);
        }

        // Store data globally for search/filter functionality
        window.lastMetricsData = data;

        // Update UI with the data
        updateUI(data);
        // updateChart(data); // Chart removed in simplified dashboard
        
        // Live activity feed removed - using only Validator Interactions table

        // Update last update time
        const lastUpdateEl = document.getElementById('last-update');
        if (lastUpdateEl) {
            lastUpdateEl.textContent = new Date().toLocaleTimeString();
            lastUpdateEl.style.color = 'var(--text-secondary)';
        }

    } catch (error) {
        console.error('Error loading metrics:', error);
        const lastUpdateEl = document.getElementById('last-update');
        if (lastUpdateEl) {
            if (error.name === 'AbortError') {
                lastUpdateEl.textContent = 'Request Timeout';
            } else {
                lastUpdateEl.textContent = 'Connection Lost';
            }
            lastUpdateEl.style.color = '#ef4444';
        }
        // Show error in console for debugging
        console.error('Dashboard error details:', error);
        
        // Try to show partial data if available
        if (window.lastMetricsData) {
            console.log('Using cached data from previous load');
            updateUI(window.lastMetricsData);
        }
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

    // Overview Metrics - ensure we get actual values, not defaults
    const overview = data.overview || {};
    const total = parseInt(overview.total_requests) || 0;
    const success = parseInt(overview.successful_requests) || 0;
    const failed = parseInt(overview.failed_requests) || 0;
    const successRate = parseFloat(overview.success_rate) || 0;
    const uptime = parseFloat(overview.uptime_hours) || 0;

    // Show meaningful data even when no requests yet
    if (total === 0) {
        updateValue('success-rate', 'Waiting...', 'warning');
        const successDetailEl = document.getElementById('success-detail');
        if (successDetailEl) successDetailEl.textContent = 'No requests yet';
        updateValue('total-requests', '0');
        const reqDetailEl = document.getElementById('req-detail');
        if (reqDetailEl) {
            // Show uptime with better formatting (at least 1 decimal, but show more precision if < 1 hour)
            if (uptime < 1) {
                const minutes = Math.floor(uptime * 60);
                reqDetailEl.textContent = `Uptime: ${minutes}m`;
            } else {
                reqDetailEl.textContent = `Uptime: ${uptime.toFixed(1)}h`;
            }
        }
    } else {
        updateValue('success-rate', `${successRate.toFixed(1)}%`, successRate >= 90 ? 'good' : successRate >= 70 ? 'warning' : 'error');
        const successDetailEl = document.getElementById('success-detail');
        if (successDetailEl) successDetailEl.textContent = `${success} successful`;
        updateValue('total-requests', total.toLocaleString());
        const reqDetailEl = document.getElementById('req-detail');
        if (reqDetailEl) reqDetailEl.textContent = `${failed} failed`;
    }

    const health = parseFloat(data.health_score || 0);
    if (total === 0) {
        updateValue('health-score', 'Ready', 'good');
        const healthDetailEl = document.getElementById('health-detail');
        if (healthDetailEl) {
            // Show uptime with better formatting (at least 1 decimal, but show more precision if < 1 hour)
            if (uptime < 1) {
                const minutes = Math.floor(uptime * 60);
                healthDetailEl.textContent = `Uptime: ${minutes}m`;
            } else {
                healthDetailEl.textContent = `Uptime: ${uptime.toFixed(1)}h`;
            }
        }
    } else {
        updateValue('health-score', health.toFixed(1), health >= 90 ? 'good' : health >= 70 ? 'warning' : 'error');
        const healthDetailEl = document.getElementById('health-detail');
        if (healthDetailEl) healthDetailEl.textContent = 'System Status';
    }

    const performance = data.performance || {};
    const avgTime = parseFloat(performance.avg_response_time || 0);
    if (total === 0) {
        updateValue('avg-response', 'Ready', 'good');
        const responseDetailEl = document.getElementById('response-detail');
        if (responseDetailEl) responseDetailEl.textContent = 'Waiting for requests';
    } else {
        updateValue('avg-response', `${avgTime.toFixed(3)}s`, avgTime < 1 ? 'good' : avgTime < 3 ? 'warning' : 'error');
        const responseDetailEl = document.getElementById('response-detail');
        if (responseDetailEl) responseDetailEl.textContent = `P95: ${parseFloat(performance.p95_response_time || 0).toFixed(3)}s`;
    }

    // Secondary Metrics - Cache Hit Rate removed from simplified dashboard
    // const cacheRate = parseFloat(get(data, 'caching.cache_hit_rate', 0)).toFixed(1);
    // updateValue('cache-hit', `${cacheRate}%`);
    // document.getElementById('cache-detail').textContent = `${get(data, 'caching.cache_hits', 0)} hits`;

    const validators = get(data, 'validators.unique_validators', 0);
    if (validators === 0 && total === 0) {
        updateValue('validators', 'Waiting');
        document.getElementById('validator-detail').textContent = 'No validators yet';
    } else {
        updateValue('validators', validators);
        document.getElementById('validator-detail').textContent = 'Active Unique';
    }

    const balance = parseFloat(get(data, 'wallet.balance_tao', 0));
    const walletUid = get(data, 'wallet.uid', null);
    if (balance === 0 && walletUid === null) {
        updateValue('wallet-balance', 'Loading...', 'warning');
        document.getElementById('wallet-balance-detail').textContent = 'Connecting...';
    } else {
        updateValue('wallet-balance', balance.toFixed(4), balance > 0 ? 'good' : '');
        if (walletUid !== null) {
            document.getElementById('wallet-balance-detail').textContent = `UID: ${walletUid} | TAO`;
        } else {
            document.getElementById('wallet-balance-detail').textContent = 'TAO';
        }
    }

    // Rewards Earned - MOTIVATIONAL!
    const rewards = data.rewards || {};
    const rewardsEarned = parseFloat(rewards.total_earned_tao || data.wallet?.rewards_earned_tao || 0);
    const baselineBalance = parseFloat(rewards.baseline_balance_tao || data.wallet?.baseline_balance_tao || 0);
    const rewardsEl = document.getElementById('rewards-earned');
    const rewardsDetailEl = document.getElementById('rewards-detail');
    
    if (rewardsEl) {
        if (rewardsEarned > 0) {
            rewardsEl.textContent = rewardsEarned.toFixed(4);
            rewardsEl.style.color = '#ffffff !important';
            rewardsEl.style.textShadow = '0 2px 4px rgba(0,0,0,0.2)';
            if (rewardsDetailEl) {
                const percentageIncrease = baselineBalance > 0 ? ((rewardsEarned / baselineBalance) * 100).toFixed(1) : '∞';
                rewardsDetailEl.textContent = baselineBalance > 0 ? `+${percentageIncrease}% from baseline (${baselineBalance.toFixed(4)} TAO)` : `Total rewards earned!`;
                rewardsDetailEl.style.color = 'rgba(255,255,255,0.9)';
            }
        } else {
            rewardsEl.textContent = '0.0000';
            rewardsEl.style.color = '#ffffff !important';
            if (rewardsDetailEl) {
                rewardsDetailEl.textContent = 'Keep mining to earn rewards!';
                rewardsDetailEl.style.color = 'rgba(255,255,255,0.9)';
            }
        }
    }

    const round = get(data, 'round.current_round', 0);
    const seconds = get(data, 'round.seconds_until_next_round', 0);
    const roundProgress = parseFloat(get(data, 'round.round_progress', 0)).toFixed(1);
    
    if (round === 0 || round === '-') {
        updateValue('current-round', 'Loading...');
        document.getElementById('round-detail').textContent = 'Fetching round info';
    } else {
        updateValue('current-round', round);
        document.getElementById('round-detail').textContent = `Next: ${formatTime(seconds)} (${roundProgress}%)`;
    }

    // Removed: God Tier Features, Anti-Overfitting, Miner Configuration sections
    // Removed: Recent Activity section (redundant with Validator Interactions log)
    // These are hidden in the simplified dashboard

    // Complete Validator Interaction Log (All Historical Data)
    const allActivity = data.validators?.all_activity || [];
    const totalInteractions = data.validators?.total_interactions || allActivity.length;
    document.getElementById('total-interactions').textContent = `${totalInteractions} total`;
    
    updateValidatorLog(allActivity);

    // Removed: Top Validators and Task Types sections
    // These are hidden in the simplified dashboard
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

function updateValidatorLog(allActivity) {
    const searchTerm = document.getElementById('log-search')?.value.toLowerCase() || '';
    const filterType = document.getElementById('log-filter')?.value || 'all';
    
    // Filter activity
    let filtered = allActivity;
    
    // Apply search filter
    if (searchTerm) {
        filtered = filtered.filter(a => {
            const ip = (a.ip || '').toLowerCase();
            const url = (a.task_url || '').toLowerCase();
            const prompt = (a.task_prompt || '').toLowerCase();
            return ip.includes(searchTerm) || url.includes(searchTerm) || prompt.includes(searchTerm);
        });
    }
    
    // Apply status filter
    if (filterType === 'success') {
        filtered = filtered.filter(a => a.success === true || String(a.success).toLowerCase() === 'true');
    } else if (filterType === 'failed') {
        filtered = filtered.filter(a => a.success === false || String(a.success).toLowerCase() === 'false');
    }
    
    // Sort by time (most recent first)
    filtered.sort((a, b) => {
        const timeA = new Date(a.time || 0).getTime();
        const timeB = new Date(b.time || 0).getTime();
        return timeB - timeA;
    });
    
    // Display
    const logElement = document.getElementById('validator-log');
    if (filtered.length > 0) {
        // Ensure all columns are visible with proper styling
        let html = '<table style="width: 100%; table-layout: auto;"><thead><tr>' +
            '<th style="min-width: 150px; white-space: nowrap;">Time</th>' +
            '<th style="min-width: 120px;">IP</th>' +
            '<th style="min-width: 70px; text-align: center;">Status</th>' +
            '<th style="min-width: 100px; text-align: right;">Response Time</th>' +
            '<th style="min-width: 120px;">Task Type</th>' +
            '<th style="min-width: 200px;">URL</th>' +
            '<th style="min-width: 300px;">Prompt</th>' +
            '</tr></thead><tbody>';
        filtered.forEach(a => {
            const isSuccess = a.success === true || String(a.success).toLowerCase() === 'true';
            const badge = isSuccess ? '<span class="badge badge-success">✓</span>' : '<span class="badge badge-error">✗</span>';
            // Parse time as UTC and convert to local timezone
            const time = a.time ? (() => {
                const utcTime = a.time.endsWith('Z') ? a.time : a.time + 'Z';
                return new Date(utcTime).toLocaleString();
            })() : (a.timestamp ? (() => {
                const utcTime = a.timestamp.endsWith('Z') ? a.timestamp : a.timestamp + 'Z';
                return new Date(utcTime).toLocaleString();
            })() : 'Unknown');
            const responseTime = parseFloat(a.response_time || 0).toFixed(3);
            const taskType = (a.task_type || 'unknown').trim();
            // Show full URL/prompt in tooltip, truncate in cell for display
            const fullUrl = (a.task_url || '').trim();
            const fullPrompt = (a.task_prompt || '').trim();
            // Show more characters for URL and prompt in the table
            const url = fullUrl.length > 100 ? fullUrl.substring(0, 100) + '...' : fullUrl;
            const prompt = fullPrompt.length > 150 ? fullPrompt.substring(0, 150) + '...' : fullPrompt;
            
            html += `<tr>
                <td style="font-size: 11px; white-space: nowrap;">${time}</td>
                <td><code style="font-size: 11px;">${a.ip || 'unknown'}</code></td>
                <td style="text-align: center;">${badge}</td>
                <td style="text-align: right; color: ${responseTime < 1 ? 'var(--accent-success)' : responseTime < 3 ? 'var(--accent-warning)' : 'var(--accent-error)'}">${responseTime}s</td>
                <td><code style="font-size: 11px;">${taskType}</code></td>
                <td style="font-size: 11px; max-width: 300px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" title="${fullUrl || '-'}">${url || '-'}</td>
                <td style="font-size: 11px; max-width: 400px; overflow: hidden; text-overflow: ellipsis;" title="${fullPrompt || '-'}">${prompt || '-'}</td>
            </tr>`;
        });
        html += '</tbody></table>';
        logElement.innerHTML = html;
    } else {
        logElement.innerHTML = '<div style="padding:20px;text-align:center;color:var(--text-tertiary)">No validator interactions found' + (searchTerm || filterType !== 'all' ? ' (filtered)' : '') + '</div>';
    }
}

// Historical data loading - kept for manual use (endpoint is still available),
// but no longer wired into the UI now that the Complete Historical Data section is removed.
window.loadHistoricalData = async function loadHistoricalData() {
    console.log('Loading historical data...');
    const btn = document.getElementById('load-history-btn');
    const container = document.getElementById('historical-data');
    
    if (!container) {
        console.error('Historical data container not found!');
        return;
    }
    
    if (btn) {
        btn.disabled = true;
        btn.textContent = 'Loading...';
    }
    
    container.innerHTML = '<p style="color: var(--text-secondary);">Loading historical data... This may take a moment.</p>';
    
    try {
        console.log('Fetching /api/dashboard/history...');
        const controller = new AbortController();
        // Historical logs can be heavy – give this plenty of time (45s)
        const timeoutId = setTimeout(() => controller.abort(), 45000);
        
        const response = await fetch('/api/dashboard/history', {
            signal: controller.signal,
            headers: { 'Accept': 'application/json' }
        });
        
        clearTimeout(timeoutId);
        
        console.log('Response status:', response.status);
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error('Error response:', errorText);
            throw new Error(`HTTP ${response.status}: ${response.statusText} - ${errorText}`);
        }
        
        const data = await response.json();
        console.log('Historical data received:', data);
        
        if (container) {
            const summary = data.summary || {};
            const interactions = data.validator_interactions || [];
            
            let html = `
                <div style="margin-bottom: 20px;">
                    <h3 style="color: var(--text-primary); margin-bottom: 10px;">Summary</h3>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 20px;">
                        <div style="padding: 15px; background: var(--bg-secondary); border-radius: 8px;">
                            <div style="color: var(--text-secondary); font-size: 12px;">Total Interactions</div>
                            <div style="color: var(--accent-primary); font-size: 24px; font-weight: bold;">${summary.total_interactions || 0}</div>
                        </div>
                        <div style="padding: 15px; background: var(--bg-secondary); border-radius: 8px;">
                            <div style="color: var(--text-secondary); font-size: 12px;">Unique Validators</div>
                            <div style="color: var(--accent-primary); font-size: 24px; font-weight: bold;">${summary.unique_validators || 0}</div>
                        </div>
                        <div style="padding: 15px; background: var(--bg-secondary); border-radius: 8px;">
                            <div style="color: var(--text-secondary); font-size: 12px;">Successful</div>
                            <div style="color: var(--accent-success); font-size: 24px; font-weight: bold;">${summary.successful_interactions || 0}</div>
                        </div>
                        <div style="padding: 15px; background: var(--bg-secondary); border-radius: 8px;">
                            <div style="color: var(--text-secondary); font-size: 12px;">Failed</div>
                            <div style="color: var(--accent-error); font-size: 24px; font-weight: bold;">${summary.failed_interactions || 0}</div>
                        </div>
                    </div>
                    ${summary.first_interaction ? `<div style="color: var(--text-secondary); font-size: 12px; margin-bottom: 5px;">First Interaction: ${(() => { const t = summary.first_interaction.endsWith('Z') ? summary.first_interaction : summary.first_interaction + 'Z'; return new Date(t).toLocaleString(); })()}</div>` : ''}
                    ${summary.last_interaction ? `<div style="color: var(--text-secondary); font-size: 12px;">Last Interaction: ${(() => { const t = summary.last_interaction.endsWith('Z') ? summary.last_interaction : summary.last_interaction + 'Z'; return new Date(t).toLocaleString(); })()}</div>` : ''}
                </div>
            `;
            
            if (interactions.length > 0) {
                html += `
                    <h3 style="color: var(--text-primary); margin-bottom: 10px;">All Validator Interactions (${interactions.length} total) - Scroll to see all</h3>
                    <div style="max-height: 800px; overflow-y: auto; border: 1px solid var(--border-color); border-radius: 8px; background: var(--bg-primary);">
                        <table style="width: 100%; border-collapse: collapse;">
                            <thead style="position: sticky; top: 0; background: var(--bg-secondary); z-index: 10;">
                                <tr style="border-bottom: 2px solid var(--border-color);">
                                    <th style="padding: 12px; text-align: left; color: var(--text-primary); font-weight: 600; border-right: 1px solid var(--border-color);">Time</th>
                                    <th style="padding: 12px; text-align: left; color: var(--text-primary); font-weight: 600; border-right: 1px solid var(--border-color);">Validator IP</th>
                                    <th style="padding: 12px; text-align: center; color: var(--text-primary); font-weight: 600; border-right: 1px solid var(--border-color);">Status</th>
                                    <th style="padding: 12px; text-align: right; color: var(--text-primary); font-weight: 600; border-right: 1px solid var(--border-color);">Response Time</th>
                                    <th style="padding: 12px; text-align: left; color: var(--text-primary); font-weight: 600;">Task Type</th>
                                </tr>
                            </thead>
                            <tbody>
                `;
                
                // Process ALL interactions - no limit
                interactions.forEach((interaction, index) => {
                    const isSuccess = interaction.success;
                    const badge = isSuccess ? '<span style="background: var(--accent-success); color: white; padding: 2px 8px; border-radius: 4px; font-size: 11px;">✓ Success</span>' : '<span style="background: var(--accent-error); color: white; padding: 2px 8px; border-radius: 4px; font-size: 11px;">✗ Failed</span>';
                    // Parse time as UTC and convert to local timezone
                    const timeStr = interaction.time || interaction.timestamp;
                    const time = timeStr ? (() => {
                        const utcTime = timeStr.endsWith('Z') ? timeStr : timeStr + 'Z';
                        return new Date(utcTime).toLocaleString();
                    })() : 'Unknown';
                    const responseTime = interaction.response_time ? `${interaction.response_time.toFixed(3)}s` : '-';
                    const taskType = interaction.task_type || '-';
                    
                    html += `
                        <tr style="border-bottom: 1px solid var(--border-color); ${index % 2 === 0 ? 'background: var(--bg-primary);' : 'background: var(--bg-secondary);'}">
                            <td style="padding: 10px; color: var(--text-secondary); font-size: 12px; border-right: 1px solid var(--border-color); white-space: nowrap;">${time}</td>
                            <td style="padding: 10px; border-right: 1px solid var(--border-color);"><code style="color: var(--accent-primary); font-size: 11px;">${interaction.ip}</code></td>
                            <td style="padding: 10px; text-align: center; border-right: 1px solid var(--border-color);">${badge}</td>
                            <td style="padding: 10px; text-align: right; color: var(--text-secondary); font-size: 12px; border-right: 1px solid var(--border-color);">${responseTime}</td>
                            <td style="padding: 10px; color: var(--text-secondary); font-size: 12px;"><code style="font-size: 11px;">${taskType}</code></td>
                        </tr>
                    `;
                });
                
                html += `
                            </tbody>
                        </table>
                        <div style="padding: 10px; text-align: center; color: var(--text-secondary); font-size: 12px; border-top: 1px solid var(--border-color); background: var(--bg-secondary);">
                            Showing all ${interactions.length} interactions. Scroll up to see more.
                        </div>
                    </div>
                `;
            } else {
                html += '<p style="color: var(--text-secondary); padding: 20px; text-align: center;">No historical validator interactions found.</p>';
            }
            
            container.innerHTML = html;
        }
        
        if (btn) {
            btn.disabled = false;
            btn.textContent = 'Load All History';
        }
    } catch (error) {
        console.error('Error loading historical data:', error);
        if (container) {
            if (error.name === 'AbortError') {
                container.innerHTML = `<p style="color: var(--accent-error);">Historical data request took too long and was cancelled. The log history is large – try again, or wait a bit between refreshes.</p>`;
            } else {
                container.innerHTML = `<p style="color: var(--accent-error);">Error loading historical data: ${error.message}</p><p style="color: var(--text-secondary); font-size: 12px; margin-top: 10px;">Check browser console (F12) for details.</p>`;
            }
        }
        if (btn) {
            btn.disabled = false;
            btn.textContent = 'Load All History';
        }
    }
};

// Reward history loading - on-chain via btcli wallet history
window.loadRewardsHistory = async function loadRewardsHistory() {
    console.log('Loading reward history...');
    const btn = document.getElementById('load-rewards-btn');
    const container = document.getElementById('rewards-history');

    if (!container) {
        console.error('Rewards history container not found!');
        return;
    }

    if (btn) {
        btn.disabled = true;
        btn.textContent = 'Loading...';
    }

    container.innerHTML = '<p style="color: var(--text-secondary);">Loading on-chain wallet history via <code>btcli wallet history</code>...</p>';

    try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 15000); // 15 second timeout

        const response = await fetch('/api/dashboard/rewards_history', {
            signal: controller.signal,
            headers: { 'Accept': 'application/json' }
        });

        clearTimeout(timeoutId);

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`HTTP ${response.status}: ${response.statusText} - ${errorText}`);
        }

        const data = await response.json();

        if (data.error) {
            container.innerHTML = `
                <p style="color: var(--accent-error);">Error loading reward history: ${data.error}</p>
                ${data.history_raw ? `<pre style="margin-top:10px; padding:10px; background: var(--bg-secondary); border-radius: 6px; color: var(--text-secondary); font-size: 11px; white-space: pre-wrap; max-height: 400px; overflow-y: auto;">${data.history_raw}</pre>` : ''}
            `;
        } else {
            const historyRaw = (data.history_raw || '').trim();
            const entries = Array.isArray(data.entries) ? data.entries : [];

            // If we have parsed entries, show a nice table; otherwise fall back to raw text
            if (entries.length > 0) {
                let totalIn = 0;
                let totalOut = 0;

                entries.forEach(e => {
                    const amt = typeof e.amount_tao === 'number' ? e.amount_tao : null;
                    if (amt !== null) {
                        if (e.direction === 'in') totalIn += amt;
                        else if (e.direction === 'out') totalOut += Math.abs(amt);
                    }
                });

                let html = `
                    <div style="margin-bottom: 12px;">
                        <p style="color: var(--text-secondary); font-size: 12px; margin-bottom: 4px;">
                            Wallet: <code>${data.wallet_name || 'default'}</code> – Parsed on-chain history from <code>btcli wallet history</code>.
                        </p>
                        <p style="color: var(--text-secondary); font-size: 12px; margin-bottom: 4px;">
                            Total reward-like entries detected: <strong>${entries.length}</strong>
                        </p>
                        <p style="color: var(--text-secondary); font-size: 12px;">
                            Estimated received: <span style="color: var(--accent-success); font-weight: 600;">${totalIn.toFixed(6)} TAO</span>
                            ${totalOut > 0 ? ` | Estimated sent/staked: <span style="color: var(--accent-error); font-weight: 600;">${totalOut.toFixed(6)} TAO</span>` : ''}
                        </p>
                    </div>
                    <div style="max-height: 400px; overflow-y: auto; border: 1px solid var(--border-color); border-radius: 8px; background: var(--bg-primary);">
                        <table style="width: 100%; border-collapse: collapse;">
                            <thead style="position: sticky; top: 0; background: var(--bg-secondary); z-index: 10;">
                                <tr style="border-bottom: 2px solid var(--border-color);">
                                    <th style="padding: 10px; text-align: left; color: var(--text-primary); font-weight: 600; border-right: 1px solid var(--border-color);">Time</th>
                                    <th style="padding: 10px; text-align: right; color: var(--text-primary); font-weight: 600; border-right: 1px solid var(--border-color);">Amount (TAO)</th>
                                    <th style="padding: 10px; text-align: center; color: var(--text-primary); font-weight: 600; border-right: 1px solid var(--border-color);">Direction</th>
                                    <th style="padding: 10px; text-align: left; color: var(--text-primary); font-weight: 600;">Raw</th>
                                </tr>
                            </thead>
                            <tbody>
                `;

                entries.forEach((e, index) => {
                    const ts = e.timestamp || '';
                    const time = ts
                        ? (() => {
                              const t = ts.endsWith('Z') ? ts : ts + 'Z';
                              return new Date(t).toLocaleString();
                          })()
                        : 'Unknown';
                    const amt = typeof e.amount_tao === 'number' ? e.amount_tao : null;
                    const amtStr = amt !== null ? amt.toFixed(6) : '-';
                    let dirLabel = 'Unknown';
                    let dirColor = 'var(--text-secondary)';
                    if (e.direction === 'in') {
                        dirLabel = 'In';
                        dirColor = 'var(--accent-success)';
                    } else if (e.direction === 'out') {
                        dirLabel = 'Out';
                        dirColor = 'var(--accent-error)';
                    }

                    html += `
                        <tr style="border-bottom: 1px solid var(--border-color); ${index % 2 === 0 ? 'background: var(--bg-primary);' : 'background: var(--bg-secondary);'}">
                            <td style="padding: 8px; color: var(--text-secondary); font-size: 12px; border-right: 1px solid var(--border-color); white-space: nowrap;">${time}</td>
                            <td style="padding: 8px; text-align: right; color: var(--text-primary); font-size: 12px; border-right: 1px solid var(--border-color);">${amtStr}</td>
                            <td style="padding: 8px; text-align: center; color: ${dirColor}; font-size: 12px; border-right: 1px solid var(--border-color);">${dirLabel}</td>
                            <td style="padding: 8px; color: var(--text-secondary); font-size: 11px;">${(e.raw || '').replace(/</g, '&lt;').replace(/>/g, '&gt;')}</td>
                        </tr>
                    `;
                });

                html += `
                            </tbody>
                        </table>
                    </div>
                `;

                // Optional: show raw history collapsed below if you want
                if (historyRaw) {
                    html += `
                        <details style="margin-top: 10px;">
                            <summary style="color: var(--text-secondary); font-size: 12px; cursor: pointer;">Show raw btcli output</summary>
                            <pre style="margin-top:8px; padding:10px; background: var(--bg-secondary); border-radius: 6px; color: var(--text-secondary); font-size: 11px; white-space: pre-wrap; max-height: 300px; overflow-y: auto;">${historyRaw}</pre>
                        </details>
                    `;
                }

                container.innerHTML = html;
            } else {
                // No parsed entries—fall back to raw text view if available
                if (historyRaw) {
                    container.innerHTML = `
                        <p style="color: var(--text-secondary); font-size: 12px; margin-bottom: 8px;">
                            Wallet: <code>${data.wallet_name || 'default'}</code> – Raw on-chain history from <code>btcli wallet history</code>.
                        </p>
                        <div style="max-height: 400px; overflow-y: auto; border: 1px solid var(--border-color); border-radius: 8px; background: var(--bg-primary);">
                            <pre style="margin: 0; padding: 12px; color: var(--text-secondary); font-size: 11px; white-space: pre-wrap;">${historyRaw}</pre>
                        </div>
                    `;
                } else {
                    container.innerHTML = '<p style="color: var(--text-secondary);">No wallet history found from btcli.</p>';
                }
            }
        }

        if (btn) {
            btn.disabled = false;
            btn.textContent = 'Load Reward History';
        }
    } catch (error) {
        console.error('Error loading reward history:', error);
        container.innerHTML = `<p style="color: var(--accent-error);">Error loading reward history: ${error.message}</p>`;
        if (btn) {
            btn.disabled = false;
            btn.textContent = 'Load Reward History';
        }
    }
};

// Real-time activity feed
let requestsToday = 0;
let lastRequestTime = null;

function updateLiveActivityFeed(data) {
    const lastRequestTimeEl = document.getElementById('live-last-request-time');
    const requestsTodayEl = document.getElementById('live-requests-today');
    const liveAvgResponseEl = document.getElementById('live-avg-response');
    const liveSuccessRateEl = document.getElementById('live-success-rate');
    
    // Get recent activity
    const recentActivity = data.validators?.recent_activity || [];
    const allActivity = data.validators?.all_activity || [];
    
    // Update system status
    if (recentActivity.length > 0) {
        const latest = recentActivity[0];
        if (latest.time) {
            const time = new Date(latest.time);
            const now = new Date();
            const diffMs = now - time;
            const diffMins = Math.floor(diffMs / 60000);
            const diffSecs = Math.floor((diffMs % 60000) / 1000);
            
            if (lastRequestTimeEl) {
                if (diffMins > 0) {
                    lastRequestTimeEl.textContent = `${diffMins}m ${diffSecs}s ago`;
                    lastRequestTimeEl.style.color = diffMins > 5 ? '#ef4444' : '#10b981';
                } else {
                    lastRequestTimeEl.textContent = `${diffSecs}s ago`;
                    lastRequestTimeEl.style.color = '#10b981';
                }
            }
            lastRequestTime = time;
        }
        
        // Count requests today
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        requestsToday = allActivity.filter(a => {
            if (!a.time) return false;
            const activityDate = new Date(a.time);
            return activityDate >= today;
        }).length;
        if (requestsTodayEl) requestsTodayEl.textContent = requestsToday;
    } else {
        if (lastRequestTimeEl) lastRequestTimeEl.textContent = 'Never';
        if (requestsTodayEl) requestsTodayEl.textContent = '0';
    }
    
    // Update performance metrics
    const perf = data.performance || {};
    if (liveAvgResponseEl) {
        const avgTime = parseFloat(perf.avg_response_time || 0);
        if (avgTime > 0) {
            liveAvgResponseEl.textContent = `${avgTime.toFixed(3)}s`;
            liveAvgResponseEl.style.color = avgTime < 1 ? '#10b981' : avgTime < 3 ? '#f59e0b' : '#ef4444';
        } else {
            liveAvgResponseEl.textContent = '-';
        }
    }
    
    const overview = data.overview || {};
    if (liveSuccessRateEl) {
        const successRate = parseFloat(overview.success_rate || 0);
        if (successRate > 0) {
            liveSuccessRateEl.textContent = `${successRate.toFixed(1)}%`;
            liveSuccessRateEl.style.color = successRate >= 90 ? '#10b981' : successRate >= 70 ? '#f59e0b' : '#ef4444';
        } else {
            liveSuccessRateEl.textContent = '-';
        }
    }
}

// Start
window.addEventListener('load', () => {
    loadMetrics();
    // Poll every 5 seconds for updates (lighter on browser and server)
    setInterval(loadMetrics, 5000);
    
    // Add event listeners for search and filter
    const searchInput = document.getElementById('log-search');
    const filterSelect = document.getElementById('log-filter');
    
    if (searchInput) {
        searchInput.addEventListener('input', () => {
            // Re-render log when search changes
            const data = window.lastMetricsData;
            if (data) {
                updateValidatorLog(data.validators?.all_activity || []);
            }
        });
    }
    
    if (filterSelect) {
        filterSelect.addEventListener('change', () => {
            // Re-render log when filter changes
            const data = window.lastMetricsData;
            if (data) {
                updateValidatorLog(data.validators?.all_activity || []);
            }
        });
    }
    
    // Live monitoring removed - using only Validator Interactions table
});

// LIVE MONITORING: Server-Sent Events for real-time updates
let liveEventSource = null;
let liveEvents = [];
let activeTasks = {};

function initLiveMonitoring() {
    const indicator = document.getElementById('live-status-indicator');
    const text = document.getElementById('live-status-text');
    if (!indicator || !text) return; // Live monitoring section not present
    
    // Try to connect to SSE stream
    if (typeof EventSource !== 'undefined') {
        try {
            liveEventSource = new EventSource('/api/dashboard/live');
            
            liveEventSource.onopen = function() {
                indicator.style.background = '#10b981';
                text.textContent = 'Connected';
                console.log('✅ Live monitoring connected');
            };
            
            liveEventSource.onerror = function() {
                // SSE failed, fallback to polling (which is still "LIVE")
                console.log('SSE not available, using polling mode');
                liveEventSource.close();
                initLiveMonitoringPolling();
            };
            
            liveEventSource.onmessage = function(event) {
                try {
                    const data = JSON.parse(event.data);
                    handleLiveEvent(data);
                } catch (e) {
                    console.error('Error parsing live event:', e);
                }
            };
        } catch (e) {
            console.log('SSE not available, using polling mode:', e);
            // Fallback to polling (which is still "LIVE")
            initLiveMonitoringPolling();
        }
    } else {
        // Browser doesn't support SSE, use polling
        initLiveMonitoringPolling();
    }
}

function initLiveMonitoringPolling() {
    const indicator = document.getElementById('live-status-indicator');
    const text = document.getElementById('live-status-text');
    if (!indicator || !text) return;
    
    // Polling mode - still "LIVE" since we're getting real-time updates
    indicator.style.background = '#10b981';  // Green - polling is working
    text.textContent = 'LIVE';
    text.style.color = '#10b981';
    
    // Poll every 2 seconds (matches dashboard refresh rate)
    setInterval(async () => {
        try {
            // The metrics endpoint already provides all the data we need
            // No need for a separate live status endpoint
            const response = await fetch('/api/dashboard/metrics');
            if (response.ok) {
                const data = await response.json();
                // Update live activity feed with latest data
                updateLiveActivityFeed(data);
            }
        } catch (e) {
            console.error('Error polling live status:', e);
            // On error, show disconnected state
            if (indicator) indicator.style.background = '#ef4444';
            if (text) {
                text.textContent = 'Disconnected';
                text.style.color = '#ef4444';
            }
        }
    }, 2000);
}

function handleLiveEvent(data) {
    if (data.type === 'status') {
        handleLiveStatus(data.data);
    } else if (data.type === 'event') {
        handleLiveEventData(data.data);
    } else if (data.type === 'error') {
        console.error('Live stream error:', data.message);
    }
}

function handleLiveStatus(status) {
    // Update active tasks
    activeTasks = status.active_tasks || {};
    updateActiveTasksDisplay();
    
    // Update recent events
    if (status.recent_events) {
        liveEvents = status.recent_events.slice(-50); // Keep last 50
        updateEventsDisplay();
    }
}

function handleLiveEventData(event) {
    // Add new event to list
    liveEvents.push(event);
    if (liveEvents.length > 50) {
        liveEvents.shift(); // Keep only last 50
    }
    updateEventsDisplay();
    
    // Update active tasks if this is a task event
    if (event.task_id) {
        if (event.type === 'task_start') {
            activeTasks[event.task_id] = {
                task_id: event.task_id,
                prompt: event.prompt,
                url: event.url,
                validator_ip: event.validator_ip,
                status: 'processing',
                start_time: event.timestamp
            };
        } else if (event.type === 'task_complete') {
            delete activeTasks[event.task_id];
        } else if (event.type === 'task_step' && activeTasks[event.task_id]) {
            activeTasks[event.task_id].current_step = event.step;
        } else if (event.type === 'actions_generated' && activeTasks[event.task_id]) {
            activeTasks[event.task_id].actions_generated = event.action_count;
        }
        updateActiveTasksDisplay();
    }
}

function updateActiveTasksDisplay() {
    const container = document.getElementById('live-active-tasks');
    if (!container) return;
    
    const taskIds = Object.keys(activeTasks);
    
    if (taskIds.length === 0) {
        container.innerHTML = '<div style="color: #949ba4; padding: 10px;">No active tasks</div>';
        return;
    }
    
    const html = taskIds.map(taskId => {
        const task = activeTasks[taskId];
        const elapsed = task.start_time ? Math.floor((Date.now() / 1000 - task.start_time)) : 0;
        const prompt = (task.prompt || '').substring(0, 50) + (task.prompt && task.prompt.length > 50 ? '...' : '');
        
        return `
            <div style="padding: 8px; border-bottom: 1px solid #2a2e36; color: #ffffff;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                    <strong style="color: #10b981;">${taskId.substring(0, 8)}...</strong>
                    <span style="color: #949ba4; font-size: 11px;">${elapsed}s</span>
                </div>
                <div style="color: #949ba4; font-size: 11px; margin-bottom: 4px;">${prompt}</div>
                <div style="color: #6366f1; font-size: 11px;">
                    ${task.current_step || 'processing'} 
                    ${task.actions_generated ? `(${task.actions_generated} actions)` : ''}
                </div>
                ${task.validator_ip ? `<div style="color: #f59e0b; font-size: 10px; margin-top: 4px;">Validator: ${task.validator_ip}</div>` : ''}
            </div>
        `;
    }).join('');
    
    container.innerHTML = html;
}

function updateEventsDisplay() {
    const container = document.getElementById('live-events');
    if (!container) return;
    
    if (liveEvents.length === 0) {
        container.innerHTML = '<div style="color: #949ba4; padding: 10px;">Waiting for events...</div>';
        return;
    }
    
    const html = liveEvents.slice().reverse().map(event => {
        const time = new Date(event.time_str || event.timestamp * 1000).toLocaleTimeString();
        const emoji = {
            'task_start': '📥',
            'task_complete': event.success ? '✅' : '❌',
            'task_step': '📊',
            'actions_generated': '⚡',
            'validator_connection': '🔗',
            'cache_hit': '💾',
            'error': '❌'
        }[event.type] || '📌';
        
        const color = {
            'task_start': '#10b981',
            'task_complete': event.success ? '#10b981' : '#ef4444',
            'task_step': '#6366f1',
            'actions_generated': '#f59e0b',
            'validator_connection': '#8b5cf6',
            'cache_hit': '#06b6d4',
            'error': '#ef4444'
        }[event.type] || '#949ba4';
        
        return `
            <div style="padding: 6px; border-bottom: 1px solid #2a2e36; color: #ffffff; font-size: 11px;">
                <div style="display: flex; gap: 8px; align-items: center;">
                    <span style="font-size: 14px;">${emoji}</span>
                    <span style="color: ${color}; font-weight: 500;">${event.type}</span>
                    <span style="color: #949ba4; margin-left: auto; font-size: 10px;">${time}</span>
                </div>
                ${event.task_id ? `<div style="color: #949ba4; font-size: 10px; margin-top: 2px; margin-left: 22px;">Task: ${event.task_id.substring(0, 12)}...</div>` : ''}
                ${event.step ? `<div style="color: #6366f1; font-size: 10px; margin-top: 2px; margin-left: 22px;">${event.step}</div>` : ''}
                ${event.action_count !== undefined ? `<div style="color: #f59e0b; font-size: 10px; margin-top: 2px; margin-left: 22px;">${event.action_count} actions</div>` : ''}
                ${event.error_message ? `<div style="color: #ef4444; font-size: 10px; margin-top: 2px; margin-left: 22px;">${event.error_message.substring(0, 60)}...</div>` : ''}
            </div>
        `;
    }).join('');
    
    container.innerHTML = html;
}
