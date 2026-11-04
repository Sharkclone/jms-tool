// JMS Tool - doc token dang nhap tu trang JMS
// API cua JMS xac thuc bang header authToken, gia tri la localStorage "YL_TOKEN"
// cua trang jms.jtexpress.vn (khong phai cookie). Content script nay doc token
// (va ngon ngu) roi nho background.js gui xuong cau noi Python o localhost:8765.
// Token chi di toi localhost tren may nay, khong di dau khac.

let lastSent = "";

function readAndSend() {
  let token = "";
  let lang = "";
  try {
    token = localStorage.getItem("YL_TOKEN") || "";
    lang = localStorage.getItem("lang") || "";
  } catch (e) {
    return;
  }
  if (!token) return;
  const stamp = token + "|" + lang;
  if (stamp === lastSent) return;
  lastSent = stamp;
  try {
    chrome.runtime.sendMessage({ type: "jms_token", token, lang });
  } catch (e) {
    // Extension vua reload - bo qua, lan quet sau se gui lai.
  }
}

// Gui ngay khi trang JMS tai xong, kiem tra lai moi 30 giay (token doi khi
// dang nhap lai / lam moi phien) va moi khi quay lai tab.
readAndSend();
setInterval(readAndSend, 30000);
document.addEventListener("visibilitychange", () => {
  if (!document.hidden) readAndSend();
});
