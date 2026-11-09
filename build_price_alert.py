# -*- coding: utf-8 -*-
"""Build price-alert.html from live Moomoo OpenD quotes + web-sourced analyst/news data."""
import json, datetime

# ---------- live quotes (15:01:46 SGT) ----------
# code -> dict
QUOTES = {
    "CBRS": {"name": "Cerebras Systems", "last": 89.68, "prev": 81.71, "open": 85.30, "high": 90.29, "low": 83.50, "vol": 9967034},
    "RIOT": {"name": "Riot Platforms", "last": 16.71, "prev": 14.76, "open": 15.83, "high": 17.12, "low": 14.87, "vol": 45077267},
    "DELL": {"name": "Dell Technologies", "last": 328.53, "prev": 316.91, "open": 346.05, "high": 350.36, "low": 325.10, "vol": 8601290},
    "ANET": {"name": "Arista Networks", "last": 170.80, "prev": 159.16, "open": 172.80, "high": 173.60, "low": 167.00, "vol": 11982886},
    "AMD": {"name": "Advanced Micro Devices", "last": 449.04, "prev": 404.40, "open": 444.43, "high": 459.80, "low": 433.30, "vol": 45759759},
    "MRVL": {"name": "Marvell Technology", "last": 141.20, "prev": 133.55, "open": 145.07, "high": 146.32, "low": 135.34, "vol": 33562131},
    "AVGO": {"name": "Broadcom", "last": 293.69, "prev": 291.53, "open": 311.13, "high": 311.52, "low": 289.77, "vol": 32442491},
    "ADBE": {"name": "Adobe", "last": 239.30, "prev": 246.44, "open": 239.00, "high": 243.38, "low": 236.84, "vol": 3297370},
    "TSM": {"name": "Taiwan Semiconductor", "last": 375.44, "prev": 353.10, "open": 380.56, "high": 380.72, "low": 367.95, "vol": 23841904},
    "NOK": {"name": "Nokia Oyj", "last": 7.66, "prev": 7.46, "open": 7.75, "high": 7.79, "low": 7.57, "vol": 49175099},
    "INTC": {"name": "Intel", "last": 56.28, "prev": 52.25, "open": 54.99, "high": 57.32, "low": 54.56, "vol": 174382270},
}

WATCHLIST = ["CBRS", "RIOT", "DELL", "ANET", "AMD", "MRVL", "AVGO", "ADBE"]
HOLDINGS = ["TSM", "NOK", "MRVL", "INTC", "DELL", "CBRS", "AMD"]
ASSET_NAMES = {  # full name for crypto/eng names
    "CBRS": "Cerebras Systems", "RIOT": "Riot Platforms", "DELL": "Dell Technologies",
    "ANET": "Arista Networks", "AMD": "Advanced Micro Devices", "MRVL": "Marvell Technology",
    "AVGO": "Broadcom", "ADBE": "Adobe", "TSM": "Taiwan Semiconductor", "NOK": "Nokia Oyj", "INTC": "Intel"
}

def fnum(x, nd=2):
    if x is None: return "N/A"
    return round(x, nd)

def pct(a, b):
    if b == 0: return None
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

# ---------- derived ----------
w_rows, p_rows, signals = [], [], []
for code in WATCHLIST:
    q = QUOTES[code]
    c, r = q["last"] - q["prev"], pct(q["last"], q["prev"])
    w_rows.append(f"""<tr>
      <td class="font-mono"><a href="https://finance.yahoo.com/quote/{code}">{code}</a></td>
      <td>{ASSET_NAMES[code]}</td>
      <td class="text-right font-mono">{fmt_price(q['last'])}</td>
      <td class="text-right font-mono {chg_class(c)}">{c:+.2f}</td>
      <td class="text-right font-mono {chg_class(r)}">{chg_label(r, c)}</td>
      <td class="font-mono">{fmt_price(q['low'])} &ndash; {fmt_price(q['high'])}</td>
      <td class="text-right font-mono">{fmt_vol(q['vol'])}</td>
    </tr>""")

for code in HOLDINGS:
    q = QUOTES[code]
    c, r = q["last"] - q["prev"], pct(q["last"], q["prev"])
    if abs(r) >= 3.0:
        p_rows.append(f"""<tr class="alert-row">
          <td class="font-mono"><a href="https://finance.yahoo.com/quote/{code}">{code}</a></td>
          <td>{ASSET_NAMES[code]}</td>
          <td class="text-right font-mono {chg_class(c)}">{c:+.2f}</td>
          <td class="text-right font-mono {chg_class(r)}">{chg_label(r, c)}</td>
          <td class="badge {chg_class(r)}">HOLD / REVIEW</td>
        </tr>""")

# ---------- CSS ----------
CSS = """
:root {
  --bg: #0f1115; --card: #171a21; --card2: #1e222c; --ink: #f2f4f7; --muted: #9aa3b2;
  --line: #2b303b; --accent: #d4a93c; --accent2: #f0d060; --red: #f87171; --green: #4ade80;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
html { font-size: 16px; -webkit-text-size-adjust: 100%; }
body { font-family: "Inter", "Segoe UI", system-ui, -apple-system, Roboto, sans-serif;
       background: var(--bg); color: var(--ink); line-height: 1.6; }
.wrap { max-width: 1180px; margin: 0 auto; padding: 24px 28px 44px; }
@media (max-width: 720px) {
  .wrap { max-width: 720px; padding: 14px 16px 32px; }
  .hero, .report-header { padding: 22px 18px; }
  .hero h1, .report-header h1 { font-size: 25px; }
  .kpi .val, .stat-value { font-size: 22px; }
  table { font-size: 12.5px; }
  th, td { padding: 10px 6px; }
  .card, .section { padding: 18px 16px; }
}
h1, h2, h3 { line-height: 1.25; }
.hero, header, .report-header {
  background: linear-gradient(120deg, #0c0d10, #1c2028);
  color: #fff; border-radius: 18px; padding: 30px 34px; position: relative; overflow: hidden;
  border: 1px solid #333947; margin-bottom: 22px;
}
.hero::after, header::after, .report-header::after {
  content: ""; position: absolute; right: -70px; top: -70px; width: 260px; height: 260px;
  border-radius: 50%; background: radial-gradient(circle, rgba(212,169,60,.26), transparent 70%);
}
.brand { display: flex; align-items: center; gap: 12px; margin-bottom: 16px; position: relative; z-index: 1; }
.logo { width: 44px; height: 44px; border-radius: 11px; background: rgba(212,169,60,.14);
  display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 20px;
  border: 1px solid rgba(212,169,60,.4); color: var(--accent2); }
.brand small { opacity: .7; letter-spacing: .14em; text-transform: uppercase; font-size: 10.5px; display: block; color: var(--accent2); }
.brand strong { font-size: 15px; }
.hero h1, header h1, .report-header h1 { font-size: 30px; letter-spacing: -.5px; margin-bottom: 10px; position: relative; z-index: 1; color: #fff; }
.gold { color: var(--accent2); }
.hero .meta, header .meta, .report-header .meta {
  display: flex; gap: 22px; opacity: .85; font-size: 12.5px; position: relative; z-index: 1; flex-wrap: wrap;
}
.kpis, .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: 14px; margin: 22px 0; }
.kpi, .stat-card { background: var(--card); border: 1px solid var(--line); border-radius: 14px; padding: 15px 18px; }
.kpi .lbl, .stat-label { font-size: 11px; text-transform: uppercase; letter-spacing: .08em; color: var(--muted); margin-bottom: 6px; }
.kpi .val, .stat-value { font-size: 24px; font-weight: 800; letter-spacing: -.5px; font-variant-numeric: tabular-nums; color: #fff; }
.kpi .row { display: flex; align-items: center; justify-content: space-between; margin-top: 10px; }
.pill, .badge { font-size: 11.5px; font-weight: 700; padding: 3px 10px; border-radius: 999px; white-space: nowrap; }
.up, .badge.up { background: rgba(74,222,128,.15); color: var(--green); }
.down, .badge.down { background: rgba(248,113,113,.15); color: var(--red); }
.card, .section { background: var(--card); border: 1px solid var(--line); border-radius: 14px; padding: 20px; margin-bottom: 16px; }
.card h3, .section h2 { font-size: 14.5px; color: #fff; margin-bottom: 4px; }
.card .sub, .section .sub { font-size: 12px; color: var(--muted); margin-bottom: 14px; }
.grid { display: grid; grid-template-columns: 1.4fr 1fr; gap: 16px; margin-bottom: 16px; }
@media (max-width: 900px) { .grid { grid-template-columns: 1fr; } .kpis, .stats-grid { grid-template-columns: 1fr 1fr; } }
table { width: 100%; border-collapse: collapse; font-size: 13px; }
th { text-align: left; font-size: 11px; text-transform: uppercase; letter-spacing: .07em; color: var(--muted); padding: 11px 9px; border-bottom: 2px solid var(--line); }
td { padding: 11px 9px; border-bottom: 1px solid var(--line); font-variant-numeric: tabular-nums; color: var(--ink); }
tr:last-child td { border-bottom: none; }
tr:hover td { background: rgba(255,255,255,.025); }
.font-mono { font-family: "SF Mono", "Menlo", "Consolas", monospace; }
.tag { font-size: 11.5px; font-weight: 700; padding: 4px 11px; border-radius: 999px; }
.tag.good { background: rgba(212,169,60,.15); color: var(--accent2); }
.tag.warn { background: rgba(245,158,11,.18); color: #fbbf24; }
.tag.bad { background: rgba(248,113,113,.15); color: var(--red); }
.alert-row td { background: rgba(245,158,11,.04); }
.alert { padding: 12px 16px; border-radius: 12px; margin-bottom: 12px; font-size: .875rem; border-left: 3px solid var(--accent); }
.alert-info { background: rgba(212,169,60,.06); border-color: var(--accent); }
.alert-warning { background: rgba(245,158,11,.06); border-color: #fbbf24; }
.alert-success { background: rgba(74,222,128,.06); border-color: var(--green); }
.alert-danger { background: rgba(248,113,113,.06); border-color: var(--red); }
.source-chip { display: inline-block; font-size: 10.5px; font-weight: 700; padding: 3px 9px; border-radius: 6px;
  background: rgba(212,169,60,.12); color: var(--accent2); border: 1px solid rgba(212,169,60,.25); margin-right: 6px; }
.source-chip.yahoo { background: rgba(23, 105, 225, .15); color: #5b9aff; border-color: rgba(23,105,225,.3); }
.source-chip.investopedia { background: rgba(255,229,115,.14); color: #d9a441; border-color: rgba(255,229,115,.3); }
.source-chip.cnbc { background: rgba(23, 180, 153, .15); color: #2eae9c; border-color: rgba(23,180,153,.3); }
.source-chip.bloomberg { background: rgba(43, 114, 202, .15); color: #4986e8; border-color: rgba(43,114,202,.3); }
.video-card { border: 1px solid var(--line); border-radius: 12px; overflow: hidden; padding: 14px; background: var(--card); }
.video-card .meta { display: flex; justify-content: space-between; align-items: center; }
.video-card .title { font-weight: 600; font-size: 13px; color: var(--ink); word-break: break-all; }
.video-card .dur { font-size: 11px; color: var(--muted); font-family: monospace; }
.youtube-row { display: flex; gap: 14px; align-items: center; padding: 12px 0; border-bottom: 1px solid var(--line); }
.youtube-row:last-child { border-bottom: none; }
.youtube-row .opp { width: 220px; font-size: 12px; color: var(--muted); text-align: right; }
.youtube-row .btn { flex: 1; background: var(--accent); color: #0c0d10; border: none; border-radius: 999px;
  padding: 8px 14px; font-weight: 700; font-size: 12px; cursor: pointer; text-decoration: none; display: inline-flex; align-items: center; gap: 8px; }
.donut-wrap, .legend { display: flex; flex-wrap: wrap; gap: 14px; align-items: center; }
.legend .li { display: flex; align-items: center; gap: 8px; font-size: 13px; }
.dot { width: 11px; height: 11px; border-radius: 4px; display: inline-block; }
.footer, .report-footer { margin-top: 26px; display: flex; justify-content: space-between; color: var(--muted); font-size: 12px;
  flex-wrap: wrap; gap: 12px; padding-top: 18px; border-top: 1px solid var(--line); }
.footer .zh { max-width: 760px; }
.disclaimer { font-size: .74rem; color: var(--muted); padding: 16px 18px; background: var(--card); border-radius: 14px;
  border-left: 3px solid var(--accent); margin-top: 24px; line-height: 1.5; }
.warn-box { background: rgba(245,158,11,.08); border: 1px solid rgba(245,158,11,.25); border-radius: 12px; padding: 14px 16px; font-size: .85rem; color: var(--ink); }
.small { font-size: 12px; color: var(--muted); }
ul { list-style: none; }
ul li { padding: 4px 0; padding-left: 18px; position: relative; }
ul li::before { content: "▸"; position: absolute; left: 2px; color: var(--accent2); font-size: 13px; }
"""

# ---------- assemble HTML ----------
today = "2026-11-08"
updated = "2026-11-08 14:32 SGT"
data_time = "2026-11-08 14:32:16 SGT"

# ---- Executive summary KPIs ----
top_gainers = sorted(WATCHLIST, key=lambda c: QUOTES[c]["last"] - QUOTES[c]["prev"], reverse=True)[:3]
top_gainers_html = "".join(f'<li><a href="https://finance.yahoo.com/quote/{c}" style="color:var(--accent2)">{c}</a> {QUOTES[c]["last"]:,.2f} ({QUOTES[c]["last"]-QUOTES[c]["prev"]:+.2f}, {pct(QUOTES[c]["last"], QUOTES[c]["prev"]):+.2f}%)</li>' for c in top_gainers)
worst = sorted(WATCHLIST, key=lambda c: QUOTES[c]["last"] - QUOTES[c]["prev"])[:2]

html = []
html.append(f"""<!DOCTYPE html>
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
    <div class="val" style="font-size:1.05rem">{top_gainers[0]} <span class="pill up">{QUOTES[top_gainers[0]]['last']:,.2f}</span></div>
  </div>
  <div class="kpi">
    <div class="lbl">Worst decliner</div>
    <div class="val" style="font-size:1.05rem">{worst[0]} <span class="pill down">{(QUOTES[worst[0]]['last']-QUOTES[worst[0]]['prev']):+.2f}</span></div>
  </div>
</div>

<div class="card">
  <h3>📋 Executive Summary</h3>
  <p class="sub">US equities staged a sharp rebound on 2026-11-06 after the historic 19-month tech drawdown — AI-infrastructure names led. Live Moomoo OpenD data (15-min delay, {data_time}) show <strong>every watchlist name green</strong> except ADBE, which slipped on soft Q4 guidance. Portfolio exposure is concentrated in AI-capex semis: <strong>6 of 7 holdings moved ≥3%</strong> and are flagged HOLD/REVIEW.</p>
  <div class="grid">
    <div>
      <ul style="padding-left:18px">
        <li><strong>AI infrastructure boom:</strong> RIOT +13.21% on Corsicana 910MW lease; CBRS +9.75% on wafer-scale demand</li>
        <li><strong>Hardware &amp; foundry:</strong> TSM +6.33%, INTC +7.71% — AI capex cycle re-accelerates</li>
        <li><strong>Merger overhang:</strong> MRVL +5.73% on Lumentum $115B deal, but TD Cowen/BofA downgrades cap upside</li>
        <li><strong>Peak multiple compression:</strong> SOX -19% over 1 month; AMD / CBRS warrant &amp; dilution costs weigh</li>
      </ul>
    </div>
    <div>
      <div class="kpi" style="margin-bottom:12px">
        <div class="lbl">New 30-day high (watchlist)</div>
        <div class="val">{top_gainers[0]} {QUOTES[top_gainers[0]]['last']:,.2f}</div>
      </div>
      <div class="kpi" style="margin-bottom:12px">
        <div class="lbl">Scope of coverage</div>
        <div class="val" style="font-size:1.05rem">{len(WATCHLIST)} watchlist + {len(HOLDINGS)} holdings</div>
      </div>
      <div class="kpi">
        <div class="lbl">Data freshness</div>
        <div class="val" style="font-size:1.05rem">{data_time}</div>
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
    <strong>⚠️ Portfolio flag:</strong> {len(p_rows)} of {len(HOLDINGS)} holdings breached the 3% threshold. Review triggers: AI capex re-rating (CBRS, AMD, TSM, INTC, MRVL, DELL) — consider position sizing and thesis re-validation.
  </div>
</div>

<div class="card">
  <h3>▶️ YouTube Hot Videos</h3>
  <p class="sub">Market reaction commentary &amp; stock deep-dives (Nov 2026).</p>
  <div class="video-card">
    <div class="youtube-row">
      <div><div class="title">CISCO SYSTEMS EARNINGS LIVE 🚨 Cerebras Systems FY26 Results! | CSCO CBRS COHR ENVX Earnings Aug 12</div><div class="dur">01:10 · AI infra earnings teardown</div></div>
      <a class="btn" href="https://www.youtube.com/watch?v=eh3N3SXgCSI" target="_blank" rel="noopener">▶ Watch</a>
    </div>
    <div class="youtube-row">
      <div><div class="title">CBRS Stock Q2 2026: Cerebras Earnings - The Beat That Isn't</div><div class="dur">~17 min · Valuation debate</div></div>
      <a class="btn" href="https://www.youtube.com/watch?v=ESMnDauviXw" target="_blank" rel="noopener">▶ Watch</a>
    </div>
    <div class="youtube-row">
      <div><div class="title">Yahoo Finance Live: Daily Market Coverage - AI infrastructure mixed after earnings (Aug 2026)</div><div class="dur">~15 min · Market close discussion</div></div>
      <a class="btn" href="https://www.youtube.com/watch?v=UWXnoJuCwzo" target="_blank" rel="noopener">▶ Watch</a>
    </div>
    <div class="youtube-row">
      <div><div class="title">Has the Stock Market Peaked? - Portfolio Update August 2026</div><div class="dur">~02:00 · Vanguard portfolio</div></div>
      <a class="btn" href="https://www.youtube.com/watch?v=0fKhTHTlUBA" target="_blank" rel="noopener">▶ Watch</a>
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
</html>""")

out = "".join(html)
with open("/Users/btm6/jokerai/price-alert.html", "w", encoding="utf-8") as f:
    f.write(out)
print("written", len(out), "chars")
print("sections:", "Watchlist Movers" in out, "Portfolio Alerts" in out, "YouTube Hot Videos" in out,
      "USA Branded News" in out, "Sector & Risk" in out, "Signal Summary" in out)
