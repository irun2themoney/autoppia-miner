# Hotkey Registration on Autoppia Subnet

## Understanding Hotkey Registration

If Autoppia is built on **Bittensor**, hotkey registration costs are **dynamic** and based on market demand:

### How Registration Costs Work

Registration fees adjust based on subnet demand each epoch:

- **All slots filled** → Cost increases in next epoch
- **Some slots filled** → Cost stays the same  
- **No slots filled** → Cost decreases in next epoch

This creates a market-driven pricing mechanism.

### Finding Current Registration Cost

To check the current registration cost for Autoppia's subnet:

```bash
# List all subnets and their registration fees
btcli subnets list

# Or check specific subnet (if you know the subnet ID)
btcli subnet show --netuid <subnet_id>
```

### Historical Registration Costs

You can view historical registration cost charts at:
- Taostats: `https://taostats.io/subnets/netuid-<subnetID>/#registration`
- Replace `<subnetID>` with Autoppia's subnet ID

## Important Notes

⚠️ **Registration fees are NOT refundable**
- TAO spent on registration is converted to alpha and recycled
- It's returned to unissued supply, not refunded upon de-registration
- Consider this as an operational cost

## Next Steps

1. **Check Autoppia's official documentation**:
   - Visit: https://luxit.gitbook.io/autoppia-docs
   - Check "Developer Studio" → "Publish a Template" section
   - Look for pricing/registration information

2. **Contact Autoppia directly**:
   - Official website: https://app.autoppia.com
   - Community channels (Twitter, Telegram, GitHub)
   - Support team

3. **Check if registration is required**:
   - Publishing a worker template might be free
   - Only running a miner/validator might require registration
   - Clarify with Autoppia team

## Alternative: Publishing Worker Template

If you're just **publishing a worker template** (not running a miner):
- This might be **free** via Autoppia Developer Studio
- No hotkey registration needed
- Just need to upload your `template.json` and code

## Questions to Ask Autoppia

1. Is hotkey registration required for publishing templates?
2. What's the current registration cost for Autoppia subnet?
3. What's the subnet ID/netuid for Autoppia?
4. Are there any alternatives to registration for developers?

