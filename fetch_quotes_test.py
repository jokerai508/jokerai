import json
from moomoo import *

tickers = ["US.CBRS", "US.RIOT", "US.DELL", "US.ANET", "US.AMD",
           "US.MRVL", "US.AVGO", "US.ADBE", "US.TSM", "US.NOK", "US.INTC"]

quote_ctx = OpenQuoteContext(host="127.0.0.1", port=11111)
try:
    ret, msg = quote_ctx.subscribe(tickers, SubType.QUOTE)
    print("SUBSCRIBE ret:", ret, "msg:", msg)
    ret, data = quote_ctx.get_market_snapshot(tickers)
    print("SNAPSHOT ret:", ret)
    print("COLUMNS:", list(data.columns))
    for _, row in data.iterrows():
        print(row["code"], "| last:", row.get("last_price"), "| prev_close:", row.get("prev_close"),
              "| change:", row.get("change"), "| change_rate:", row.get("change_rate"),
              "| open:", row.get("open"), "| high:", row.get("high"), "| low:", row.get("low"),
              "| volume:", row.get("volume"))
finally:
    quote_ctx.close()
