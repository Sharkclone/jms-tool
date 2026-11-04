# J&T JMS Tool — bản local (HTML + Python)

Tool thao tác JMS (đăng ký chuyển hoàn hàng loạt, tra hành trình, tra ký nhận CSKH)
chạy hoàn toàn trên máy của bạn: trang HTML giao diện + cầu nối Python nhỏ
chuyển tiếp yêu cầu tới API thật của JMS bằng phiên đăng nhập của bạn.

**Điểm quan trọng đã giải mã từ web JMS:** API của JMS xác thực bằng **token**
(header `authToken` = giá trị `YL_TOKEN` trong localStorage của trang JMS),
không phải bằng cookie. Chi tiết kỹ thuật nằm ở `api-recon.md` mục 6.

## Chạy tool

1. Mở thư mục này, chạy: `python server.py` (Windows: `py server.py`)
   — chỉ dùng thư viện chuẩn của Python, không cần cài thêm gì.
2. Mở trình duyệt vào: http://localhost:8765
3. Đăng nhập JMS như bình thường — nếu đã cài extension (mục dưới), tool tự có phiên.
   Chưa cài extension thì dán YL_TOKEN vào ô **Phiên đăng nhập**, bấm **Lưu token**.
4. Dùng các tab chức năng. Xong việc thì quay lại cửa sổ Python, nhấn `Ctrl+C` để tắt.

## Chạy như phần mềm PC (app-mode)

Bấm đúp file **`JMS-Tool.bat`** trong thư mục này: nó tự chạy bridge (cửa sổ
thu nhỏ) rồi mở tool trong một cửa sổ Chrome riêng (không thanh địa chỉ, có
icon trên taskbar — nhìn như phần mềm thật). Muốn ghim thì chuột phải vào
cửa sổ app trên taskbar → **Pin to taskbar**. Tắt tool thì đóng cả cửa sổ
app lẫn cửa sổ bridge.

## Dùng trên điện thoại (mobile)

1. Trên máy tính, bấm đúp **`JMS-Tool-Mobile.bat`** (hoặc chạy
   `py server.py --host 0.0.0.0`) — bridge sẽ in ra địa chỉ LAN dạng
   `http://<IP-máy-tính>:8765`.
2. Điện thoại **cùng WiFi** với máy tính mở địa chỉ đó bằng Chrome là dùng
   được hết các tab (giao diện đã chỉnh cho màn hình nhỏ).
3. Muốn giống app thì trong Chrome trên điện thoại bấm menu → **Thêm vào
   Màn hình chính** — lần sau bấm icon là mở thẳng tool.

⚠️ **Lưu ý an toàn:** chế độ mobile mở bridge ra mạng LAN — ai cùng WiFi
mở được địa chỉ đó là dùng được phiên JMS của bạn. Chỉ bật trên WiFi tin
cậy (WiFi nhà riêng), xong việc thì tắt bridge ngay. Bản sau sẽ thêm mã
PIN nếu bạn cần dùng trên mạng chung.

## Lấy phiên đăng nhập — cách tự động (khuyên dùng)

Trong thư mục `extension/` có sẵn một extension Chrome mini đi kèm (v1.1):

1. Mở `chrome://extensions` → bật **Developer mode** → **Load unpacked** → chọn thư mục `extension/` trong project này.
   (Đã cài bản cũ thì bấm nút **Reload** của extension để lên v1.1.)
2. Xong. Extension tự gửi xuống cầu nối cả hai thứ:
   - **Token YL_TOKEN** đọc từ trang JMS (kiểm tra lại mỗi 30 giây, token đổi là gửi bản mới).
   - **Cookie** của jtexpress.vn (kể cả cookie HttpOnly), mỗi khi cookie thay đổi.
   Icon hiện "OK" là đã gửi thành công.
3. Cầu nối phải đang chạy thì extension mới gửi được; nếu chưa chạy,
   lần thay đổi kế tiếp nó sẽ gửi lại.

## Lấy token JMS — cách thủ công (dự phòng)

1. Đăng nhập JMS trên trình duyệt như bình thường (kể cả bước Google Authenticator).
2. Nhấn `F12` → thẻ **Application** → mục **Local Storage** → chọn `https://jms.jtexpress.vn`.
3. Tìm khóa **YL_TOKEN**, copy toàn bộ giá trị của nó.
4. Dán vào tool. Khi JMS đăng xuất/hết phiên, làm lại các bước này.

Phiên đăng nhập chỉ lưu trong file `session.json` ngay trên máy bạn.
**Đừng gửi file `session.json` cho ai khác** — ai có token là vào được phiên JMS của bạn.

## Trạng thái hiện tại

- ✅ Đã nạp đủ API thật của JMS vào `endpoints.json` (trích xuất từ mã JS của web JMS
  ngày 2026-11-04): đăng ký chuyển hoàn (tìm kiếm + lưu lần 1/lần 2), tra ký nhận CSKH,
  tra hành trình (thông tin đơn + kiện vấn đề). Dữ liệu gửi đi đã chuẩn hoá đúng
  quy trình của trang JMS (tìm form → lưu; thành công khi JMS trả `code = 1`).
- ✅ Cầu nối tự gắn header `authToken` + `countryId: 1` cho POST, giống hệt web JMS.
- ✅ Tab **Đăng ký chuyển hoàn theo file** (thêm tối 2026-11-04, đúng quy trình trang
  batch MutilReturnBack2 của JMS): chọn file .txt/.csv chứa mã → tool tra cứu theo lô
  tối đa 200 mã/lần (tự chia nhỏ) → bảng kiểm tra mã nào được phép (enteringFlag) →
  chọn loại chuyển hoàn (danh sách tải từ JMS) → lưu một lần bằng afterFilterSave;
  mã không được phép bị chặn lưu như trang gốc (tool hỏi có loại ra không).
  File .xlsx: lưu thành CSV rồi chọn ở đây (bản sau hỗ trợ đọc thẳng .xlsx và
  đường upload mẫu Excel thật của JMS).
- ⏳ Chưa chạy thật bằng token sống trên máy của bạn — lần chạy đầu tiên nên thử
  1–2 mã tra cứu (chỉ đọc) trước, rồi mới chạy đăng ký chuyển hoàn hàng loạt.

## File trong project

- `server.py` — cầu nối Python (nghe ở 127.0.0.1:8765, chuyển tiếp request + token/cookie).
- `index.html` — giao diện (1 file duy nhất, không cần internet).
- `endpoints.json` — danh sách API JMS thật.
- `api-recon.md` — toàn bộ ghi chép giải mã API của web JMS.
- `extension/` — extension Chrome tự lấy phiên đăng nhập (cookie + token).
- `JMS-Tool.bat` — chạy tool kiểu app-mode trên PC Windows.
- `JMS-Tool-Mobile.bat` — chạy bridge mở ra LAN để dùng trên điện thoại.
- `manifest.webmanifest`, `tool-icon.svg` — khai báo để thêm tool vào màn hình chính điện thoại.
- `session.json` — phiên đăng nhập (tự tạo khi lưu; file nhạy cảm).
