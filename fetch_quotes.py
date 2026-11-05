import sys
import json
from moomoo import *

tickers = ["US.CBRS", "US.RIOT", "US.DELL", "US.ANET", "US.AMD", "US.MRVL", "US.AVGO", "US.ADBE", "US.TSM", "US.NOK", "US.INTC"]
results = {}

for ticker in tickers:
    try:
        # Using the SDK function directly.
        # In the skills docs, we see get_market_snapshot.
        ret, data = get_market_snapshot(ticker)
        if ret:
            # Extract required fields
            # Note: Some data might be in 'snapshot' or 'quote'
            results[ticker] = data
        else:
            results[ticker] = "Data fetch failed"
    except Exception as e:
        results[ticker] = f"Error: {str(e)}"

print(json.dumps(results, indent=2))
