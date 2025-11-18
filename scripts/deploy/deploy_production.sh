#!/bin/bash
# Production Deployment Script
# Deploys the latest miner code to production server

set -e

echo "🚀 Starting Production Deployment..."

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Server details
SERVER="root@134.199.203.133"
PROJECT_DIR="autoppia-miner"

echo -e "${YELLOW}📦 Pulling latest code...${NC}"
ssh $SERVER "cd $PROJECT_DIR && git pull origin main || git pull origin master"

echo -e "${YELLOW}📥 Installing dependencies...${NC}"
ssh $SERVER "cd $PROJECT_DIR && pip install -r requirements.txt"

echo -e "${YELLOW}🔄 Restarting services...${NC}"
ssh $SERVER "sudo systemctl restart autoppia-api"
ssh $SERVER "sudo systemctl restart autoppia-miner"

echo -e "${YELLOW}⏳ Waiting for services to start...${NC}"
sleep 5

echo -e "${YELLOW}✅ Checking service status...${NC}"
ssh $SERVER "sudo systemctl status autoppia-api --no-pager | head -10"
ssh $SERVER "sudo systemctl status autoppia-miner --no-pager | head -10"

echo -e "${YELLOW}🧪 Testing endpoints...${NC}"
ssh $SERVER "curl -s http://localhost:8080/health | head -5"

echo -e "${GREEN}✅ Deployment Complete!${NC}"
echo -e "${GREEN}🎉 Miner is ready to earn TAO!${NC}"
