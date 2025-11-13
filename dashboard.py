#!/usr/bin/env python3
"""
Autoppia Miner Analytics Dashboard
Real-time monitoring of miner performance, earnings, and model usage
"""

import os
import json
import asyncio
import re
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, List, Any, Tuple

try:
    from fastapi import FastAPI, WebSocket
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import HTMLResponse, JSONResponse
    import uvicorn
except ImportError:
    print("FastAPI not installed. Installing...")
    os.system("pip install fastapi uvicorn")
    from fastapi import FastAPI, WebSocket
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import HTMLResponse, JSONResponse
    import uvicorn


class MinerAnalytics:
    """Analytics engine for miner performance"""
    
    def __init__(self, log_file: str = "logs/autoppia-miner.log"):
        self.log_file = log_file
        self.metrics = {
            "tasks_completed": 0,
            "tasks_failed": 0,
            "total_tokens_used": 0,
            "model_usage": defaultdict(int),
            "model_success": defaultdict(int),
            "model_failures": defaultdict(int),
            "response_times": [],
            "estimated_cost": 0.0,
            "estimated_savings": 0.0,
            "start_time": datetime.now(),
        }
        self.model_costs = {
            "llama-2-7b": 0.01,
            "llama-2-13b": 0.02,
            "mixtral-8x7b": 0.05,
            "qwen": 0.03,
            "deepseek": 0.04,
            "gpt-4": 1.00,
        }
        self.refresh_metrics()
    
    def refresh_metrics(self):
        """Parse logs and update metrics"""
        if not Path(self.log_file).exists():
            return
        
        try:
            with open(self.log_file, 'r') as f:
                logs = f.readlines()
            
            # Reset counters
            self.metrics["model_usage"] = defaultdict(int)
            self.metrics["model_success"] = defaultdict(int)
            self.metrics["model_failures"] = defaultdict(int)
            self.metrics["response_times"] = []
            self.metrics["tasks_completed"] = 0
            self.metrics["tasks_failed"] = 0
            
            estimated_cost_gpt4 = 0.0
            estimated_cost_routed = 0.0
            
            for line in logs:
                # Track model routing
                if "Task complexity:" in line:
                    match = re.search(r'Using model: (\S+)', line)
                    if match:
                        model = match.group(1)
                        self.metrics["model_usage"][model] += 1
                
                # Track successful tasks
                if "success" in line.lower() and "true" in line.lower():
                    self.metrics["tasks_completed"] += 1
                    # Extract model if present
                    model_match = re.search(r'Using model: (\S+)', line)
                    if model_match:
                        model = model_match.group(1)
                        self.metrics["model_success"][model] += 1
                
                # Track failures
                if "error" in line.lower() or "failed" in line.lower():
                    self.metrics["tasks_failed"] += 1
                
                # Track response times
                if "took" in line.lower() and "ms" in line.lower():
                    time_match = re.search(r'(\d+(?:\.\d+)?)\s*ms', line)
                    if time_match:
                        self.metrics["response_times"].append(float(time_match.group(1)))
            
            # Calculate cost savings
            total_tasks = self.metrics["tasks_completed"]
            
            # Cost if all used GPT-4
            estimated_cost_gpt4 = total_tasks * 1.0
            
            # Cost with routing
            estimated_cost_routed = 0.0
            for model, count in self.metrics["model_usage"].items():
                cost = self.model_costs.get(model, 1.0)
                estimated_cost_routed += count * cost
            
            self.metrics["estimated_cost"] = estimated_cost_routed
            self.metrics["estimated_savings"] = estimated_cost_gpt4 - estimated_cost_routed
        
        except Exception as e:
            print(f"Error parsing logs: {e}")
    
    def get_summary(self) -> Dict[str, Any]:
        """Get current metrics summary"""
        self.refresh_metrics()
        
        total_tasks = self.metrics["tasks_completed"] + self.metrics["tasks_failed"]
        success_rate = (self.metrics["tasks_completed"] / total_tasks * 100) if total_tasks > 0 else 0
        
        avg_response_time = (
            sum(self.metrics["response_times"]) / len(self.metrics["response_times"])
            if self.metrics["response_times"]
            else 0
        )
        
        uptime = datetime.now() - self.metrics["start_time"]
        hours_running = uptime.total_seconds() / 3600
        
        # Estimate daily/monthly based on current pace
        daily_tasks = total_tasks / max(hours_running / 24, 1)
        monthly_tasks = daily_tasks * 30
        
        return {
            "summary": {
                "total_tasks": total_tasks,
                "completed": self.metrics["tasks_completed"],
                "failed": self.metrics["tasks_failed"],
                "success_rate": f"{success_rate:.1f}%",
                "avg_response_time_ms": f"{avg_response_time:.0f}",
                "hours_running": f"{hours_running:.1f}",
            },
            "projections": {
                "estimated_daily_tasks": f"{daily_tasks:.0f}",
                "estimated_monthly_tasks": f"{monthly_tasks:.0f}",
                "estimated_daily_cost": f"${daily_tasks * self.metrics['estimated_cost'] / total_tasks:.2f}" if total_tasks > 0 else "$0",
                "estimated_monthly_cost": f"${monthly_tasks * self.metrics['estimated_cost'] / total_tasks:.2f}" if total_tasks > 0 else "$0",
            },
            "cost_analysis": {
                "actual_cost": f"${self.metrics['estimated_cost']:.2f}",
                "gpt4_cost": f"${total_tasks * 1.0:.2f}",
                "total_savings": f"${self.metrics['estimated_savings']:.2f}",
                "savings_percentage": f"{(self.metrics['estimated_savings'] / (total_tasks * 1.0) * 100):.1f}%" if total_tasks > 0 else "0%",
            },
            "model_breakdown": {
                "usage": dict(self.metrics["model_usage"]),
                "success_rates": dict(self.metrics["model_success"]),
            },
        }


# Initialize FastAPI app
app = FastAPI(title="Autoppia Miner Dashboard")
analytics = MinerAnalytics()


@app.get("/", response_class=HTMLResponse)
async def dashboard():
    """Serve the dashboard HTML"""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Autoppia Miner Dashboard</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: #333;
                min-height: 100vh;
                padding: 20px;
            }
            
            .container {
                max-width: 1400px;
                margin: 0 auto;
            }
            
            header {
                text-align: center;
                color: white;
                margin-bottom: 30px;
            }
            
            header h1 {
                font-size: 2.5em;
                margin-bottom: 10px;
            }
            
            header p {
                font-size: 1.1em;
                opacity: 0.9;
            }
            
            .grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }
            
            .card {
                background: white;
                border-radius: 10px;
                padding: 20px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                transition: transform 0.3s ease;
            }
            
            .card:hover {
                transform: translateY(-5px);
            }
            
            .card-title {
                color: #667eea;
                font-size: 0.9em;
                text-transform: uppercase;
                letter-spacing: 1px;
                margin-bottom: 10px;
                font-weight: 600;
            }
            
            .card-value {
                font-size: 2em;
                font-weight: bold;
                color: #333;
            }
            
            .card-value.success {
                color: #27ae60;
            }
            
            .card-value.warning {
                color: #f39c12;
            }
            
            .card-value.savings {
                color: #e74c3c;
            }
            
            .chart-container {
                background: white;
                border-radius: 10px;
                padding: 20px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                margin-bottom: 30px;
            }
            
            .chart-title {
                color: #667eea;
                font-size: 1.3em;
                font-weight: 600;
                margin-bottom: 20px;
            }
            
            .charts-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }
            
            .refresh-btn {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                padding: 15px 30px;
                border-radius: 5px;
                font-size: 1em;
                cursor: pointer;
                transition: transform 0.2s ease;
                display: block;
                margin: 20px auto;
            }
            
            .refresh-btn:hover {
                transform: scale(1.05);
            }
            
            .status {
                display: inline-block;
                padding: 5px 15px;
                border-radius: 20px;
                font-size: 0.9em;
                font-weight: 600;
                margin-top: 10px;
            }
            
            .status.running {
                background: #d4edda;
                color: #155724;
            }
            
            .status.error {
                background: #f8d7da;
                color: #721c24;
            }
            
            footer {
                text-align: center;
                color: white;
                margin-top: 30px;
                font-size: 0.9em;
            }
            
            .last-updated {
                text-align: center;
                color: white;
                margin-bottom: 20px;
                font-size: 0.95em;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>🚀 Autoppia Miner Dashboard</h1>
                <p>Real-time Analytics & Performance Monitoring</p>
            </header>
            
            <div class="last-updated">
                Last updated: <span id="lastUpdated">--:--:--</span>
            </div>
            
            <!-- Summary Cards -->
            <div class="grid">
                <div class="card">
                    <div class="card-title">Tasks Completed</div>
                    <div class="card-value success" id="tasksCompleted">0</div>
                    <div style="color: #999; font-size: 0.9em; margin-top: 5px;">Success Rate: <span id="successRate">0%</span></div>
                </div>
                
                <div class="card">
                    <div class="card-title">Monthly Projection</div>
                    <div class="card-value" id="monthlyTasks">0</div>
                    <div style="color: #999; font-size: 0.9em; margin-top: 5px;">Tasks/Month</div>
                </div>
                
                <div class="card">
                    <div class="card-title">💰 Total Savings</div>
                    <div class="card-value savings" id="totalSavings">$0.00</div>
                    <div style="color: #999; font-size: 0.9em; margin-top: 5px;">vs GPT-4 Only</div>
                </div>
                
                <div class="card">
                    <div class="card-title">Monthly Cost Projection</div>
                    <div class="card-value" id="monthlyCost">$0.00</div>
                    <div style="color: #999; font-size: 0.9em; margin-top: 5px;">Actual | <span id="gpt4Cost">$0.00</span> GPT-4</div>
                </div>
                
                <div class="card">
                    <div class="card-title">Avg Response Time</div>
                    <div class="card-value" id="avgResponseTime">0ms</div>
                    <div style="color: #999; font-size: 0.9em; margin-top: 5px;">Performance</div>
                </div>
                
                <div class="card">
                    <div class="card-title">Uptime</div>
                    <div class="card-value" id="uptime">0h</div>
                    <div style="color: #999; font-size: 0.9em; margin-top: 5px;">Running</div>
                </div>
            </div>
            
            <!-- Charts -->
            <div class="charts-grid">
                <div class="chart-container">
                    <div class="chart-title">📊 Model Usage Distribution</div>
                    <canvas id="modelUsageChart"></canvas>
                </div>
                
                <div class="chart-container">
                    <div class="chart-title">✅ Success Rate by Model</div>
                    <canvas id="successRateChart"></canvas>
                </div>
            </div>
            
            <!-- Detailed Stats -->
            <div class="chart-container">
                <div class="chart-title">📈 Performance Breakdown</div>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px;">
                    <div>
                        <strong style="color: #667eea;">Task Statistics</strong>
                        <div id="taskStats" style="margin-top: 10px; line-height: 1.8;">
                            <!-- Populated by JS -->
                        </div>
                    </div>
                    <div>
                        <strong style="color: #667eea;">Cost Analysis</strong>
                        <div id="costStats" style="margin-top: 10px; line-height: 1.8;">
                            <!-- Populated by JS -->
                        </div>
                    </div>
                </div>
            </div>
            
            <button class="refresh-btn" onclick="fetchData()">🔄 Refresh Now</button>
            
            <footer>
                <p>✨ Smart model routing saving you money while maintaining quality ✨</p>
                <p style="margin-top: 10px; font-size: 0.85em;">Dashboard updates automatically every 10 seconds</p>
            </footer>
        </div>
        
        <script>
            let modelUsageChart = null;
            let successRateChart = null;
            
            async function fetchData() {
                try {
                    const response = await fetch('/api/metrics');
                    const data = await response.json();
                    updateDashboard(data);
                } catch (error) {
                    console.error('Error fetching data:', error);
                }
            }
            
            function updateDashboard(data) {
                const summary = data.summary;
                const projections = data.projections;
                const costs = data.cost_analysis;
                const models = data.model_breakdown;
                
                // Update summary cards
                document.getElementById('tasksCompleted').textContent = summary.total_tasks;
                document.getElementById('successRate').textContent = summary.success_rate;
                document.getElementById('monthlyTasks').textContent = projections.estimated_monthly_tasks;
                document.getElementById('monthlyCost').textContent = projections.estimated_monthly_cost;
                document.getElementById('gpt4Cost').textContent = (parseFloat(projections.estimated_monthly_cost) * 10).toFixed(2);
                document.getElementById('totalSavings').textContent = costs.total_savings;
                document.getElementById('avgResponseTime').textContent = summary.avg_response_time_ms;
                document.getElementById('uptime').textContent = summary.hours_running;
                document.getElementById('lastUpdated').textContent = new Date().toLocaleTimeString();
                
                // Update task stats
                const taskStats = `
                    <div>Total Tasks: <strong>${summary.total_tasks}</strong></div>
                    <div>Completed: <strong style="color: #27ae60;">${summary.completed}</strong></div>
                    <div>Failed: <strong style="color: #e74c3c;">${summary.failed}</strong></div>
                    <div>Success Rate: <strong style="color: #667eea;">${summary.success_rate}</strong></div>
                `;
                document.getElementById('taskStats').innerHTML = taskStats;
                
                // Update cost stats
                const costStats = `
                    <div>Actual Cost: <strong style="color: #e74c3c;">${costs.actual_cost}</strong></div>
                    <div>GPT-4 Only: <strong style="color: #f39c12;">${costs.gpt4_cost}</strong></div>
                    <div>Total Savings: <strong style="color: #27ae60;">${costs.total_savings}</strong></div>
                    <div>Savings %: <strong style="color: #667eea;">${costs.savings_percentage}</strong></div>
                `;
                document.getElementById('costStats').innerHTML = costStats;
                
                // Update charts
                updateModelUsageChart(models.usage);
                updateSuccessRateChart(models.success_rates);
            }
            
            function updateModelUsageChart(usage) {
                const ctx = document.getElementById('modelUsageChart').getContext('2d');
                const labels = Object.keys(usage);
                const data = Object.values(usage);
                const colors = [
                    '#667eea', '#764ba2', '#f093fb', '#4facfe',
                    '#00f2fe', '#43e97b', '#fa709a', '#fee140'
                ];
                
                if (modelUsageChart) {
                    modelUsageChart.destroy();
                }
                
                modelUsageChart = new Chart(ctx, {
                    type: 'doughnut',
                    data: {
                        labels: labels,
                        datasets: [{
                            data: data,
                            backgroundColor: colors.slice(0, labels.length),
                            borderColor: '#fff',
                            borderWidth: 2
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            legend: {
                                position: 'bottom'
                            }
                        }
                    }
                });
            }
            
            function updateSuccessRateChart(successRates) {
                const ctx = document.getElementById('successRateChart').getContext('2d');
                const labels = Object.keys(successRates);
                const data = Object.values(successRates);
                const colors = [
                    '#27ae60', '#2ecc71', '#3498db', '#9b59b6',
                    '#e74c3c', '#f39c12', '#1abc9c', '#34495e'
                ];
                
                if (successRateChart) {
                    successRateChart.destroy();
                }
                
                successRateChart = new Chart(ctx, {
                    type: 'bar',
                    data: {
                        labels: labels,
                        datasets: [{
                            label: 'Successful Tasks',
                            data: data,
                            backgroundColor: colors.slice(0, labels.length),
                            borderColor: '#fff',
                            borderWidth: 1
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            legend: {
                                display: false
                            }
                        },
                        scales: {
                            y: {
                                beginAtZero: true
                            }
                        }
                    }
                });
            }
            
            // Fetch data on load
            fetchData();
            
            // Auto-refresh every 10 seconds
            setInterval(fetchData, 10000);
        </script>
    </body>
    </html>
    """


@app.get("/api/metrics")
async def get_metrics():
    """Get current metrics"""
    summary = analytics.get_summary()
    return JSONResponse(summary)


@app.get("/api/live-logs")
async def get_live_logs():
    """Get recent logs"""
    try:
        with open(analytics.log_file, 'r') as f:
            lines = f.readlines()
        
        # Get last 50 lines
        recent = lines[-50:] if len(lines) > 50 else lines
        
        # Extract relevant info
        task_logs = []
        for line in recent:
            if any(keyword in line for keyword in ['complexity', 'success', 'error', 'task']):
                task_logs.append({
                    'timestamp': datetime.now().isoformat(),
                    'message': line.strip()
                })
        
        return JSONResponse({'logs': task_logs})
    except Exception as e:
        return JSONResponse({'error': str(e)}, status_code=500)


def main():
    """Run the dashboard server"""
    port = int(os.getenv("DASHBOARD_PORT", 8090))
    
    print(f"""
    ╔════════════════════════════════════════════════════════════╗
    ║                                                            ║
    ║        🚀 AUTOPPIA MINER ANALYTICS DASHBOARD               ║
    ║                                                            ║
    ║  📊 Dashboard: http://localhost:{port}
    ║  📡 API: http://localhost:{port}/api/metrics
    ║                                                            ║
    ║  Monitor your miner performance in real-time!             ║
    ║                                                            ║
    ╚════════════════════════════════════════════════════════════╝
    """)
    
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")


if __name__ == "__main__":
    main()

