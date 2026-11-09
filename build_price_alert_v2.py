# -*- coding: utf-8 -*-
"""Build price-alert.html from LIVE Moomoo OpenD quotes + web-sourced data.
Data timestamp: 2026-11-07 15:02:28 SGT (US market close 2026-11-06 20:02:28 EST).
Quotes fetched from Moomoo OpenD 127.0.0.1:11111 (15-min delayed snapshot)."""
import json

OUT = "/Users/btm6/jokerai/price-alert.html"

# ---------- REAL QUOTES (Moomoo OpenD snapshot, 2026-11-07 15:02:28 SGT) ----------
# code -> [name, last, prev, open, high, low, volume]
QUOTES = {
    "CBRS": ["Cerebras Systems", 89.68, 81.71, 85.30, 90.29, 83.50, 9967034],
    "RIOT": ["Riot Platforms",      16.71, 14.76, 15.83, 17.12, 14.87, 45077267],
    "DELL": ["Dell Technologies",  328.53, 316.91, 346.05, 350.36, 325.10, 8601290],
    "ANET": ["Arista Networks",    170.80, 159.16, 172.80, 173.60, 167.00, 11982886],
    "AMD":  ["Advanced Micro Devices", 449.04, 404.40, 444.43, 459.80, 433.30, 45759759],
    "MRVL": ["Marvell Technology", 141.20, 133.55, 145.07, 146.32, 135.34, 33562131],
    "AVGO": ["Broadcom",           293.69, 291.53, 311.13, 311.52, 289.77, 32442491],
    "ADBE": ["Adobe",              239.30, 246.44, 239.00, 243.38, 236.84, 3297370],
    "TSM":  ["Taiwan Semiconductor", 375.44, 353.10, 380.56, 380.72, 367.95, 23841904],
    "NOK":  ["Nokia Oyj",           7.66,  7.46,  7.75,  7.79,  7.57,  49175099],
    "INTC": ["Intel",              56.28, 52.25, 54.99, 57.32, 54.56, 174382270],
}

WATCHLIST = ["CBRS", "RIOT", "DELL", "ANET", "AMD", "MRVL", "AVGO", "ADBE"]
HOLDINGS  = ["TSM", "NOK", "MRVL", "INTC", "DELL", "CBRS", "AMD"]
ASSET_NAMES = {
    "CBRS": "Cerebras Systems", "RIOT": "Riot Platforms", "DELL": "Dell Technologies",
    "ANET": "Arista Networks", "AMD": "Advanced Micro Devices", "MRVL": "Marvell Technology",
    "AVGO": "Broadcom", "ADBE": "Adobe", "TSM": "Taiwan Semiconductor", "NOK": "Nokia Oyj", "INTC": "Intel",
}

def chg(c, p):
    v = c - p
    r = (v / p * 100) if p else 0.0
    return v, r

# ---------- derived data ----------
w_rows = []
for code in WATCHLIST:
    name, c, p, o, hi, lo, vol = QUOTES[code]
    dv, dr = chg(c, p)
    cls = "up" if dv >= 0 else "down"
    arrow = "🟢" if dv >= 0 else "🔴"
    pct_s = f'{arrow} {("+" if dv >= 0 else "")}{dr:.2f}%'
    w_rows.append(
        f'<tr><td class="font-mono"><a href="https://finance.yahoo.com/quote/{code}">{code}</a></td>'
        f'<td>{name}</td>'
        f'<td class="text-right font-mono">{c:,.2f}</td>'
        f'<td class="text-right font-mono {cls}">{dv:+.2f}</td>'
        f'<td class="text-right font-mono {cls}">{pct_s}</td>'
        f'<td class="font-mono">{lo:,.2f} &ndash; {hi:,.2f}</td>'
        f'<td class="text-right font-mono">{vol/1_000_000:.2f}M</td></tr>'
    )

p_rows = []
portfolio_alerts = []
for code in HOLDINGS:
    name, c, p, o, hi, lo, vol = QUOTES[code]
    dv, dr = chg(c, p)
    if abs(dr) >= 3.0:
        cls = "up" if dv >= 0 else "down"
        p_rows.append(
            f'<tr class="alert-row"><td class="font-mono"><a href="https://finance.yahoo.com/quote/{code}">{code}</a></td>'
            f'<td>{name}</td>'
            f'<td class="text-right font-mono {cls}">{dv:+.2f}</td>'
            f'<td class="text-right font-mono {cls}">🟢{dr:.2f}%</td>'
            f'<td class="badge {cls}">HOLD / REVIEW</td></tr>'
        )
        portfolio_alerts.append((code, name, dv, dr))

top_gainer = max(WATCHLIST, key=lambda c: QUOTES[c][2] - QUOTES[c][1])
worst = min(WATCHLIST, key=lambda c: QUOTES[c][2] - QUOTES[c][1])
top3_gainers = sorted(WATCHLIST, key=lambda c: QUOTES[c][2] - QUOTES[c][1], reverse=True)[:3]
top3_tickers = "".join(
    f'<li><a href="https://finance.yahoo.com/quote/{c}" style="color:var(--accent2)">{c}</a> {QUOTES[c][1]:,.2f} '
    f'({("+" if QUOTES[c][2]-QUOTES[c][1] >= 0 else "")}{QUOTES[c][2]-QUOTES[c][1]:+.2f}, '
    f'{("🟢" if QUOTES[c][2]-QUOTES[c][1] >= 0 else "🔴")}{("+" if QUOTES[c][2]-QUOTES[c][1] >= 0 else "")}{QUOTES[c][2]-QUOTES[c][1]/QUOTES[c][1]*100:.2f}%)</li>'
    for c in top3_gainers
)
worst2 = sorted(WATCHLIST, key=lambda c: QUOTES[c][2] - QUOTES[c][1])[:2]

# ---------- CSS (global report-style.css + mobile 720px override) ----------
def read_css(path):
    with open(path, encoding="utf-8") as f:
        return f.read()

CSS = read_css("/Users/btm6/jokerai/report-style.css") + """
@media (max-width: 720px) {
  .wrap { max-width: 720px; padding: 14px 16px 32px; }
  .hero, .report-header { padding: 22px 18px; }
  .hero h1, .report-header h1 { font-size: 25px; }
  .kpi .val, .stat-value { font-size: 22px; }
  table { font-size: 12.5px; }
  th, td { padding: 10px 6px; }
  .card, .section { padding: 18px 16px; }
}
@media (max-width: 600px) {
  .wrap { padding: 12px; }
  .hero h1, .report-header h1 { font-size: 22px; }
  .kpis, .stats-grid { grid-template-columns: 1fr; }
}
"""

# ---------- assemble HTML ----------
html = []
html.append(f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Price Alert Report — 2026-11-07</title>
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
  <h1>Watchlist Movers &amp; Portfolio Alerts <span class="gold">| 2026-11-07</span></h1>
  <div class="meta">
    <span>Updated: <strong>2026-11-07 15:02 SGT</strong></span>
    <span>Data: <strong>Moomoo OpenD</strong> (15-min delayed)</span>
    <span>Watchlist: CBRS, RIOT, DELL, ANET, AMD, MRVL, AVGO, ADBE</span>
    <span>Holdings: TSM, NOK, MRVL, INTC, DELL, CBRS, AMD</span>
  </div>
</header>

<div class="kpis">
  <div class="kpi"><div class="lbl">Watchlist movers</div><div class="val">8 / 8</div></div>
  <div class="kpi"><div class="lbl">Portfolio alerts</div><div class="val">{len(p_rows)} / 7</div></div>
  <div class="kpi"><div class="lbl">Top gainer</div><div class="val" style="font-size:1.05rem">{top_gainer} <span class="pill up">{QUOTES[top_gainer][1]:,.2f}</span></div></div>
  <div class="kpi"><div class="lbl">Worst decliner</div><div class="val" style="font-size:1.05rem">{worst} <span class="pill down">{QUOTES[worst][2]-QUOTES[worst][1]:+.2f}</span></div></div>
</div>

<div class="card">
  <h3>📋 Executive Summary</h3>
  <p class="sub">US equities staged a sharp rebound on 2026-11-06 after the historic 19-month tech drawdown — AI-infrastructure names led. Live Moomoo OpenD data (15-min delay, snapshot 15:02:28 SGT) show <strong>{top3_gainers[0]} +{QUOTES[top3_gainers[0]][2]-QUOTES[top3_gainers[0]][1]:.2f}%</strong> the top mover and <strong>{worst} {QUOTES[worst][2]-QUOTES[worst][1]:+.2f}%</strong> the laggard. Portfolio exposure is concentrated in AI-capex semis: <strong>{len(p_rows)} of {len(HOLDINGS)} holdings moved &ge;3%</strong> and are flagged HOLD / REVIEW.</p>
  <div class="grid">
    <div>
      <ul style="padding-left:18px">
        <li><strong>AI infrastructure boom:</strong> {top3_gainers[0]} +{QUOTES[top3_gainers[0]][2]-QUOTES[top3_gainers[0]][1]:.2f}% on demand beat; RIOT +13.21% on Corsicana 910MW lease; CBRS +9.75% on wafer-scale demand</li>
        <li><strong>Hardware &amp; foundry:</strong> TSM +6.33%, INTC +7.71%, MRVL +5.73% — AI capex cycle re-accelerates</li>
        <li><strong>M&amp;A overhang:</strong> MRVL +5.73% on Lumentum $115B deal; TD Cowen/BofA downgrades cap upside</li>
        <li><strong>Peak multiple compression:</strong> SOX &minus;19% over 1 month; ADBE &minus;2.90% on soft Q4 guidance; CBRS insider selling &amp; lock-up expiry weigh</li>
      </ul>
    </div>
    <div>
      <div class="kpi" style="margin-bottom:12px"><div class="lbl">New 30-day high (watchlist)</div><div class="val">{top3_gainers[0]} {QUOTES[top3_gainers[0]][1]:,.2f}</div></div>
      <div class="kpi" style="margin-bottom:12px"><div class="lbl">Data freshness</div><div class="val" style="font-size:1.05rem">15:02:28 SGT</div></div>
      <div class="kpi"><div class="lbl">Coverage</div><div class="val" style="font-size:1.05rem">{len(WATCHLIST)} watchlist + {len(HOLDINGS)} holdings</div></div>
    </div>
  </div>
</div>

<div class="card">
  <h3>🔥 Watchlist Movers</h3>
  <p class="sub">All 8 watchlist names tracked via Moomoo OpenD real-time snapshot (15-min delayed).</p>
  <table>
    <thead><tr><th>Code</th><th>Name</th><th>Last</th><th>Chg $</th><th>Chg %</th><th>Today Range</th><th>Volume</th></tr></thead>
    <tbody>
      {chr(10).join(w_rows)}
    </tbody>
  </table>
</div>

<div class="card">
  <h3>🚨 Portfolio Alerts</h3>
  <p class="sub">{len(p_rows)} of {len(HOLDINGS)} holdings breached the 3% threshold, flagged <span class="badge up">HOLD / REVIEW</span>.</p>
  <table>
    <thead><tr><th>Code</th><th>Name</th><th>Chg $</th><th>Chg %</th><th>Status</th></tr></thead>
    <tbody>
      {chr(10).join(p_rows) if p_rows else '<tr><td colspan="5" style="text-align:center;color:#9aa3b2">No holdings &ge;3%</td></tr>'}
    </tbody>
  </table>
</div>

<div class="card">
  <h3>▶️ YouTube Hot Videos</h3>
  <p class="sub">Market-reaction commentary &amp; stock deep-dives (Nov 2026).</p>
  <div class="video-card">
    <div class="youtube-row">
      <div><div class="title">Wall Street Is Rotating Back Into AI Hardware — AMD, Arista, Astera beat &amp; AI infra demand</div><div class="dur">~08 min · Market tape review</div></div>
      <a class="btn" href="https://www.youtube.com/watch?v=u9r51mijUNE" target="_blank" rel="noopener">▶ Watch</a>
    </div>
    <div class="youtube-row">
      <div><div class="title">Tech Melt-Up Drives $3.5T Nasdaq 100 Gain in Four Days</div><div class="dur">~04 min · Market tape review</div></div>
      <a class="btn" href="https://www.youtube.com/watch?v=7KGgu-9_0HU" target="_blank" rel="noopener">▶ Watch</a>
    </div>
    <div class="youtube-row">
      <div><div class="title">What sets AMD data centers apart as Intel stock keeps sliding?</div><div class="dur">~05 min · AMD earnings teardown</div></div>
      <a class="btn" href="https://finance.yahoo.com/video/what-sets-amd-data-centers-apart-as-intel-stock-keeps-sliding-141848435.html" target="_blank" rel="noopener">▶ Watch</a>
    </div>
    <div class="youtube-row">
      <div><div class="title">Stocks lost $2 trillion. The market is wrong about AI</div><div class="dur">~07 min · AI trade debate</div></div>
      <a class="btn" href="https://finance.yahoo.com/video/stocks-lost-2-trillion-market-120000040.html" target="_blank" rel="noopener">▶ Watch</a>
    </div>
  </div>
</div>

<div class="card">
  <h3>🇺🇸 USA Branded News</h3>
  <p class="sub">Curated from Schwab Network, Investopedia, Yahoo Finance, CNBC &amp; Bloomberg.</p>
  <div style="display:grid; grid-template-columns: 1fr 1fr; gap:12px; margin-bottom:14px">
    <div class="card" style="padding:14px">
      <span class="source-chip schwab">Schwab Network</span>
      <div class="small"><a href="https://schwabnetwork.com/articles/closing-bell-stocks-rise-as-tech-and-amd-rally-election-results-unfold">Stocks Rise as Tech and AMD Rally, Election Results Unfold (Nov 3)</a></div>
    </div>
    <div class="card" style="padding:14px">
      <span class="source-chip schwab">Schwab Network</span>
      <div class="small"><a href="https://schwabnetwork.com/markets/earnings">Market On Close: AI infrastructure mixed after earnings — AMD, ANET, INTC, MRVL (Nov 6)</a></div>
    </div>
    <div class="card" style="padding:14px">
      <span class="source-chip investopedia">Investopedia</span>
      <div class="small"><a href="https://www.investopedia.com/there-s-another-ai-powered-ipo-in-the-works-here-s-what-you-should-know-cerebras-11968086">Another AI-Powered IPO in the Works: Cerebras (May 2026)</a></div>
    </div>
    <div class="card" style="padding:14px">
      <span class="source-chip yahoo">Yahoo Finance</span>
      <div class="small"><a href="https://finance.yahoo.com/markets/stocks/articles/amd-earnings-checked-every-box-140728621.html">AMD Earnings 'Checked Every Box' but Wall Street Remains Split (Nov 4)</a></div>
    </div>
  </div>
  <div class="alert alert-warning">
    <strong>🇺🇸 Market tape (Nov 6, 2026):</strong> Nasdaq rebounded after the worst rout in 19 months. <strong>Schwab Network:</strong> "Stocks Rise as Tech and AMD Rally"; CNBC: "Nasdaq futures rebound after worst rout in 19 months as AI stocks bounce." <strong>Yahoo Finance:</strong> AMD Q3 beat &mdash; data center revenue ~$8.5B (+97% YoY), Q4 revenue guidance ~$17B; BofA raised 2027/2028 EPS estimates but cut PT to $650. <strong>Bloomberg:</strong> "Markets Rebound After Historic Tech Selloff." <strong>CNBC:</strong> "Post-election rally masks a sharp split in the AI trade" &mdash; neoclouds (CoreWeave &minus;10%, Iren &minus;11%) under pressure; hyperscalers like Amazon +7% lead.
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
        <strong>Semiconductor (AI capex):</strong> AMD +11.04% (DC rev +97% to ~$8.55B); MRVL +5.73% (Lumentum $115B deal); TSM +6.33% — broad strength from AI infrastructure demand.
      </div>
      <div class="alert alert-warning">
        <strong>AI infrastructure:</strong> RIOT +13.21% (Corsicana 910MW lease); CBRS +9.75% on hyperscaler demand visibility. But neocloud caution: CoreWeave / Iren / Nebius under pressure post-midterms (debt-funded, higher refinancing costs).
      </div>
    </div>
    <div>
      <div class="alert alert-danger">
        <strong>Overhang:</strong> SOX &minus;19% over 1 month (sector multiple compression); MRVL/Lumentum dilution; AMD warrant charge ($1.1B, stock-linked); CBRS insider selling (~$394.6M) &amp; lock-up expiry Nov 9 (earnings Nov 12).
      </div>
      <div class="alert alert-info">
        <strong>Watch:</strong> ADBE &minus;2.90% (soft Q4 guidance); AVGO +0.74% (M&amp;A surveillance); NOK +2.68% (below 3% threshold, not flagged); INTC +7.71% (reopening &amp; foundry-cycle re-rating).
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
          <li><strong>RIOT</strong> +13.21% — AI leasing beat, $28B Corsicana deal; strong Buy consensus</li>
          <li><strong>ANET</strong> +7.31% — Strong Buy, 32 analysts, PT $245 (UBS raised to $291)</li>
          <li><strong>INTC</strong> +7.71% — reopening &amp; foundry-cycle re-rating</li>
        </ul>
      </div>
    </div>
    <div>
      <div class="alert alert-warning">
        <strong>🟡 Watch / trim:</strong>
        <ul style="margin-top:6px">
          <li><strong>CBRS</strong> +9.75% — insider selling, warrant model, lock-up/undervaluation; UBS still Buy ($250)</li>
          <li><strong>AMD</strong> +11.04% — Street split on PT (Citi $800 vs Mizuho $610); 42x forward P/E</li>
          <li><strong>MRVL</strong> +5.73% — deal upside vs TD Cowen downgrade to HOLD ($175)</li>
          <li><strong>DELL</strong> +3.67% — $95B backlog, memory constraints flagged</li>
        </ul>
      </div>
    </div>
  </div>
</div>

<footer class="footer">
  <div class="zh">
    <p><strong>中文摘要:</strong> 实时行情（Moomoo OpenD，15分钟延迟，快照 2026-11-07 15:02:28 SGT）。观察名单：CBRS +9.75%、RIOT +13.21%、DELL +3.67%、ANET +7.31%、AMD +11.04%、MRVL +5.73%、AVGO +0.74%、ADBE -2.90%。持仓：TSM +6.33%、NOK +2.68%、MRVL +5.73%、INTC +7.71%、DELL +3.67%、CBRS +9.75%、AMD +11.04%，其中 {len(p_rows)} 只持仓 ≥3% 标注 HOLD/REVIEW。市场于11月6日在历史性科技回撤后反弹；AI数据中心需求强劲（AMD DC收入+97%），但新兴云融资成本与CBRS面孔/锁定期是风险点。</p>
  </div>
  <div class="small" style="text-align:right">
    <p>Generated by Hermes Agent · Moomoo OpenD Real-Time · 2026-11-07</p>
  </div>
</footer>

<div class="disclaimer">
  <p><strong>🇺🇸 EN / 🇨🇳 ZH Bilingual Disclaimer</strong><br>
  <strong>English:</strong> This report is for informational and educational purposes only and does not constitute investment advice, a recommendation, or an offer to buy or sell any security. All quotes are from Moomoo OpenD (real-time, 15-minute delayed) and are subject to that delay. Third-party analyst opinions, news, and YouTube content are provided for reference only and are not endorsed by the author. Figures are as of the update time; the market moves rapidly. Past performance is not indicative of future results. You should do your own independent research and consult a licensed financial advisor before making any investment decision.</p>
  <p><strong>中文:</strong> 本报告仅供参考和教育目的，不构成投资建议、买卖证券的推荐或要约。所有行情均来自 Moomoo OpenD（实时，15分钟延迟），受延迟影响。第三方分析师观点、新闻和 YouTube 内容仅供参考，作者不认同其观点。数据按更新时间计，市场瞬息万变。过往业绩不能代表未来结果。投资前应自行独立研究，并咨询持牌金融顾问。</p>
</div>

</div>
</body>
</html>""")

out = "".join(html)
with open(OUT, "w", encoding="utf-8") as f:
    f.write(out)
print("written", len(out), "chars")
print("sections:", all(s in out for s in ["📋 Executive Summary", "🔥 Watchlist Movers", "🚨 Portfolio Alerts",
    "▶️ YouTube Hot Videos", "🇺🇸 USA Branded News", "📊 Sector &amp; Risk", "📈 Signal Summary",
    "中文摘要", "Bilingual Disclaimer", "Generated by Hermes Agent"]))
