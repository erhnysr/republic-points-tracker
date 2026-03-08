#!/usr/bin/env python3
"""
Republic Points Tracker - Real-time validator points tracking
Author: erhnysr | github.com/erhnysr
"""
from flask import Flask, render_template_string
import requests, json
from datetime import datetime

app = Flask(__name__)

REST_URL = "http://localhost:1317"

def get_validators():
    try:
        r = requests.get(f"{REST_URL}/cosmos/staking/v1beta1/validators?status=BOND_STATUS_BONDED&pagination.limit=100", timeout=10)
        if r.status_code == 200:
            return r.json().get("validators", [])
    except:
        pass
    return []

TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Republic Points Tracker</title>
    <meta http-equiv="refresh" content="30">
    <style>
        *{box-sizing:border-box;margin:0;padding:0}
        body{font-family:'Segoe UI',Arial;background:#0d1117;color:#c9d1d9;padding:20px}
        h1{color:#00d4ff;margin-bottom:20px;font-size:28px}
        .grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:15px;margin-bottom:20px}
        .card{background:#161b22;padding:20px;border-radius:10px;border:1px solid #30363d}
        .card h3{color:#8b949e;font-size:12px;text-transform:uppercase;margin-bottom:8px}
        .stat{font-size:32px;font-weight:bold;color:#00d4ff}
        table{width:100%;border-collapse:collapse;background:#161b22;border-radius:10px;overflow:hidden}
        th{background:#21262d;padding:12px;text-align:left;color:#8b949e;font-size:12px;text-transform:uppercase}
        td{padding:12px;border-top:1px solid #30363d}
        tr:hover{background:#1c2128}
        .bonded{color:#00ff88}.jailed{color:#ff4444}
        .rank{font-weight:bold;color:#ffd700}
        .footer{margin-top:20px;color:#8b949e;font-size:12px}
    </style>
</head>
<body>
    <h1>📊 Republic Points Tracker</h1>
    <div class="grid">
        <div class="card"><h3>Total Validators</h3><div class="stat">{{ total }}</div></div>
        <div class="card"><h3>Total Staked</h3><div class="stat">{{ total_staked }}</div></div>
        <div class="card"><h3>Jailed</h3><div class="stat" style="color:#ff4444">{{ jailed }}</div></div>
        <div class="card"><h3>Updated</h3><div class="stat" style="font-size:14px;margin-top:8px">{{ updated }}</div></div>
    </div>
    <table>
        <tr><th>Rank</th><th>Moniker</th><th>Status</th><th>Tokens (RAI)</th><th>Commission</th></tr>
        {% for v in validators %}
        <tr>
            <td class="rank">#{{ loop.index }}</td>
            <td>{{ v.moniker }}{% if v.moniker == "ERHANREPU" %} ⭐{% endif %}</td>
            <td class="{{ "jailed" if v.jailed else "bonded" }}">{{ "🔴 Jailed" if v.jailed else "🟢 Active" }}</td>
            <td>{{ v.tokens }}</td>
            <td>{{ v.commission }}%</td>
        </tr>
        {% endfor %}
    </table>
    <div class="footer">Built by erhnysr | github.com/erhnysr/republic-points-tracker | Auto-refreshes every 30s</div>
</body>
</html>
'''

@app.route('/')
def index():
    vals = get_validators()
    sorted_vals = sorted(vals, key=lambda x: int(x.get("tokens", 0)), reverse=True)
    formatted = []
    for v in sorted_vals:
        try:
            tokens = f"{int(v.get('tokens',0))/1e18:,.2f}"
            commission = f"{float(v.get('commission',{}).get('commission_rates',{}).get('rate',0))*100:.1f}"
        except:
            tokens = "0"
            commission = "0"
        formatted.append({"moniker": v.get("description",{}).get("moniker","?"), "jailed": v.get("jailed", False), "tokens": tokens, "commission": commission})
    total_staked = sum(int(v.get("tokens",0)) for v in vals)
    return render_template_string(TEMPLATE,
        validators=formatted,
        total=len(vals),
        total_staked=f"{total_staked/1e18:,.0f} RAI",
        jailed=sum(1 for v in vals if v.get("jailed")),
        updated=datetime.utcnow().strftime("%H:%M UTC"))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
