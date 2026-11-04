// JMS Tool - Tu lay phien dang nhap
// Gui xuong cau noi Python o localhost:8765:
//  - Cookie cua jtexpress.vn (ke ca HttpOnly) - doc bang chrome.cookies.
//  - Token xac thuc API (YL_TOKEN trong localStorage cua trang JMS) - do
//    content.js doc va gui qua message.
// Phien dang nhap CHI di toi localhost tren may nay, khong di dau khac.

const BRIDGE_URLS = ["http://localhost:8765/api/session", "http://127.0.0.1:8765/api/session"];
let pushTimer = null;
let lastToken = "";
let lastLang = "";

async function collectCookieHeader() {
  const cookies = await chrome.cookies.getAll({ domain: "jtexpress.vn" });
  if (!cookies.length) return "";
  return cookies.map(c => c.name + "=" + c.value).join("; ");
}

async function pushSession() {
  const payload = {};
  try {
    payload.cookie = await collectCookieHeader();
  } catch (e) {
    console.warn("Khong doc duoc cookie JMS:", e);
  }
  if (lastToken) payload.token = lastToken;
  if (lastLang) payload.lang = lastLang;
  if (!payload.cookie && !payload.token) return;
  for (const url of BRIDGE_URLS) {
    try {
      const res = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      if (res.ok) {
        console.log("Da gui phien JMS xuong JMS Tool (" + new Date().toLocaleTimeString() + ")");
        chrome.action.setBadgeText({ text: "OK" });
        chrome.action.setBadgeBackgroundColor({ color: "#157347" });
        return;
      }
    } catch (e) {
      // Cau noi chua chay - bo qua, lan thay doi sau se gui lai.
    }
  }
  chrome.action.setBadgeText({ text: "!" });
  chrome.action.setBadgeBackgroundColor({ color: "#b02a37" });
}

function schedulePush() {
  if (pushTimer) clearTimeout(pushTimer);
  pushTimer = setTimeout(pushSession, 800);
}

// Gui ngay khi extension duoc cai / trinh duyet khoi dong
chrome.runtime.onInstalled.addListener(schedulePush);
chrome.runtime.onStartup.addListener(schedulePush);

// Tu dong gui lai moi khi cookie cua jtexpress.vn thay doi (dang nhap, lam moi phien...)
chrome.cookies.onChanged.addListener((info) => {
  const domain = (info.cookie && info.cookie.domain) || "";
  if (domain.includes("jtexpress.vn")) schedulePush();
});

// content.js tren trang JMS gui token len -> luu lai va day xuong cau noi
chrome.runtime.onMessage.addListener((msg) => {
  if (msg && msg.type === "jms_token" && msg.token) {
    lastToken = msg.token;
    lastLang = msg.lang || "";
    schedulePush();
  }
});

// Bam vao icon extension = gui ngay lap tuc
chrome.action.onClicked.addListener(pushSession);
