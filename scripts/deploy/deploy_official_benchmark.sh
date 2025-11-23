#!/bin/bash

# Deploy Official Autoppia IWA Benchmark Framework
# This sets up the complete benchmark environment for testing miners

set -e

echo "🚀 Deploying Official Autoppia IWA Benchmark Framework..."

# Configuration
REMOTE_HOST="134.199.203.133"
REMOTE_USER="root"
MINER_URL="https://134.199.203.133:8443"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}📋 Configuration:${NC}"
echo "  Remote Host: $REMOTE_HOST"
echo "  Miner URL: $MINER_URL"
echo ""

# Check if we're running from the correct directory
if [ ! -f "requirements.txt" ]; then
    echo -e "${RED}❌ Error: Must run from autoppia-miner root directory${NC}"
    exit 1
fi

echo -e "${YELLOW}📦 Step 1: Copying benchmark repository to remote server...${NC}"

# Create benchmark directory on remote server
ssh -o StrictHostKeyChecking=no $REMOTE_USER@$REMOTE_HOST << EOF
    mkdir -p /opt/autoppia-benchmark
    cd /opt/autoppia-benchmark
    echo "Created benchmark directory"
EOF

# Copy the official repository
echo "Copying official autoppia_iwa repository..."
rsync -avz --exclude='.git' ../official_autoppia_repo/ $REMOTE_USER@$REMOTE_HOST:/opt/autoppia-benchmark/

echo -e "${GREEN}✅ Repository copied successfully${NC}"

echo -e "${YELLOW}📦 Step 2: Setting up Python environment on remote server...${NC}"

# Setup Python environment remotely
ssh -o StrictHostKeyChecking=no $REMOTE_USER@$REMOTE_HOST << EOF
    cd /opt/autoppia-benchmark

    # Install system dependencies
    apt update
    apt install -y python3-pip python3-venv curl

    # Create virtual environment
    python3 -m venv benchmark_env
    source benchmark_env/bin/activate

    # Upgrade pip
    pip install --upgrade pip

    echo "Python environment created"
EOF

echo -e "${GREEN}✅ Python environment setup complete${NC}"

echo -e "${YELLOW}📦 Step 3: Installing benchmark dependencies...${NC}"

# Install dependencies remotely
ssh -o StrictHostKeyChecking=no $REMOTE_USER@$REMOTE_HOST << EOF
    cd /opt/autoppia-benchmark
    source benchmark_env/bin/activate

    # Install autoppia_iwa_module dependencies
    cd autoppia_iwa_module
    pip install -e .

    # Install additional requirements if any
    if [ -f requirements.txt ]; then
        pip install -r requirements.txt
    fi

    # Install playwright browsers
    playwright install chromium

    echo "Dependencies installed"
EOF

echo -e "${GREEN}✅ Dependencies installed${NC}"

echo -e "${YELLOW}📦 Step 4: Setting up demo web applications...${NC}"

# Setup demo webs remotely
ssh -o StrictHostKeyChecking=no $REMOTE_USER@$REMOTE_HOST << EOF
    cd /opt/autoppia-benchmark/autoppia_iwa_module/modules/webs_demo/scripts

    # Make script executable and run it
    chmod +x setup.sh

    # Run the setup script (this will install Docker if needed)
    ./setup.sh

    echo "Demo web applications setup initiated"
EOF

echo -e "${GREEN}✅ Demo web applications setup initiated${NC}"

echo -e "${YELLOW}📦 Step 5: Creating benchmark configuration...${NC}"

# Create benchmark configuration file
cat > /tmp/benchmark_config.py << 'EOF'
#!/usr/bin/env python3
"""
Official Benchmark Configuration for Autoppia Miner
Tests the miner at https://134.199.203.133:8443 against demo web applications
"""

import asyncio
from loguru import logger

from autoppia_iwa.entrypoints.benchmark.benchmark import Benchmark
from autoppia_iwa.entrypoints.benchmark.config import BenchmarkConfig
from autoppia_iwa.entrypoints.benchmark.task_generation import get_projects_by_ids
from autoppia_iwa.src.demo_webs.config import demo_web_projects
from autoppia_iwa.src.web_agents.apified_agent import ApifiedWebAgent

# =========================
# 💡 Code configuration
# =========================

# 1) Agents (our miner)
AGENTS = [
    ApifiedWebAgent(
        id="autoppia-miner-001",
        name="AutoppiaMiner_Prod",
        base_url="https://134.199.203.133:8443",
        timeout=120
    ),
]

# 2) Projects to evaluate (demo web applications)
PROJECT_IDS = [
    "autoconnect",  # Start with one project for testing
    # "autocinema",
    # "autobooks",
    # "autowork",
]

PROJECTS = get_projects_by_ids(demo_web_projects, PROJECT_IDS)

# 3) Benchmark parameters
CFG = BenchmarkConfig(
    projects=PROJECTS,
    agents=AGENTS,
    # Tasks
    use_cached_tasks=False,  # Generate fresh tasks
    prompts_per_use_case=2,  # 2 tasks per use case
    num_use_cases=3,         # 3 use cases per project
    # Execution
    runs=3,                  # 3 runs for statistical significance
    max_parallel_agent_calls=1,  # Sequential execution
    use_cached_solutions=False,  # Always call our miner
    record_gif=False,        # No GIFs for production testing
    # Dynamic HTML
    enable_dynamic_html=True,  # Enable dynamic content
    # Persistence
    save_results_json=True,   # Save detailed results
    plot_results=False,       # No plots needed
)

def main():
    """
    Main entrypoint for the official benchmark.
    """
    try:
        logger.info("🚀 Starting Official Autoppia Miner Benchmark")
        logger.info(f"Configuration: {len(CFG.projects)} projects, {len(CFG.agents)} agents, {CFG.runs} runs")

        # Validate configuration
        if not CFG.projects:
            logger.error("No valid projects - check demo webs are running")
            return

        if not CFG.agents:
            logger.error("No agents configured")
            return

        logger.info("Configuration validated ✓")

        # Create and run benchmark
        benchmark = Benchmark(CFG)
        results = asyncio.run(benchmark.run())

        logger.info("🎯 Official Benchmark Complete!")
        logger.info("Results saved to: results/benchmark_results_*.json")

        # Print summary
        print("\n" + "="*60)
        print("📊 OFFICIAL BENCHMARK RESULTS SUMMARY")
        print("="*60)

        for project_results in results:
            project_name = project_results.get('project', 'unknown')
            agent_results = project_results.get('agents', [])

            for agent_result in agent_results:
                agent_name = agent_result.get('agent', 'unknown')
                success_rate = agent_result.get('success_rate', 0)
                avg_time = agent_result.get('avg_time', 0)

                print(f"🏆 {agent_name} - {project_name}")
                print(".1f"                print(".3f"                print()

        print("✅ If success rate > 80%, your miner is ready for mainnet!")
        print("🔗 Check IWA Platform: https://infinitewebarena.autoppia.com")
        print("="*60)

    except KeyboardInterrupt:
        logger.warning("Benchmark interrupted by user")
    except Exception as e:
        logger.error(f"Benchmark failed: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    main()
EOF

# Copy config to remote server
scp /tmp/benchmark_config.py $REMOTE_USER@$REMOTE_HOST:/opt/autoppia-benchmark/benchmark_config.py

echo -e "${GREEN}✅ Benchmark configuration created${NC}"

echo -e "${YELLOW}📦 Step 6: Creating benchmark runner script...${NC}"

# Create runner script
cat > /tmp/run_official_benchmark.sh << 'EOF'
#!/bin/bash

# Official Autoppia IWA Miner Benchmark Runner
# Run this to test your miner against the official benchmark

set -e

echo "🚀 Running Official Autoppia IWA Miner Benchmark..."
echo "This will test your miner against demo web applications"
echo ""

cd /opt/autoppia-benchmark

# Activate virtual environment
source benchmark_env/bin/activate

# Check if demo webs are running
echo "🔍 Checking if demo web applications are running..."
if ! docker ps | grep -q "webs_server"; then
    echo "⚠️  Demo webs not running. Starting them..."
    cd autoppia_iwa_module/modules/webs_demo/scripts
    ./setup.sh
    sleep 10
fi

echo "✅ Demo webs are running"

# Run the benchmark
echo ""
echo "🎯 Starting benchmark..."
echo "This may take several minutes..."
echo ""

python benchmark_config.py

echo ""
echo "🎉 Benchmark complete!"
echo "📁 Check results in: /opt/autoppia-benchmark/results/"
EOF

# Copy runner script to remote server
scp /tmp/run_official_benchmark.sh $REMOTE_USER@$REMOTE_HOST:/opt/autoppia-benchmark/run_official_benchmark.sh
ssh -o StrictHostKeyChecking=no $REMOTE_USER@$REMOTE_HOST "chmod +x /opt/autoppia-benchmark/run_official_benchmark.sh"

echo -e "${GREEN}✅ Benchmark runner script created${NC}"

echo ""
echo -e "${GREEN}🎉 Official Benchmark Framework Deployed Successfully!${NC}"
echo ""
echo -e "${BLUE}📋 Next Steps:${NC}"
echo "1. SSH to your server: ssh root@$REMOTE_HOST"
echo "2. Run the benchmark: ./run_official_benchmark.sh"
echo "3. Check results in: /opt/autoppia-benchmark/results/"
echo ""
echo -e "${YELLOW}⚠️  Important:${NC}"
echo "- Demo web applications must be running (Docker required)"
echo "- This tests your miner with real validator logic"
echo "- Success rate > 80% means you're ready for mainnet evaluation"
echo ""
echo -e "${BLUE}🔗 Related:${NC}"
echo "- IWA Platform: https://infinitewebarena.autoppia.com"
echo "- Documentation: https://github.com/autoppia/autoppia_iwa/blob/main/autoppia_iwa/entrypoints/benchmark/README.md"
