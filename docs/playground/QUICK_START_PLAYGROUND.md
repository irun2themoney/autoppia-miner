# Quick Start - Test on IWA Playground

## 🎯 What You Need to Do

1. **Open the Playground**: https://infinitewebarena.autoppia.com/playground

2. **Find the "Agent Endpoint" field**

3. **Type this exactly**:
   ```
   got-pen-mass-subdivision.trycloudflare.com
   ```

4. **Click "Run Benchmark"**

## ✅ That's It!

Your miner will be tested automatically.

## 🔍 What's Happening Behind the Scenes?

- Your API is running on your server
- A tunnel makes it accessible via HTTPS
- The playground connects through the tunnel
- Tests run automatically

## ❓ Common Questions

**Q: Do I include "https://"?**
A: No! Just type: `got-pen-mass-subdivision.trycloudflare.com`

**Q: What if it says "Failed to fetch"?**
A: The tunnel URL might have changed. Run:
   ```bash
   bash scripts/fix_playground_access.sh
   ```
   Then use the new URL it shows.

**Q: Can I use the IP address instead?**
A: No, because the playground uses HTTPS and your API uses HTTP. The tunnel fixes this.

## 🆘 Need Help?

Run this to check everything:
```bash
bash scripts/fix_playground_access.sh
```

It will tell you:
- ✅ If the tunnel is working
- ✅ What URL to use
- ✅ If there are any problems

