## Get Balance

Get the ETH (native token) and USDC (ERC-20 token) balances of the current BASE address.

Quick one-liner:
```bash
curl [http://127.0.0.1:5333/balance](http://127.0.0.1:5333/balance)
# Output: {"status": "success", "address": "0x...", "ETH": 1.25, "USDC": 1500.5}