#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""NEXUS Detail Page Generator — convert akun .txt -> HTML bagus.
Di-cron tiap menit: scan /var/www/html/*.txt, generate .html baru/berubah."""
import os, re, glob, html as H
import urllib.parse

SRC_DIR = "/var/www/html"
TPL = """<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="referrer" content="no-referrer">
<title>__TITLE__ · NEXUS TUNNELING</title>
<style>
:root{--bg:#0a0a0a;--card:#141414;--line:#262626;--txt:#f2f2f2;--dim:#8a8a8a;--acc:#ffffff}
*{margin:0;padding:0;box-sizing:border-box}
body{background:var(--bg);color:var(--txt);font-family:'Segoe UI',system-ui,-apple-system,sans-serif;min-height:100vh;display:flex;align-items:center;justify-content:center;padding:24px}
.wrap{width:100%;max-width:560px}
.brand{border:1px solid var(--line);background:var(--card);padding:14px 18px;text-align:center;margin-bottom:14px}
.brand h1{font-size:15px;letter-spacing:6px;font-weight:700}
.brand span{display:block;font-size:10px;letter-spacing:3px;color:var(--dim);margin-top:4px}
.card{border:1px solid var(--line);background:var(--card);padding:22px}
.card h2{font-size:13px;letter-spacing:2px;color:var(--dim);font-weight:600;text-transform:uppercase;margin-bottom:16px;padding-bottom:10px;border-bottom:1px solid var(--line)}
.row{display:flex;justify-content:space-between;gap:12px;padding:7px 0;font-size:13.5px;border-bottom:1px dashed rgba(255,255,255,.06)}
.row:last-child{border-bottom:none}
.row .k{color:var(--dim);white-space:nowrap}
.row .v{color:var(--txt);text-align:right;word-break:break-all;font-weight:600}
.sec{margin-top:18px}
.sec h2{margin-top:0}
.links .row{align-items:flex-start;flex-direction:column;gap:4px}
.links .tag{font-size:10px;letter-spacing:2px;color:var(--dim);text-transform:uppercase;font-weight:700}
.links .lk{font-family:ui-monospace,'Cascadia Code',Consolas,monospace;font-size:11.5px;color:#e8e8e8;background:#0d0d0d;border:1px solid var(--line);padding:8px 10px;word-break:break-all;line-height:1.5;display:block;width:100%}
.btn{display:inline-flex;align-items:center;gap:6px;border:1px solid var(--acc);background:transparent;color:var(--acc);font-size:11px;letter-spacing:2px;padding:6px 14px;cursor:pointer;text-transform:uppercase;font-weight:700;margin-top:10px;transition:.15s}
.btn:hover{background:var(--acc);color:#000}
.exp{border:1px solid var(--line);background:#0d0d0d;padding:10px 14px;display:flex;justify-content:space-between;font-size:13px;margin-top:14px}
.exp .k{color:var(--dim)}
.foot{margin-top:14px;text-align:center;font-size:10.5px;color:var(--dim);letter-spacing:2px}
.ok{color:#fff;font-weight:700}
@media(max-width:480px){body{padding:12px}.card{padding:16px}}
</style>
</head>
<body>
<div class="wrap">
  <div class="brand"><h1>NEXUS TUNNELING</h1><span>__SUBTITLE__</span></div>
  <div class="card">
    <h2>Account Info</h2>
    __INFO_ROWS__
    <div class="sec links">
      <h2>Configuration Links</h2>
      __LINK_ROWS__
    </div>
    <div class="exp"><span class="k">EXPIRED</span><span class="ok">__EXP__</span></div>
  </div>
  <div class="foot">NEXUS TUNNELING · VPN DETAIL PAGE · V2.4</div>
</div>
<script>
function cp(t,e){navigator.clipboard.writeText(t).then(function(){var o=e.textContent;e.textContent='COPIED';setTimeout(function(){e.textContent=o},1200)})}
</script>
</body>
</html>"""

def esc(s):
    return H.escape(str(s), quote=True)

def convert(path):
    lines = [l.rstrip() for l in open(path, encoding='utf-8', errors='replace').read().splitlines()]
    title = None
    info, links = [], []
    cur_link_tag = None
    for l in lines:
        m = re.match(r'^([A-Za-z][A-Za-z0-9 /]*)\s*:\s*(.+)$', l)
        if m and 'vmess://' not in l and 'vless://' not in l and 'trojan://' not in l and 'ss://' not in l:
            k, v = m.group(1).strip(), m.group(2).strip()
            if k.lower() in ('tls', 'ntls', 'grpc', 'xhttp', 'ws-xhttp', 'up', 'uptls', 'upntls', 'none', 'multi', 'stn', 'tlsxhttp', 'grpcxhttp', 'reality', 'any'):
                links.append((k.upper(), v))
            elif k.lower() == 'exp':
                exp = v
            else:
                if k.lower() in ('host', 'domain', 'server'):
                    title_host = v
                info.append((k, v))
        elif re.match(r'^(vmess|vless|trojan|ss)://', l.strip()):
            links.append((cur_link_tag or 'LINK', l.strip()))
        elif l.strip() and not set(l.strip()) <= set('-─='):
            if not title:
                title = l.strip()
    # fallback title
    if not title:
        title = os.path.basename(path).replace('.txt', '')

    # info rows
    rows = "".join(f'<div class="row"><span class="k">{esc(k)}</span><span class="v">{esc(v)}</span></div>' for k, v in info)
    # link rows
    lrows = ""
    for tag, url in links:
        u = esc(url)
        lrows += (f'<div class="row"><span class="tag">{esc(tag)}</span>'
                  f'<a class="lk" href="#" onclick="return false">{u}</a>'
                  f'<button class="btn" onclick="cp(\'{u}\',this)">Copy</button></div>')
    if not lrows:
        lrows = '<div class="row"><span class="v">No links</span></div>'

    proto = "VMESS" if "vmess" in path.lower() else ("VLESS" if "vless" in path.lower() else ("TROJAN" if "trojan" in path.lower() else "VPN"))
    out = TPL.replace("__TITLE__", esc(title)) \
             .replace("__SUBTITLE__", f"{proto} ACCOUNT DETAIL") \
             .replace("__INFO_ROWS__", rows) \
             .replace("__LINK_ROWS__", lrows) \
             .replace("__EXP__", esc(exp if 'exp' in dir() else '-'))
    return out

def main():
    n = 0
    for txt in glob.glob(os.path.join(SRC_DIR, "*.txt")):
        if 'readme' in txt.lower():
            continue
        html_path = txt[:-4] + ".html"
        try:
            if os.path.exists(html_path) and os.path.getmtime(html_path) >= os.path.getmtime(txt):
                continue
            open(html_path, "w", encoding="utf-8").write(convert(txt))
            n += 1
        except Exception as e:
            print("ERR", txt, e)
    print(f"generated {n} html")

if __name__ == "__main__":
    main()
