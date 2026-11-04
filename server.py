#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JMS Tool - Cau noi Python chay local (Duong 2: HTML + Python).

Chay:  python server.py        (Windows: py server.py)
Mo:    http://localhost:8765

Nhiem vu cua file nay:
- Phat trang index.html cho trinh duyet.
- Nhan cookie dang nhap JMS tu giao dien, luu vao session.json (chi tren may nay).
- Nhan yeu cau tu giao dien, gan cookie, chuyen tiep toi API that cua JMS
  (dinh nghia trong endpoints.json), roi tra ket qua ve cho giao dien.

Chi dung thu vien chuan cua Python - khong can cai them gi.
Chi nghe o 127.0.0.1 (may nay), khong mo ra mang ngoai.
"""

import json
import os
import sys
import time
import urllib.request
import urllib.error
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SESSION_FILE = os.path.join(BASE_DIR, "session.json")
ENDPOINTS_FILE = os.path.join(BASE_DIR, "endpoints.json")
PORT = 8765
JMS_ORIGIN = "https://jms.jtexpress.vn"

# Tu cap nhat: code moi luon lay tu repo GitHub cua tool (nhanh main).
# Chi tai dung danh sach file nay - khong bao gio dong vao session.json.
UPDATE_REPO = "Sharkclone/jms-tool"
UPDATE_BRANCH = "main"
UPDATE_FILES = ["server.py", "index.html", "endpoints.json", "README.md", "api-recon.md",
                "version.json", "extension/manifest.json", "extension/background.js",
                "extension/content.js", "JMS-Tool.bat", "JMS-Tool-Mobile.bat",
                "manifest.webmanifest", "tool-icon.svg"]


def load_session():
    try:
        with open(SESSION_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_session(cookie=None, token=None, lang=None):
    # Giu lai cac gia tri cu neu lan luu nay khong gui kem (extension gui tung phan).
    data = load_session()
    if cookie is not None:
        data["cookie"] = cookie
    if token is not None:
        data["token"] = token
    if lang:
        data["lang"] = lang
    data["saved_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(SESSION_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return data


def load_endpoints():
    with open(ENDPOINTS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def forward_to_jms(name, payload):
    """Chuyen tiep 1 yeu cau toi endpoint JMS co ten `name` trong endpoints.json."""
    endpoints = load_endpoints()
    ep = endpoints.get(name)
    if ep is None:
        return 400, {"error": "unknown_endpoint", "detail": "Khong co endpoint '%s' trong endpoints.json" % name}
    url = (ep.get("url") or "").strip()
    if not url:
        return 400, {
            "error": "endpoint_not_configured",
            "detail": "Endpoint '%s' chua duoc nap URL that cua JMS (cho buoc bat request)." % name,
        }
    session = load_session()
    cookie = (session.get("cookie") or "").strip()
    token = (session.get("token") or "").strip()
    if not token and not cookie:
        return 400, {"error": "no_session", "detail": "Chua co phien dang nhap JMS (thieu token YL_TOKEN). Mo JMS da dang nhap de extension tu gui xuong, hoac dan token thu cong."}

    method = (ep.get("method") or "POST").upper()
    body = None
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
        "Origin": JMS_ORIGIN,
        "Referer": JMS_ORIGIN + "/",
        "Accept": "application/json, text/plain, */*",
        # JMS xac thuc bang header authToken (YL_TOKEN trong localStorage cua trang JMS),
        # giong het trinh chan request cua web JMS; kem lang + mui gio.
        "lang": (session.get("lang") or "vi_VN"),
        "timezone": "GMT+07:00",
    }
    if token:
        headers["authToken"] = token
    if cookie:
        headers["Cookie"] = cookie
    if method == "POST":
        # Web JMS tu them countryId=1 vao moi body POST (ma nuoc VN) - cau noi lam giong.
        if isinstance(payload, dict) and "countryId" not in payload:
            payload = dict(payload)
            payload["countryId"] = "1"
        body = json.dumps(payload if payload is not None else {}).encode("utf-8")
        headers["Content-Type"] = "application/json;charset=UTF-8"
    elif payload:
        from urllib.parse import urlencode
        url = url + ("&" if "?" in url else "?") + urlencode(payload)

    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            return resp.status, {"ok": True, "upstream_status": resp.status, "data": raw}
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="replace") if e.fp else ""
        return 200, {"ok": False, "upstream_status": e.code, "data": raw}
    except Exception as e:
        return 200, {"ok": False, "upstream_status": 0, "data": "Loi ket noi JMS: %s" % e}


def _github_raw_url(rel):
    from urllib.parse import quote
    return "https://raw.githubusercontent.com/%s/%s/%s" % (UPDATE_REPO, UPDATE_BRANCH, quote(rel))


def _fetch_url(url):
    req = urllib.request.Request(url, headers={"User-Agent": "JMS-Tool-Updater"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read()


def _local_version():
    try:
        with open(os.path.join(BASE_DIR, "version.json"), "r", encoding="utf-8") as f:
            return json.load(f).get("version") or "?"
    except Exception:
        return "?"


def _version_tuple(v):
    try:
        return tuple(int(p) for p in str(v).split("."))
    except Exception:
        return None


def check_update():
    """So sanh version local voi version moi nhat tren repo.
    Chi bao co ban moi khi ban tren repo that su moi hon ban local."""
    try:
        remote = json.loads(_fetch_url(_github_raw_url("version.json")).decode("utf-8"))
        latest = remote.get("version") or "?"
    except Exception as e:
        return 200, {"ok": False, "error": "fetch_failed",
                     "detail": "Khong tai duoc version moi tu GitHub: %s" % e}
    current = _local_version()
    lt, ct = _version_tuple(latest), _version_tuple(current)
    if lt is not None and ct is not None:
        available = lt > ct
    else:
        available = latest != current
    return 200, {"ok": True, "current": current, "latest": latest,
                 "update_available": available}


def apply_update():
    """Tai ban moi -> sao luu ban cu -> ghi de. session.json khong bao gio bi dong vao."""
    # 1. Tai toan bo file moi ve truoc; chi khi du thi moi cham vao file cu.
    try:
        new_contents = {}
        for rel in UPDATE_FILES:
            new_contents[rel] = _fetch_url(_github_raw_url(rel))
        json.loads(new_contents["version.json"].decode("utf-8"))
    except Exception as e:
        return 200, {"ok": False, "error": "download_failed",
                     "detail": "Tai ban moi that bai, ban cu van nguyen: %s" % e}
    # 1b. File Python moi phai bien dich duoc, neu khong thi huy - tranh lam hong lan chay sau.
    for rel, content in new_contents.items():
        if rel.endswith(".py"):
            try:
                compile(content.decode("utf-8"), rel, "exec")
            except Exception as e:
                return 200, {"ok": False, "error": "invalid_python",
                             "detail": "Ban moi co file Python loi, giu nguyen ban cu: %s (%s)" % (rel, e)}
    # 2. Sao luu ban cu vao backups/<thoi gian>/ (tru session.json).
    stamp = time.strftime("%Y%m%d-%H%M%S")
    backup_dir = os.path.join(BASE_DIR, "backups", stamp)
    for rel in UPDATE_FILES:
        src = os.path.join(BASE_DIR, rel)
        if os.path.isfile(src):
            dst = os.path.join(backup_dir, rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            with open(src, "rb") as f:
                data = f.read()
            with open(dst, "wb") as f:
                f.write(data)
    # 3. Ghi de + lap danh sach file thay doi de hien cho nguoi dung.
    changed = []
    for rel in UPDATE_FILES:
        src = os.path.join(BASE_DIR, rel)
        old = open(src, "rb").read() if os.path.isfile(src) else None
        if old != new_contents[rel]:
            changed.append(rel)
        with open(src, "wb") as f:
            f.write(new_contents[rel])
    new_version = json.loads(new_contents["version.json"].decode("utf-8")).get("version")
    return 200, {"ok": True, "current": _local_version(), "new_version": new_version,
                 "changed": changed, "backup_dir": backup_dir,
                 "restart_needed": "server.py" in changed,
                 "extension_reload_needed": any(r.startswith("extension/") for r in changed)}


def startup_update():
    """Tu dong cap nhat khi bridge khoi dong (neu co ban moi tren repo).
    Bat ky loi nao (mat mang, tai hong) cung chi in canh bao roi chay tiep ban cu."""
    try:
        code, chk = check_update()
        if not chk.get("ok") or not chk.get("update_available"):
            return
        print("Co ban moi %s (dang dung %s) - dang tu dong cap nhat..." % (chk["latest"], chk["current"]))
        code, res = apply_update()
        if res.get("ok"):
            print("Da tu dong cap nhat len %s. Ban cu sao luu tai %s." % (res["new_version"], res["backup_dir"]))
            if res.get("restart_needed"):
                print("Luu y: server.py da doi - lan khoi dong sau se chay ban moi.")
        else:
            print("Tu dong cap nhat that bai (%s) - van chay ban cu." % (res.get("detail") or res.get("error")))
    except Exception as e:
        print("Khong kiem tra duoc ban moi (%s) - van chay ban cu." % e)


def _lan_ips():
    """Dia chi IPv4 LAN cua may nay (bo qua loopback)."""
    import socket
    ips = []
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  # chi hoi bang dinh tuyen, khong gui du lieu
        ips.append(s.getsockname()[0])
        s.close()
    except Exception:
        pass
    try:
        for info in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET):
            ip = info[4][0]
            if not ip.startswith("127.") and ip not in ips:
                ips.append(ip)
    except Exception:
        pass
    return ips


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):  # giam log rac
        sys.stderr.write("[%s] %s\n" % (time.strftime("%H:%M:%S"), fmt % args))

    def _send_json(self, code, obj):
        raw = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def _read_json_body(self):
        try:
            length = int(self.headers.get("Content-Length") or 0)
        except Exception:
            length = 0
        if length <= 0:
            return {}
        try:
            return json.loads(self.rfile.read(length).decode("utf-8"))
        except Exception:
            return {}

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            path = os.path.join(BASE_DIR, "index.html")
            with open(path, "rb") as f:
                raw = f.read()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)
            return
        if self.path == "/api/session/status":
            s = load_session()
            has_cookie = bool((s.get("cookie") or "").strip())
            has_token = bool((s.get("token") or "").strip())
            self._send_json(200, {"cookie_set": has_cookie, "token_set": has_token,
                                  "saved_at": s.get("saved_at") if (has_cookie or has_token) else None})
            return
        if self.path == "/api/update/check":
            code, obj = check_update()
            self._send_json(code, obj)
            return
        if self.path == "/api/update/apply":
            # Cap nhat lam thay doi du lieu nen chi nhan POST; GET lac vao day
            # (trang cu goi khong kem body) thi tra loi ro rang thay vi 404 kho hieu.
            self._send_json(405, {"error": "method_not_allowed",
                                  "detail": "Cap nhat phai goi bang POST - tai lai trang de lay ban giao dien moi."})
            return
        if self.path == "/api/endpoints":
            eps = load_endpoints()
            self._send_json(200, {k: {"configured": bool((v.get("url") or "").strip()), "note": v.get("note", "")}
                                  for k, v in eps.items() if isinstance(v, dict)})
            return
        if self.path in ("/manifest.webmanifest", "/tool-icon.svg"):
            fname = self.path.lstrip("/")
            path = os.path.join(BASE_DIR, fname)
            ctype = "application/manifest+json" if fname.endswith(".webmanifest") else "image/svg+xml"
            with open(path, "rb") as f:
                raw = f.read()
            self.send_response(200)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)
            return
        self._send_json(404, {"error": "not_found"})

    def do_POST(self):
        if self.path == "/api/session":
            body = self._read_json_body()
            cookie = (body.get("cookie") or "").strip()
            token = (body.get("token") or "").strip()
            lang = (body.get("lang") or "").strip()
            if not cookie and not token:
                self._send_json(400, {"error": "empty_session", "detail": "Thieu ca cookie lan token."})
                return
            data = save_session(cookie=cookie or None, token=token or None, lang=lang or None)
            self._send_json(200, {"ok": True, "saved_at": data["saved_at"]})
            return
        if self.path == "/api/update/apply":
            code, obj = apply_update()
            self._send_json(code, obj)
            return
        if self.path.startswith("/api/call/"):
            name = self.path[len("/api/call/"):].strip()
            payload = self._read_json_body()
            code, obj = forward_to_jms(name, payload)
            self._send_json(code, obj)
            return
        self._send_json(404, {"error": "not_found"})


def main():
    import argparse
    ap = argparse.ArgumentParser(description="JMS Tool bridge")
    ap.add_argument("--host", default="127.0.0.1",
                    help="Dia chi lang nghe (mac dinh 127.0.0.1; 0.0.0.0 de mo qua LAN cho mobile)")
    ap.add_argument("--port", type=int, default=PORT)
    args = ap.parse_args()
    startup_update()
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print("JMS Tool dang chay: http://%s:%d  (Ctrl+C de dung)" % (args.host, args.port))
    if args.host == "0.0.0.0":
        print("Che do LAN (mobile) - mo tren dien thoai cung WiFi tai:")
        for ip in _lan_ips():
            print("  http://%s:%d" % (ip, args.port))
        print("  CHI DUNG TREN WIFI TIN CAY - ai cung mang LAN mo duoc dia chi nay.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nDa dung.")


if __name__ == "__main__":
    main()
