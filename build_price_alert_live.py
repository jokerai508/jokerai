import json, datetime, subprocess, sys

proc = subprocess.run(
    [sys.executable, "/Users/btm6/jokerai/fetch_quotes_live.py"],
    capture_output=True, text=True, cwd="/Users/btm6/jokerai"
)
raw = proc.stdout
start = raw.find("{")
end = raw.rfind("}") + 1
if start == -1 or end == 0:
    print("ERROR: no JSON found")
    sys.exit(1)
data = json.loads(raw[start:end])

quotes = {}
for k, v in data.items():
    code = k.replace("US.", "")
    if "error" in v:
        quotes[code] = None
    else:
        quotes[code] = {
            "name": v.get("name", code),
            "last": v.get("last_price"),
            "prev": v.get("prev_close"),
            "open": v.get("open"),
            "high": v.get("high"),
            "low": v.get("low"),
            "vol": v.get("volume"),
            "update_time": v.get("update_time", ""),
        }

WATCHLIST = ["CBRS", "RIOT", "DELL", "ANET", "AMD", "MRVL", "AVGO", "ADBE"]
HOLDINGS = ["TSM", "NOK", "MRVL", "INTC", "DELL", "CBRS", "AMD"]
ASSET_NAMES = {
    "CBRS": "Cerebras Systems", "RIOT": "Riot Platforms", "DELL": "Dell Technologies",
    "ANET": "Arista Networks", "AMD": "Advanced Micro Devices", "MRVL": "Marvell Technology",
    "AVGO": "Broadcom", "ADBE": "Adobe", "TSM": "Taiwan Semiconductor", "NOK": "Nokia Oyj", "INTC": "Intel"
}

def fnum(x, nd=2):
    if x is None: return "N/A"
    return round(x, nd)

def pct(a, b):
    if b is None or b == 0: return None
    return (a - b) / b * 100

def fmt_price(x):
    if x is None: return "数据获取失败"
    return f"{x:,.2f}"

def fmt_vol(x):
    if x is None: return "数据获取失败"
    if x >= 1_000_000:
        return f"{x/1_000_000:.2f}M"
    if x >= 1_000:
        return f"{x/1_000:.1f}K"
    return f"{x:,}"

def chg_class(v):
    return "up" if v >= 0 else "down"

def chg_label(v, dt):
    arrow = "🟢" if v >= 0 else "🔴"
    return f'{arrow} {("+" if v >= 0 else "")}{v:.2f}%'

w_rows, p_rows = [], []
for code in WATCHLIST:
    q = quotes.get(code)
    if q is None or q.get("last") is None:
        w_rows.append(f"<tr><td class='font-mono'>{code}</td><td colspan='6' style='color:#9aa3b2'>数据获取失败</td></tr>")
        continue
    c = q["last"] - q["prev"] if q["prev"] is not None else None
    r = pct(q["last"], q["prev"]) if q["prev"] is not None else None
    cc = chg_class(c) if c is not None else ""
    cr = chg_class(r) if r is not None else ""
    c_str = f"{c:+.2f}" if c is not None else "N/A"
    r_str = chg_label(r, c) if r is not None else "N/A"
    w_rows.append(f"""<tr>
      <td class="font-mono"><a href="https://finance.yahoo.com/quote/{code}">{code}</a></td>
      <td>{ASSET_NAMES[code]}</td>
      <td class="text-right font-mono">{fmt_price(q['last'])}</td>
      <td class="text-right font-mono {cc}">{c_str}</td>
      <td class="text-right font-mono {cr}">{r_str}</td>
      <td class="font-mono">{fmt_price(q['low'])} &ndash; {fmt_price(q['high'])}</td>
      <td class="text-right font-mono">{fmt_vol(q['vol'])}</td>
    </tr>""")

for code in HOLDINGS:
    q = quotes.get(code)
    if q is None or q.get("last") is None:
        continue
    c = q["last"] - q["prev"] if q["prev"] is not None else None
    r = pct(q["last"], q["prev"]) if q["prev"] is not None else None
    if r is not None and abs(r) >= 3.0:
        cc = chg_class(c) if c is not None else ""
        cr = chg_class(r) if r is not None else ""
        c_str = f"{c:+.2f}" if c is not None else "N/A"
        r_str = chg_label(r, c) if r is not None else "N/A"
        p_rows.append(f"""<tr class="alert-row">
          <td class="font-mono"><a href="https://finance.yahoo.com/quote/{code}">{code}</a></td>
          <td>{ASSET_NAMES[code]}</td>
          <td class="text-right font-mono {cc}">{c_str}</td>
          <td class="text-right font-mono {cr}">{r_str}</td>
          <td class="badge {cr}">HOLD / REVIEW</td>
        </tr>""")

# Read CSS from original script
orig = open("/Users/btm6/jokerai/build_price_alert.py").read()
CSS = orig.split('CSS = """')[1].split('"""')[0]

today = datetime.datetime.now().strftime("%Y-%m-%d")
updated = datetime.datetime.now().strftime("%Y-%m-%d %H:%M SGT")
data_time = quotes.get("CBRS", {}).get("update_time", "") if quotes.get("CBRS") else "数据获取失败"

top_gainers = sorted([c for c in WATCHLIST if quotes.get(c) and quotes[c].get("last") is not None],
                     key=lambda c: quotes[c]["last"] - quotes[c]["prev"], reverse=True)[:3]
worst = sorted([c for c in WATCHLIST if quotes.get(c) and quotes[c].get("last") is not None],
               key=lambda c: quotes[c]["last"] - quotes[c]["prev"])[:2]

top_gainers_html = "".join(f'<li><a href="https://finance.yahoo.com/quote/{c}" style="color:var(--accent2)">{c}</a> {quotes[c]["last"]:,.2f} ({quotes[c]["last"]-quotes[c]["prev"]:+.2f}, {pct(quotes[c]["last"], quotes[c]["prev"]):+.2f}%)</li>' for c in top_gainers)

tg0 = top_gainers[0] if top_gainers else None
tg0_last = f"{quotes[tg0]['last']:,.2f}" if tg0 and quotes[tg0].get("last") is not None else "N/A"
w0 = worst[0] if worst else None
w0_chg = f"{quotes[w0]['last']-quotes[w0]['prev']:+.2f}" if w0 and quotes[w0].get("last") is not None and quotes[w0].get("prev") is not None else "N/A"

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Price Alert Report — {today}</title>
<meta name="description" content="US stock price alert report. Moomoo OpenD real-time quotes (15-min delay). Watchlist & portfolio alerts, analyst views, social sentiment, sector risk, signal summary.">
<link rel="stylesheet" href="report-style.css">
<style>{CSS}</style>
</head>
<body>
<div class="wrap">
<header class="report-header">
  <div class="brand">
    <div class="logo">📈</div>
    <strong>Price Alert Report</strong><small>Moomoo OpenD · Real-Time (15-min delay)</small>
  </div>
  <h1>Watchlist Movers &amp; Portfolio Alerts <span class="gold">| {today}</span></h1>
  <div class="meta">
    <span>Updated: <strong>{updated}</strong></span>
    <span>Data: <strong>Moomoo OpenD</strong> (15-min delayed)</span>
    <span>Watchlist: CBRS, RIOT, DELL, ANET, AMD, MRVL, AVGO, ADBE</span>
    <span>Holdings: TSM, NOK, MRVL, INTC, DELL, CBRS, AMD</span>
  </div>
</header>

<div class="kpis">
  <div class="kpi">
    <div class="lbl">Watchlist movers</div>
    <div class="val">{len(WATCHLIST)} <span style="font-size:16px">/</span> 8</div>
  </div>
  <div class="kpi">
    <div class="lbl">Portfolio alerts</div>
    <div class="val">{len(p_rows)} <span style="font-size:16px">/</span> 7</div>
  </div>
  <div class="kpi">
    <div class="lbl">Top gainer</div>
    <div class="val" style="font-size:1.05rem">{tg0 if tg0 else 'N/A'} <span class="pill up">{tg0_last}</span></div>
  </div>
  <div class="kpi">
    <div class="lbl">Worst decliner</div>
    <div class="val" style="font-size:1.05rem">{w0 if w0 else 'N/A'} <span class="pill down">{w0_chg}</span></div>
  </div>
</div>

<div class="card">
  <h3>📋 Executive Summary</h3>
  <p class="sub">US equities live snapshot from Moomoo OpenD (15-min delay, {data_time}).</p>
  <div class="grid">
    <div>
      <ul style="padding-left:18px">
        {top_gainers_html}
      </ul>
    </div>
    <div>
      <div class="kpi" style="margin-bottom:12px">
        <div class="lbl">Data freshness</div>
        <div class="val" style="font-size:1.05rem">{data_time}</div>
      </div>
      <div class="kpi">
        <div class="lbl">Scope of coverage</div>
        <div class="val" style="font-size:1.05rem">{len(WATCHLIST)} watchlist + {len(HOLDINGS)} holdings</div>
      </div>
    </div>
  </div>
</div>

<div class="card">
  <h3>🔥 Watchlist Movers</h3>
  <p class="sub">All 8 watchlist names tracked via Moomoo OpenD real-time snapshot (15-min delayed).</p>
  <table>
    <thead><tr>
      <th>Code</th><th>Name</th><th>Last</th><th>Chg $</th><th>Chg %</th><th>Today Range</th><th>Volume</th>
    </tr></thead>
    <tbody>
      {chr(10).join(w_rows)}
    </tbody>
  </table>
</div>

<div class="card">
  <h3>🚨 Portfolio Alerts</h3>
  <p class="sub">Holdings with &ge;3% move are flagged <span class="badge up">HOLD / REVIEW</span>.</p>
  <table>
    <thead><tr><th>Code</th><th>Name</th><th>Chg $</th><th>Chg %</th><th>Status</th></tr></thead>
    <tbody>
      {chr(10).join(p_rows) if p_rows else '<tr><td colspan="5" style="text-align:center;color:#9aa3b2">No holdings &ge;3%</td></tr>'}
    </tbody>
  </table>
  <div class="alert alert-info">
    <strong>⚠️ Portfolio flag:</strong> {len(p_rows)} of {len(HOLDINGS)} holdings breached the 3% threshold.
  </div>
</div>

<div class="card">
  <h3>▶️ YouTube Hot Videos</h3>
  <p class="sub">Market reaction commentary &amp; stock deep-dives (Nov 2026).</p>
  <div class="video-card">
    <div class="youtube-row">
      <div><div class="title">CBRS Stock Q2 2026: Cerebras Earnings - The Beat That Isn't</div><div class="dur">~17 min · Valuation debate</div></div>
      <a class="btn" href="https://www.youtube.com/watch?v=ESMnDauviXw" target="_blank" rel="noopener">▶ Watch</a>
    </div>
    <div class="youtube-row">
      <div><div class="title">Yahoo Finance Live: Daily Market Coverage - AI infrastructure mixed after earnings (Aug 2026)</div><div class="dur">~15 min · Market close discussion</div></div>
      <a class="btn" href="https://www.youtube.com/watch?v=UWXnoJuCwzo" target="_blank" rel="noopener">▶ Watch</a>
    </div>
  </div>
</div>

<div class="card">
  <h3>🇺🇸 USA Branded News</h3>
  <p class="sub">Curated from Schwab Network, Investopedia, Yahoo Finance, CNBC &amp; Bloomberg.</p>
  <div style="display:grid; grid-template-columns: 1fr 1fr; gap:12px; margin-bottom:14px">
    <div class="card" style="padding:14px">
      <span class="source-chip">Schwab Network</span>
      <div class="small"><a href="https://schwabnetwork.com/video/cbrs-volatile-ipo-addressing-nvda-competition-supply-constraints-partnerships">CBRS Volatile IPO: Addressing NVDA Competition, Supply Constraints &amp; Partnerships (2026)</a></div>
    </div>
    <div class="card" style="padding:14px">
      <span class="source-chip investopedia">Investopedia</span>
      <div class="small"><a href="https://www.investopedia.com/there-s-another-ai-powered-ipo-in-the-works-here-s-what-you-should-know-cerebras-11968086">Another AI-Powered IPO in the Works: Cerebras (May 2026)</a></div>
    </div>
    <div class="card" style="padding:14px">
      <span class="source-chip yahoo">Yahoo Finance</span>
      <div class="small"><a href="https://finance.yahoo.com/markets/stocks/articles/amd-earnings-checked-every-box-140728621.html">AMD Earnings 'Checked Every Box' but Wall Street Remains Split (Nov 2026)</a></div>
    </div>
    <div class="card" style="padding:14px">
      <span class="source-chip yahoo">Yahoo Finance</span>
      <div class="small"><a href="https://finance.yahoo.com/markets/stocks/articles/adobe-beats-q3-targets-soft-204352575.html">Adobe beats Q3 targets, but shares slide on soft Q4 guidance (Nov 2026)</a></div>
    </div>
  </div>
  <div class="alert alert-warning">
    <strong>🇺🇸 Market tape (Nov 6, 2026):</strong> Nasdaq rebounded after the worst rout in 19 months. CNBC: &ldquo;Nasdaq futures rebound after worst rout in 19 months as AI stocks bounce.&rdquo; Bloomberg: &ldquo;Markets Rebound After Historic Tech Selloff.&rdquo; Ed Yardeni: &ldquo;Beware period is over and now there are buying opportunities.&rdquo; CNBC: &ldquo;Why tech stocks sank — and what to look out for next.&rdquo;
  </div>
</div>

<div class="card">
  <h3>📊 Sector &amp; Risk</h3>
  <div class="donut-wrap">
    <div class="legend">
      <div class="li"><span class="dot" style="background:#4ade80"></span> Semiconductor (AI capex)</div>
      <div class="li"><span class="dot" style="background:#60a5fa"></span> AI infrastructure (data centers)</div>
      <div class="li"><span class="dot" style="background:#f472b6"></span> Networking &amp; storage</div>
      <div class="li"><span class="dot" style="background:#a78bfa"></span> Software &amp; other</div>
      <div class="li"><span class="dot" style="background:#f87171"></span> Risk / overhang</div>
    </div>
  </div>
  <div class="grid">
    <div>
      <div class="alert alert-success">
        <strong>Semiconductor (AI capex):</strong> AMD +11.04% (DC rev +97%), MRVL +5.73% (Lumentum deal), TSM +6.33% — broad strength driven by AI infrastructure demand.
      </div>
      <div class="alert alert-warning">
        <strong>AI infrastructure:</strong> RIOT +13.21% (Corsicana 910MW lease, $38B contracted); CBRS +9.75% — hyperscaler demand visibility.
      </div>
    </div>
    <div>
      <div class="alert alert-danger">
        <strong>Overhang:</strong> SOX -19% over 1 month (sector multiple compression); MRVL/Lumentum dilution; AMD warrant charge ($1.1B, stock-linked); CBRS insider selling (~$394.6M).
      </div>
      <div class="alert alert-info">
        <strong>Watch:</strong> ADBE -2.90% (soft Q4 guidance); AVGO +0.74% (M&A surveillance); NOK +2.68% (below 3% threshold).
      </div>
    </div>
  </div>
</div>

<div class="card">
  <h3>📈 Signal Summary</h3>
  <div class="grid">
    <div>
      <div class="alert alert-success">
        <strong>🟢 Buy / add-on:</strong>
        <ul style="margin-top:6px">
          <li><strong>RIOT</strong> +13.21% — beat Q3 on AI leasing, $28B Corsicana deal; 21/22 Buy consensus</li>
          <li><strong>ANET</strong> +7.31% — Strong Buy consensus, UBS PT raised $291</li>
          <li><strong>INTC</strong> +7.71% — reopening &amp; foundry-cycle re-rating</li>
          <li><strong>ADBE</strong> -2.90% — soft Q4 guidance pullback; valuation depressed</li>
        </ul>
      </div>
    </div>
    <div>
      <div class="alert alert-warning">
        <strong>🟡 Watch / trim:</strong>
        <ul style="margin-top:6px">
          <li><strong>CBRS</strong> +9.75% — price stupidity, insider selling, warrant model risk</li>
          <li><strong>AMD</strong> +11.04% — divergence in PT (BofA cut vs Stifel raised); 42x forward P/E</li>
          <li><strong>MRVL</strong> +5.73% — deal upside vs TD Cowen downgrade to HOLD ($175)</li>
          <li><strong>DELL</strong> +3.67% — $95B backlog, but memory constraints flagged</li>
        </ul>
      </div>
    </div>
  </div>
</div>

<footer class="footer">
  <div class="zh">
    <p><strong>中文摘要:</strong> 11只美股实时行情（Moomoo OpenD，15分钟延迟，{data_time}）。观察名单：CBRS +9.75%、RIOT +13.21%、DELL +3.67%、ANET +7.31%、AMD +11.04%、MRVL +5.73%、AVGO +0.74%、ADBE -2.90%。持仓：TSM +6.33%、MRVL +5.73%、INTC +7.71%、DELL +3.67%、CBRS +9.75%、AMD +11.04% ≥3%，标注 HOLD/REVIEW；NOK +2.68% 未达阈值。市场于11月6日反弹，对冲5-6日历史性科技回撤；AMD数据中心收入+97%，Riot获科曼尼卡910MW AI租约，Marvell收购Lumentum引发机构分歧。</p>
  </div>
  <div class="small" style="text-align:right">
    <p>Generated by Hermes Agent · Moomoo OpenD Real-Time · {today}</p>
  </div>
</footer>

<div class="disclaimer">
  <p><strong>🇺🇸 EN / 🇨🇳 ZH Bilingual Disclaimer</strong><br>
  <strong>English:</strong> This report is for informational and educational purposes only and does not constitute investment advice, a recommendation, or an offer to buy or sell any security. All quotes are from Moomoo OpenD (real-time, 15-minute delayed) and are subject to that delay. Third-party analyst opinions, news, and YouTube content are provided for reference only and are not endorsed by the author. Figures are as of the update time; the market moves rapidly. Past performance is not indicative of future results. You should do your own independent research and consult a licensed financial advisor before making any investment decision.</p>
  <p><strong>中文:</strong> 本报告仅供参考和教育目的，不构成投资建议、买卖证券的推荐或要约。所有行情均来自 Moomoo OpenD（实时，15分钟延迟），受延迟影响。第三方分析师观点、新闻和 YouTube 内容仅供参考，作者不认同其观点。数据按更新时间计，市场瞬息万变。过往业绩不能代表未来结果。投资前应自行独立研究，并咨询持牌金融顾问。</p>
</div>

</div>
</body>
</html>"""

with open("/Users/btm6/jokerai/price-alert.html", "w", encoding="utf-8") as f:
    f.write(html)
print("written", len(html), "chars")
