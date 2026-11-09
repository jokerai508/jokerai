import json
from moomoo import *

tickers = ["US.CBRS", "US.RIOT", "US.DELL", "US.ANET", "US.AMD",
           "US.MRVL", "US.AVGO", "US.ADBE", "US.TSM", "US.NOK", "US.INTC"]

quote_ctx = OpenQuoteContext(host="127.0.0.1", port=11111)
results = {}
try:
    quote_ctx.subscribe(tickers, SubType.QUOTE)
    ret, data = quote_ctx.get_market_snapshot(tickers)
    if ret == 0:
        for _, row in data.iterrows():
            code = row.get("code", "")
            lp = row.get("last_price")
            pc = row.get("prev_close_price")
            op = row.get("open_price")
            hi = row.get("high_price")
            lo = row.get("low_price")
            vol = row.get("volume")
            chg = None
            chg_pct = None
            if lp is not None and pc is not None and pc != 0:
                chg = round(lp - pc, 2)
                chg_pct = round((lp - pc) / pc * 100, 2)
            results[code] = {
                "code": code,
                "name": row.get("name", ""),
                "update_time": str(row.get("update_time", "")),
                "last_price": lp,
                "prev_close": pc,
                "change": chg,
                "change_rate": chg_pct,
                "open": op,
                "high": hi,
                "low": lo,
                "volume": vol,
                "pre_change_val": row.get("pre_change_val"),
                "pre_change_rate": row.get("pre_change_rate"),
                "after_change_val": row.get("after_change_val"),
                "after_change_rate": row.get("after_change_rate"),
                "overnight_change_val": row.get("overnight_change_val"),
                "overnight_change_rate": row.get("overnight_change_rate"),
            }
    else:
        for t in tickers:
            results[t] = {"code": t, "error": f"Moomoo API ret={ret}: {data}"}
except Exception as e:
    for t in tickers:
        if t not in results:
            results[t] = {"code": t, "error": f"Exception: {str(e)}"}
finally:
    try:
        quote_ctx.close()
    except Exception:
        pass

print(json.dumps(results, indent=2))
