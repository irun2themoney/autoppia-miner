# ✅ Port Change Complete

## Summary

**Date**: Current  
**Status**: ✅ Successfully Changed

### Port Change Details
- **Old Port**: 8091
- **New Port**: 8092
- **Server**: 134.199.203.133
- **Service**: autoppia-miner

---

## What Was Done

1. ✅ **Backup Created**: Service file backed up
2. ✅ **Service Updated**: Systemd service file updated to use port 8092
3. ✅ **Firewall Updated**: Port 8092 allowed in UFW
4. ✅ **Systemd Reloaded**: Daemon reloaded to pick up changes
5. ✅ **Miner Restarted**: Service restarted successfully
6. ✅ **Port Verified**: Port 8092 is listening and active
7. ✅ **Axon Served**: Axon successfully served to network on new port

---

## Current Status

### Services
- ✅ **autoppia-miner**: Active on port 8092
- ✅ **autoppia-api**: Active on port 8080 (unchanged)

### Network
- ✅ **Axon**: Served to network at 134.199.203.133:8092
- ✅ **Firewall**: Port 8092 allowed
- ✅ **Port Listening**: Confirmed active

### Logs
```
Axon created: ip=134.199.203.133, port=8092
✅ Axon started on 134.199.203.133:8092
Serving axon to network...
```

---

## Next Steps

### 1. Monitor Network Update (5-15 minutes)
The network may take 5-15 minutes to update the metagraph with the new port.

**Check status**:
```bash
python3 scripts/check_onchain_status.py
```

### 2. Monitor for Validator Queries
Watch logs for incoming queries:
```bash
ssh root@134.199.203.133 'journalctl -u autoppia-miner -f | grep -E "TASK_RECEIVED|TASK_RESPONSE|synapse"'
```

### 3. Update Community Message
If you posted in Discord/Telegram, update the message with new port:
- **New Axon**: 134.199.203.133:8092

---

## Expected Outcomes

### Short Term (5-15 minutes)
- Metagraph updates with new port
- Network re-discovers miner
- Validators may start querying new port

### Medium Term (30-90 minutes)
- Validator queries received
- Responses processed successfully
- Incentive > 0 (if queries successful)

### Long Term (1-2 hours)
- Active Status = 1 (if queries successful)
- Regular validator queries
- Emissions > 0

---

## Rollback Instructions

If the new port doesn't help, you can rollback:

```bash
ssh root@134.199.203.133
cp /etc/systemd/system/autoppia-miner.service.backup.* /etc/systemd/system/autoppia-miner.service
systemctl daemon-reload
systemctl restart autoppia-miner
```

---

## Why This Might Help

1. **Port Conflicts**: Port 8091 might have been filtered or blocked
2. **Network Refresh**: New port triggers network re-discovery
3. **Fresh Registration**: Network sees miner as "new" with different port
4. **Validator Filtering**: Some validators might filter by port ranges

---

## Monitoring Commands

### Check Port Status
```bash
netstat -tlnp | grep 8092
# or
ss -tlnp | grep 8092
```

### Check Miner Status
```bash
systemctl status autoppia-miner
```

### Watch Logs
```bash
journalctl -u autoppia-miner -f
```

### Check On-Chain Status
```bash
python3 scripts/check_onchain_status.py
```

---

**Status**: ✅ Port change successful  
**Next**: Monitor for network update and validator queries  
**Timeline**: 5-15 minutes for network update, 30-90 minutes for queries

