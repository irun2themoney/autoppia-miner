# Deployment Checklist - Validator Visibility

Use this checklist when deploying your miner to ensure validators can discover and query you.

## Pre-Deployment

- [ ] **Wallet Created**
  - [ ] Coldkey created: `btcli wallet create --wallet.name <name>`
  - [ ] Hotkey created: `btcli wallet new_hotkey --wallet.name <name> --wallet.hotkey <hotkey>`
  - [ ] Wallet backed up securely

- [ ] **TAO Balance**
  - [ ] At least 0.1 TAO in wallet for registration
  - [ ] Verified: `btcli wallet balance --wallet.name <name>`

- [ ] **Server Setup**
  - [ ] VPS/server provisioned (recommended: 4GB RAM, 2 CPU)
  - [ ] Ubuntu 20.04+ or similar Linux distribution
  - [ ] SSH access configured
  - [ ] Firewall configured (UFW or firewalld)

## Initial Deployment

- [ ] **Clone Repository**
  ```bash
  cd /opt
  git clone <your-repo-url> autoppia-miner
  cd autoppia-miner
  ```

- [ ] **Install Dependencies**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  pip install --upgrade pip
  pip install -r requirements.txt
  ```

- [ ] **Configure Environment**
  ```bash
  cp env.example .env
  nano .env
  ```
  - [ ] Set `WALLET_NAME=<your_wallet_name>`
  - [ ] Set `WALLET_HOTKEY=<your_hotkey_name>`
  - [ ] Set `API_HOST=0.0.0.0`
  - [ ] Set `API_PORT=8080`
  - [ ] Set `AXON_PORT=8091`
  - [ ] Set `NETWORK=finney`
  - [ ] Set `SUBNET_UID=36`

- [ ] **Copy Wallet to Server**
  ```bash
  # On local machine:
  scp -r ~/.bittensor/wallets/<wallet_name> root@<server_ip>:~/.bittensor/wallets/
  ```

- [ ] **Open Firewall Ports**
  ```bash
  # UFW (Ubuntu/Debian)
  sudo ufw allow 8080/tcp
  sudo ufw allow 8091/tcp
  sudo ufw reload
  
  # OR firewalld (CentOS/RHEL)
  sudo firewall-cmd --permanent --add-port=8080/tcp
  sudo firewall-cmd --permanent --add-port=8091/tcp
  sudo firewall-cmd --reload
  ```

- [ ] **Register on Subnet 36**
  ```bash
  btcli subnet register --netuid 36 --wallet.name <name> --wallet.hotkey <hotkey>
  ```
  - [ ] Registration successful
  - [ ] UID assigned

## Service Setup

- [ ] **Install Systemd Services**
  ```bash
  sudo cp scripts/deploy/autoppia-api.service /etc/systemd/system/
  sudo cp scripts/deploy/autoppia-miner.service /etc/systemd/system/
  sudo systemctl daemon-reload
  ```

- [ ] **Start Services**
  ```bash
  sudo systemctl start autoppia-api
  sudo systemctl start autoppia-miner
  sudo systemctl enable autoppia-api
  sudo systemctl enable autoppia-miner
  ```

- [ ] **Verify Services Running**
  ```bash
  sudo systemctl status autoppia-api
  sudo systemctl status autoppia-miner
  ```

## Verification

- [ ] **Check Registration**
  ```bash
  ./scripts/utils/check_registration.sh
  ```
  - [ ] Shows UID
  - [ ] Shows stake
  - [ ] Shows metagraph position

- [ ] **Verify Visibility**
  ```bash
  ./scripts/utils/verify_visibility.sh
  ```
  - [ ] API service running
  - [ ] Miner service running
  - [ ] API health endpoint responding
  - [ ] Axon port listening
  - [ ] Firewall rules correct

- [ ] **Test API Endpoint**
  ```bash
  curl http://localhost:8080/health
  ```
  - [ ] Returns JSON response
  - [ ] Status shows healthy

- [ ] **Check Miner Logs**
  ```bash
  journalctl -u autoppia-miner -n 50
  ```
  - [ ] No errors
  - [ ] Shows "Miner registered! UID: X"
  - [ ] Shows "Axon served to subtensor network"
  - [ ] Shows "Miner is running and ready"

- [ ] **Monitor for Validator Requests**
  ```bash
  journalctl -u autoppia-miner -f | grep "Processing task"
  ```
  - [ ] Wait 5-10 minutes
  - [ ] Validator requests appearing

## Post-Deployment

- [ ] **Access Dashboard**
  - [ ] Open `http://<server_ip>:8080/dashboard` in browser
  - [ ] Dashboard loads successfully
  - [ ] Metrics updating

- [ ] **Run Tests**
  ```bash
  python3 tests/test_ultimate.py http://localhost:8080
  ```
  - [ ] All tests passing

- [ ] **Check Metagraph**
  ```bash
  btcli subnet metagraph --netuid 36 | grep <your_uid>
  ```
  - [ ] Shows correct IP
  - [ ] Shows correct port (8091)
  - [ ] Status is active

- [ ] **Monitor Performance**
  - [ ] Check dashboard every few hours
  - [ ] Monitor success rate
  - [ ] Watch for validator activity

## Troubleshooting

If validators aren't seeing you after 30 minutes:

- [ ] Review [VALIDATOR_VISIBILITY_GUIDE.md](../docs/VALIDATOR_VISIBILITY_GUIDE.md)
- [ ] Re-run `./scripts/utils/check_registration.sh`
- [ ] Re-run `./scripts/utils/verify_visibility.sh`
- [ ] Check logs: `journalctl -u autoppia-miner -n 200`
- [ ] Verify external IP: `curl ifconfig.me`
- [ ] Test port accessibility from external machine
- [ ] Restart services: `sudo systemctl restart autoppia-api autoppia-miner`

## Maintenance

- [ ] **Regular Updates**
  ```bash
  cd /opt/autoppia-miner
  git pull
  pip install -r requirements.txt
  sudo systemctl restart autoppia-api autoppia-miner
  ```

- [ ] **Monitor Logs**
  ```bash
  journalctl -u autoppia-miner -f
  ```

- [ ] **Check Dashboard Daily**
  - Success rate
  - Validator activity
  - Error rates

- [ ] **Backup Wallet**
  - Keep secure backup of `~/.bittensor/wallets/`
  - Store in multiple locations

## Success Criteria

✅ Your miner is successfully deployed when:

- [ ] UID assigned on subnet 36
- [ ] Services running without errors
- [ ] Validator requests appearing in logs (every 5-10 minutes)
- [ ] Dashboard shows active validators (3+)
- [ ] Success rate above 70%
- [ ] No errors in recent logs

---

**Need Help?** See [VALIDATOR_VISIBILITY_GUIDE.md](../docs/VALIDATOR_VISIBILITY_GUIDE.md) for detailed troubleshooting.
