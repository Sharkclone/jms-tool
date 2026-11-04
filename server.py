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
        if self.path == "/api/endpoints":
            eps = load_endpoints()
            self._send_json(200, {k: {"configured": bool((v.get("url") or "").strip()), "note": v.get("note", "")}
                                  for k, v in eps.items() if isinstance(v, dict)})
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
        if self.path.startswith("/api/call/"):
            name = self.path[len("/api/call/"):].strip()
            payload = self._read_json_body()
            code, obj = forward_to_jms(name, payload)
            self._send_json(code, obj)
            return
        self._send_json(404, {"error": "not_found"})


def main():
    server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    print("JMS Tool dang chay: http://localhost:%d  (Ctrl+C de dung)" % PORT)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nDa dung.")


if __name__ == "__main__":
    main()
