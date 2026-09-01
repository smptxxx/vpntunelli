#!/usr/bin/env python3
# VPN Tunneling REST API Server
# Run on 127.0.0.1:2500 behind nginx
import http.server
import json
import os
import re
import subprocess
import uuid as uuidlib
import urllib.parse
import datetime
import threading

HOST = "127.0.0.1"
PORT = 2500
XRAY_CONFIG = "/etc/xray/config.json"
DOMAIN_FILE = "/etc/xray/domain"
AUTH_FILE = "/etc/xray/apikey"

# ---------- helpers ----------

def sh(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True)

def get_domain():
    try:
        return open(DOMAIN_FILE).read().strip()
    except Exception:
        return ""

def get_apikey():
    try:
        return open(AUTH_FILE).read().strip()
    except Exception:
        return ""

def gen_uuid():
    return str(uuidlib.uuid4())

def days_to_date(days):
    d = datetime.date.today() + datetime.timedelta(days=int(days))
    return d.isoformat()

def sanitize_user(u):
    return re.sub(r"[^a-zA-Z0-9_-]", "", u or "")[:32]

def valid_auth(params):
    auth = params.get("auth", [""])[0]
    return auth and auth == get_apikey()

def add_days_marker(marker, comment_line, json_line):
    """Insert user entry after marker line in xray config."""
    with open(XRAY_CONFIG, "r") as f:
        lines = f.readlines()
    out = []
    inserted = False
    for line in lines:
        out.append(line)
        if line.strip() == marker and not inserted:
            out.append(comment_line + "\n")
            out.append(json_line + "\n")
            inserted = True
    with open(XRAY_CONFIG, "w") as f:
        f.writelines(out)
    return inserted

def restart_xray():
    sh("systemctl restart xray")

def set_iplimit(proto, user, limit):
    base = f"/etc/kyt/limit/{proto}/ip"
    os.makedirs(base, exist_ok=True)
    if int(limit) > 0:
        open(f"{base}/{user}", "w").write(str(limit))
    else:
        try:
            os.remove(f"{base}/{user}")
        except FileNotFoundError:
            pass

def set_quota(proto, user, quota_gb):
    base = f"/etc/{proto}"
    os.makedirs(base, exist_ok=True)
    c = int(quota_gb or 0)
    if c > 0:
        open(f"{base}/{user}", "w").write(str(c * 1024 * 1024 * 1024))
    else:
        try:
            os.remove(f"{base}/{user}")
        except FileNotFoundError:
            pass

def get_iplimit(proto, user):
    try:
        return int(open(f"/etc/kyt/limit/{proto}/ip/{user}").read().strip() or 0)
    except Exception:
        return 0

def get_quota(proto, user):
    try:
        v = int(open(f"/etc/{proto}/{user}").read().strip())
        return round(v / (1024 ** 3), 2)
    except Exception:
        return 0

def db_read(proto):
    path = f"/etc/{proto}/.{proto}.db"
    rows = []
    try:
        for line in open(path).read().splitlines():
            if line.startswith("###"):
                parts = line.split()
                if len(parts) >= 3:
                    rows.append({"user": parts[1], "exp": parts[2], "key": parts[3] if len(parts) > 3 else ""})
    except FileNotFoundError:
        pass
    return rows

def db_write(proto, rows):
    path = f"/etc/{proto}/.{proto}.db"
    with open(path, "w") as f:
        f.write("& plughin Account\n")
        for r in rows:
            f.write(f"### {r['user']} {r['exp']} {r['key']}\n")

def db_find(proto, user):
    for r in db_read(proto):
        if r["user"] == user:
            return r
    return None

def xray_remove_user(marker_re):
    """Remove comment line + the JSON line following it, matching regex."""
    with open(XRAY_CONFIG, "r") as f:
        lines = f.readlines()
    out, skip_next = [], False
    for line in lines:
        if skip_next:
            skip_next = False
            continue
        if re.search(marker_re, line):
            skip_next = True  # remove the JSON entry line after comment
            continue
        out.append(line)
    with open(XRAY_CONFIG, "w") as f:
        f.writelines(out)

def httpup_links(proto, user, key):
    domain = get_domain()
    if proto == "vless":
        return f"vless://{key}@{domain}:443?path=/vless-xhttp&security=tls&encryption=none&host={domain}&type=xhttp&sni={domain}#{user}"
    if proto == "vmess":
        import base64
        vm = {"v": "2", "ps": user, "add": domain, "port": "443", "id": key, "aid": "0",
              "net": "xhttp", "path": "/vmess-xhttp", "type": "none", "host": domain, "tls": "tls"}
        return "vmess://" + base64.b64encode(json.dumps(vm).encode()).decode()
    if proto == "trojan":
        return f"trojan://{key}@{domain}:443?path=/trojan-xhttp&security=tls&host={domain}&type=xhttp&sni={domain}#{user}"
    return ""

def legacy_links(proto, user, key):
    domain = get_domain()
    res = {}
    if proto == "vmess":
        import base64
        ws = {"v": "2", "ps": user, "add": domain, "port": "443", "id": key, "aid": "0",
              "net": "ws", "path": "/vmess", "type": "none", "host": domain, "tls": "tls"}
        nt = dict(ws, port="80", tls="none")
        gc = {"v": "2", "ps": user, "add": domain, "port": "443", "id": key, "aid": "0",
              "net": "grpc", "path": "vmess-grpc", "type": "none", "host": domain, "tls": "tls"}
        res["tls"] = "vmess://" + base64.b64encode(json.dumps(ws).encode()).decode()
        res["ntls"] = "vmess://" + base64.b64encode(json.dumps(nt).encode()).decode()
        res["grpc"] = "vmess://" + base64.b64encode(json.dumps(gc).encode()).decode()
    elif proto == "vless":
        res["tls"] = f"vless://{key}@{domain}:443?path=/vless&security=tls&encryption=none&host={domain}&type=ws&sni={domain}#{user}"
        res["ntls"] = f"vless://{key}@{domain}:80?path=/vless&encryption=none&type=ws&host={domain}#{user}"
        res["grpc"] = f"vless://{key}@{domain}:443?mode=gun&security=tls&encryption=none&authority={domain}&type=grpc&serviceName=vless-grpc&sni={domain}#{user}"
    elif proto == "trojan":
        res["tls"] = f"trojan://{key}@{domain}:443?path=/trojan-ws&security=tls&host={domain}&type=ws&sni={domain}#{user}"
        res["grpc"] = f"trojan://{key}@{domain}:443?mode=gun&security=tls&authority={domain}&type=grpc&serviceName=trojan-grpc&sni={domain}#{user}"
    return res

# ---------- account ops ----------

def create_xray_account(proto, user, exp_days, limitip, quota):
    user = sanitize_user(user)
    if not user:
        return {"status": "error", "message": "invalid username"}
    if db_find(proto, user):
        return {"status": "error", "message": f"username {user} already exists"}
    key = gen_uuid()
    exp = days_to_date(exp_days)
    markers = {"vmess": ("#vmess", "#vmessgrpc", "#vmessxhttp"),
               "vless": ("#vless", "#vlessgrpc", "#vlessxhttp"),
               "trojan": ("#trojanws", "#trojangrpc", "#trojanxhttp")}
    m = markers.get(proto)
    if not m:
        return {"status": "error", "message": "unknown protocol"}
    if proto == "vmess":
        entry = '}},{{"id": "{key}","alterId": 0,"email": "{user}"'.format(key=key, user=user)
    elif proto == "vless":
        entry = '}},{{"id": "{key}","email" : "{user}"'.format(key=key, user=user)
    else:
        entry = '}},{{"password": "{key}","email": "{user}"'.format(key=key, user=user)
    prefix = {"vmess": "###", "vless": "#&", "trojan": "#!"}[proto]
    for marker in m:
        add_days_marker(marker, f"{prefix} {user} {exp}", entry)
    rows = db_read(proto)
    rows.append({"user": user, "exp": exp, "key": key})
    db_write(proto, rows)
    set_iplimit(proto, user, limitip)
    set_quota(proto, user, quota)
    restart_xray()
    return {
        "status": "success", "message": f"account {user} created",
        "data": {
            "user": user, "uuid": key, "exp": exp,
            "limitip": int(limitip), "quota": f"{quota}GB",
            "xhttp": httpup_links(proto, user, key),
            "links": legacy_links(proto, user, key),
        },
    }

def delete_xray_account(proto, user):
    user = sanitize_user(user)
    row = db_find(proto, user)
    if not row:
        return {"status": "error", "message": "account not found"}
    prefix = {"vmess": "###", "vless": "#&", "trojan": "#!"}[proto]
    xray_remove_user(r"^\s*" + re.escape(prefix) + r"\s+" + re.escape(user) + r"\s")
    rows = [r for r in db_read(proto) if r["user"] != user]
    db_write(proto, rows)
    set_iplimit(proto, user, 0)
    set_quota(proto, user, 0)
    restart_xray()
    return {"status": "success", "message": f"account {user} deleted"}

def list_xray_accounts(proto):
    rows = db_read(proto)
    domain = get_domain()
    for r in rows:
        r["limitip"] = get_iplimit(proto, r["user"])
        r["quota_gb"] = get_quota(proto, r["user"])
    return {"status": "success", "domain": domain, "total": len(rows), "accounts": rows}

def renew_xray_account(proto, user, exp_days):
    user = sanitize_user(user)
    row = db_find(proto, user)
    if not row:
        return {"status": "error", "message": "account not found"}
    exp = days_to_date(exp_days)
    with open(XRAY_CONFIG) as f:
        cfg = f.read()
    prefix = {"vmess": "###", "vless": "#&", "trojan": "#!"}[proto]
    cfg = re.sub(rf"^{prefix} {re.escape(user)} \S+", f"{prefix} {user} {exp}", cfg, flags=re.M)
    open(XRAY_CONFIG, "w").write(cfg)
    rows = db_read(proto)
    for r in rows:
        if r["user"] == user:
            r["exp"] = exp
    db_write(proto, rows)
    restart_xray()
    return {"status": "success", "message": f"account {user} renewed", "data": {"user": user, "exp": exp}}

def edit_xray_account(proto, user, limitip=None, quota=None):
    user = sanitize_user(user)
    row = db_find(proto, user)
    if not row:
        return {"status": "error", "message": "account not found"}
    if limitip is not None:
        set_iplimit(proto, user, limitip)
    if quota is not None:
        set_quota(proto, user, quota)
    return {"status": "success",
            "data": {"user": user, "limitip": get_iplimit(proto, user), "quota_gb": get_quota(proto, user)}}

# ---------- SSH ops ----------

def create_ssh_account(user, password, exp_days, limitip):
    user = sanitize_user(user)
    if not user:
        return {"status": "error", "message": "invalid username"}
    if db_find("ssh", user):
        return {"status": "error", "message": f"username {user} already exists"}
    exp = days_to_date(exp_days)
    sh(f'useradd -e {exp} -s /bin/false -M {user}')
    sh(f'echo "{password}\\n{password}\\n" | passwd {user} &> /dev/null')
    rows = db_read("ssh")
    rows.append({"user": user, "exp": exp, "key": password})
    db_write("ssh", rows)
    set_iplimit("ssh", user, limitip)
    domain = get_domain()
    return {"status": "success", "message": f"account {user} created",
            "data": {"user": user, "password": password, "exp": exp, "limitip": int(limitip),
                     "ssl": f"{domain}:443@{user}:{password}",
                     "ws": f"{domain}:80@{user}:{password}",
                     "udp": f"{domain}:1-65535@{user}:{password}"}}

def delete_ssh_account(user):
    user = sanitize_user(user)
    if not db_find("ssh", user):
        return {"status": "error", "message": "account not found"}
    sh(f"userdel -r {user} 2>/dev/null || userdel {user}")
    rows = [r for r in db_read("ssh") if r["user"] != user]
    db_write("ssh", rows)
    set_iplimit("ssh", user, 0)
    return {"status": "success", "message": f"account {user} deleted"}

def list_ssh_accounts():
    rows = db_read("ssh")
    for r in rows:
        r["limitip"] = get_iplimit("ssh", r["user"])
    return {"status": "success", "total": len(rows), "accounts": rows}

def renew_ssh_account(user, exp_days):
    user = sanitize_user(user)
    if not db_find("ssh", user):
        return {"status": "error", "message": "account not found"}
    exp = days_to_date(exp_days)
    sh(f"chage -E {exp} {user}")
    rows = db_read("ssh")
    for r in rows:
        if r["user"] == user:
            r["exp"] = exp
    db_write("ssh", rows)
    return {"status": "success", "message": f"account {user} renewed", "data": {"user": user, "exp": exp}}

# ---------- HTTP handler ----------

DOC_HTML = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>VPN Tunneling API Docs</title>
<style>
body{font-family:system-ui,sans-serif;max-width:900px;margin:2rem auto;padding:0 1rem;background:#0f172a;color:#e2e8f0}
h1{color:#38bdf8}h2{color:#facc15;margin-top:2rem}
table{border-collapse:collapse;width:100%;margin:1rem 0}
td,th{border:1px solid #334155;padding:.5rem;text-align:left}
th{background:#1e293b}
code{background:#1e293b;padding:2px 6px;border-radius:4px;color:#4ade80;word-break:break-all}
</style></head><body>
<h1>VPN Tunneling REST API</h1>
<p>Auth: semua endpoint butuh parameter <code>auth=APIKEY</code> (lihat di welcome screen VPS).</p>
<p>Base URL: <code>https://DOMAIN:81/api</code> atau <code>http://DOMAIN:PORT/api</code></p>

<h2>SSH</h2>
<table>
<tr><th>Endpoint</th><th>Parameter</th></tr>
<tr><td><code>/api/trial-ssh</code></td><td>auth</td></tr>
<tr><td><code>/api/create-ssh</code></td><td>auth, user, password, exp(hari), limitip</td></tr>
<tr><td><code>/api/renew-ssh</code></td><td>auth, user, exp(hari)</td></tr>
<tr><td><code>/api/del-ssh</code></td><td>auth, user</td></tr>
<tr><td><code>/api/cek-ssh</code></td><td>auth</td></tr>
</table>

<h2>VMESS</h2>
<table>
<tr><th>Endpoint</th><th>Parameter</th></tr>
<tr><td><code>/api/trial-vmess</code></td><td>auth, quota, limitip, exp</td></tr>
<tr><td><code>/api/create-vmess</code></td><td>auth, user, quota, limitip, exp</td></tr>
<tr><td><code>/api/renew-vmess</code></td><td>auth, user, exp</td></tr>
<tr><td><code>/api/del-vmess</code></td><td>auth, user</td></tr>
<tr><td><code>/api/cek-vmess</code></td><td>auth</td></tr>
<tr><td><code>/api/edit-vmess</code></td><td>auth, user, limitip, quota</td></tr>
</table>

<h2>VLESS</h2>
<table>
<tr><th>Endpoint</th><th>Parameter</th></tr>
<tr><td><code>/api/trial-vless</code></td><td>auth, quota, limitip, exp</td></tr>
<tr><td><code>/api/create-vless</code></td><td>auth, user, quota, limitip, exp</td></tr>
<tr><td><code>/api/renew-vless</code></td><td>auth, user, exp</td></tr>
<tr><td><code>/api/del-vless</code></td><td>auth, user</td></tr>
<tr><td><code>/api/cek-vless</code></td><td>auth</td></tr>
<tr><td><code>/api/edit-vless</code></td><td>auth, user, limitip, quota</td></tr>
</table>

<h2>TROJAN</h2>
<table>
<tr><th>Endpoint</th><th>Parameter</th></tr>
<tr><td><code>/api/trial-trojan</code></td><td>auth, quota, limitip, exp</td></tr>
<tr><td><code>/api/create-trojan</code></td><td>auth, user, quota, limitip, exp</td></tr>
<tr><td><code>/api/renew-trojan</code></td><td>auth, user, exp</td></tr>
<tr><td><code>/api/del-trojan</code></td><td>auth, user</td></tr>
<tr><td><code>/api/cek-trojan</code></td><td>auth</td></tr>
<tr><td><code>/api/edit-trojan</code></td><td>auth, user, limitip, quota</td></tr>
</table>

<h2>Contoh Request</h2>
<p>Create vmess:</p>
<p><code>https://DOMAIN:81/api/create-vmess?auth=APIKEY&user=ahh1&quota=10&limitip=1&exp=30</code></p>
<p>Trial ssh:</p>
<p><code>https://DOMAIN:81/api/trial-ssh?auth=APIKEY</code></p>

<h2>Contoh Response (create)</h2>
<pre>{
  "status": "success",
  "message": "account ahh1 created",
  "data": {
    "user": "ahh1",
    "uuid": "b8e6...-...",
    "exp": "2026-10-01",
    "limitip": 1,
    "quota": "10GB",
    "xhttp": "vless://.../vless-xhttp...",
    "links": { "tls": "...", "ntls": "...", "grpc": "..." }
  }
}</pre>
</body></html>"""

class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, obj, code=200):
        body = json.dumps(obj, indent=2).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_html(self, html):
        body = html.encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        route = parsed.path.rstrip("/")
        params = urllib.parse.parse_qs(parsed.query)

        if route in ("/doc", "/vps/doc", "/api/doc"):
            self._send_html(DOC_HTML.replace("DOMAIN", get_domain()))
            return

        if not route.startswith("/api/"):
            self._send({"status": "error", "message": "not found"}, 404)
            return

        if not valid_auth(params):
            self._send({"status": "error", "message": "invalid auth key"}, 403)
            return

        ep = route[len("/api/"):]
        user = params.get("user", [None])[0]
        quota = params.get("quota", [None])[0]
        limitip = params.get("limitip", ["1"])[0]
        exp = params.get("exp", [None])[0]
        password = params.get("password", [None])[0]

        import random, string
        def rnd(n=8):
            return "".join(random.choices(string.ascii_lowercase + string.digits, k=n))

        try:
            # ---- SSH ----
            if ep == "trial-ssh":
                u, p = "trial-" + rnd(5), rnd(8)
                res = create_ssh_account(u, p, 1, 1)
                res.setdefault("data", {})["trial"] = True
                self._send(res)
            elif ep == "create-ssh":
                if not user or not password or not exp:
                    self._send({"status": "error", "message": "need user, password, exp"})
                else:
                    self._send(create_ssh_account(user, password, exp, limitip))
            elif ep == "renew-ssh":
                self._send(renew_ssh_account(user, exp or 1))
            elif ep == "del-ssh":
                self._send(delete_ssh_account(user))
            elif ep == "cek-ssh":
                self._send(list_ssh_accounts())

            # ---- VMESS / VLESS / TROJAN ----
            elif ep.startswith(("trial-vmess", "trial-vless", "trial-trojan")):
                proto = ep.split("-")[1]
                u = "trial-" + rnd(5)
                self._send(create_xray_account(proto, u, exp or 1, limitip, quota or 0))
            elif ep.startswith(("create-vmess", "create-vless", "create-trojan")):
                proto = ep.split("-")[1]
                if not user or not exp:
                    self._send({"status": "error", "message": "need user, exp"})
                else:
                    self._send(create_xray_account(proto, user, exp, limitip, quota or 0))
            elif ep.startswith(("renew-vmess", "renew-vless", "renew-trojan")):
                proto = ep.split("-")[1]
                self._send(renew_xray_account(proto, user, exp or 1))
            elif ep.startswith(("del-vmess", "del-vless", "del-trojan")):
                proto = ep.split("-")[1]
                self._send(delete_xray_account(proto, user))
            elif ep.startswith(("cek-vmess", "cek-vless", "cek-trojan")):
                proto = ep.split("-")[1]
                self._send(list_xray_accounts(proto))
            elif ep.startswith(("edit-vmess", "edit-vless", "edit-trojan")):
                proto = ep.split("-")[1]
                self._send(edit_xray_account(proto, user, limitip, quota))
            else:
                self._send({"status": "error", "message": "unknown endpoint"}, 404)
        except Exception as e:
            self._send({"status": "error", "message": str(e)}, 500)

if __name__ == "__main__":
    print(f"API server on {HOST}:{PORT}")
    http.server.ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
