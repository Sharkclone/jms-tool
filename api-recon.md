# Bản đồ chức năng & dữ liệu JMS — phục vụ JMS Tool local

Nguồn: phiên khảo sát 2026-11-04 18:25–18:37 (đăng nhập tài khoản Hill, thao tác CHỈ ĐỌC).
Trình duyệt khảo sát không mở được DevTools → phần "trường dữ liệu" dưới đây lấy từ giao diện thật;
endpoint API thật được trích xuất riêng từ file JS của web JMS (mục cuối file).

## 1. Đăng ký chuyển hoàn — returnAndForwardMaintainAddSite
URL trang: https://jms.jtexpress.vn/app/operatingPlatformIndex/returnAndForwardMaintainAddSite

- Tìm kiếm theo mã vận đơn → trả về 1 dòng, điền sẵn form. Trường dữ liệu thấy trong response hiển thị:
  mã vận đơn; loại chuyển hoàn (mặc định "Chuyển hoàn"); mã bưu cục chuyển; mã bưu cục nhận;
  tên bưu cục chuyển; số lượng; khối lượng; mã nhân viên quét; họ tên nhân viên;
  mã nhân viên lấy hàng; lý do chuyển hoàn; ngày tạo đơn; tên người gửi; SĐT người gửi;
  phí vận chuyển; COD; địa chỉ người nhận.
- Trên giao diện, "Loại đơn" chọn: Trả lại (= Hoàn lần 1) / Chuyển hoàn lần 2 (= Hoàn lần 2)
  — theo quy trình Hill đã dạy; trang này chính là nơi Muse thao tác tay mỗi sáng.
- Nút "Lưu và thêm mới" = thao tác GHI: chưa gọi thật, cần endpoint + payload thật trước khi làm vào tool.
- Giới hạn giao diện: Thêm dòng tối đa 30 dòng; phân trang 10/20/50/100; có Xuất file / Nhập file.

## 2. Tra ký nhận CSKH — serviceSignForQuery
URL trang: https://jms.jtexpress.vn/app/operatingPlatformIndex/serviceSignForQuery?title=Tra%20k%C3%BD%20nh%E1%BA%ADn%20CSKH&moduleCode=

- Gửi: mã vận đơn (dán nhiều mã, tối đa 500 — theo quy trình Hill dạy), ngày tra cứu (mặc định hôm nay),
  các lọc phụ: Loại ký nhận, Loại vận đơn, Mã bưu cục, Tên người ký nhận, SĐT, Theo người quét, Theo ngày.
- Response (bảng): Mã vận đơn, Loại vận đơn, Hình ảnh, Địa chỉ giao hàng, Trạng thái đơn hàng,
  Nhân viên quét, Mã nhân viên quét, Thời gian quét, Bưu cục ký nhận, Mã bưu cục ký nhận,
  Tên người ký, SĐT người ký, Thời gian ký, Mã ký nhận, Loại ký nhận, Hình thức ký nhận, Kênh, SĐT liên hệ.
- Lưu ý quy trình "Lọc Đơn" của Hill: cần trường LOẠI QUÉT CUỐI (Đóng Bao / Giao lại hàng / Quét kiện vấn đề)
  để lọc — đối chiếu cột trạng thái/quét khi nạp API thật.

## 3. Tra hành trình — trackingExpress
URL trang: https://jms.jtexpress.vn/app/operatingPlatformIndex/trackingExpress?title=

- Gửi: chế độ "Theo vận đơn" + danh sách mã (tối đa 100 mã theo nhãn giao diện; quy trình Hill dùng tới 1000
  qua thao tác trang — cần xác minh giới hạn thật của API). Chế độ khác: Theo mã chuyển phát, Theo SĐT người nhận.
- Response: tổng quan đơn (mã, trạng thái, ngày gửi, bưu cục gửi/nhận, hình thức, số lượng, khối lượng)
  + timeline hành trình (thời gian, thao tác, bưu cục) — trang hiện luôn phần "Lịch sử POD" phục vụ Check Giao Lại:
  cần các trường: Loại thao tác (Giao lại hàng / Quét kiện vấn đề...), Thời gian yêu cầu giao lại, tên nhân viên quét.
- Giữ nguyên thứ tự thời gian API trả về, không tự sắp xếp lại.

## 4. Điều phối — orderScheduling
URL trang: https://jms.jtexpress.vn/app/customerPlatformIndex/orderScheduling?title=%C4%90i%E1%BB%81u%20ph%E1%BB%91i&moduleCode=

- Mở trang là có sẵn bảng tổng hợp theo bưu cục (mặc định 297A01) + chọn ngày bắt đầu/kết thúc, nút Tìm kiếm.
- Các chỉ số: đơn mới / đã giao / chưa giao / chưa phân công / đã phân công / phân công thất bại / hết hạn /
  đã chuyển phát / chuyển phát thất bại / đã hủy / khiếu nại / đã nhận, kèm cột số liệu hôm nay/quá hạn...
- Nút "Điều phối đơn đặt" = thao tác GHI (phân công) — chưa khảo sát sâu, làm sau nếu Hill cần.

## 5. Menu chức năng theo quyền tài khoản (đã lọc quyền)
- Nền tảng điều hành: Tra hành trình, Thiết lập quy tắc, Bổ sung hành trình, Shipper 5 sao,
  Quản lý tem bao, Chặn/Hoàn/Tiếp (chứa Đăng ký chuyển hoàn), GS dữ liệu, QL ký nhận, Báo biểu, Chuyển đơn.
- Nền tảng khách hàng: Báo cáo đơn đặt hàng, Điều phối đơn đặt, Tra cứu đơn đặt,
  Truy vấn đơn hàng đã đánh dấu, Lịch sử in đơn.
- Dữ liệu cơ bản: Quản lý thông tin bưu cục, Tra cứu dữ liệu bưu cục, Phạm vi bưu cục, Xếp ca,
  Tra cứu dữ liệu chấm công.
- 13 nhóm tổng: Dữ liệu cơ bản, Nền tảng điều hành, Quản lý cộng đồng, Dịch vụ tích hợp,
  Nền tảng khách hàng, Kinh doanh bưu cục, Quyết toán tài chính, Nguồn lực vận chuyển,
  Chất lượng dịch vụ, Chỉ số vận hành, Cơ sở dữ liệu, Thiết bị thông minh, Nền tảng quy hoạch
  (chưa mở rộng hết mục con của các nhóm còn lại).

## 6. Endpoint API thật (trích xuất từ JS của web JMS, 2026-11-04)

Kiến trúc: JMS là Vue SPA + vi ứng dụng (qiankun). Mọi API đi qua gateway
**https://jmsgw.jtexpress.vn** (biến VUE_APP_API_URL trong app.js), tiền tố dịch vụ của
Nền tảng điều hành là biến `OPE` trong mã con (đối chiếu các lời gọi ghi cứng
"/operatingplatform/..." trong cùng mã → OPE = "/operatingplatform", đang kiểm chứng trực tiếp).
Response envelope: `{code, msg, data}`; thành công khi `code` bằng hằng SUCCESS của trang.
Tổng cộng trích xuất được 213 hàm API từ mã JS của hệ con operatingPlatformIndex.

### 6.1 Đăng ký chuyển hoàn (module trang ReturnAndForwardMaintainAddSite)
- Tìm kiếm (nút Tìm kiếm): **GET** `/operatingplatform/rebackTransferExpress/findByWaybillNo`
  với query `waybillNo=<mã>&applyTypeCode=<4|6>` (hàm applyInfo; qs.stringify).
  - applyTypeCode **4 = Trả lại (Hoàn lần 1)**, **6 = Hoàn lần 2** (nhãn gốc: 4="退回", 6="二次退件").
  - Response data = toàn bộ thông tin đơn (chính là form được điền sẵn trên giao diện).
- Lưu (nút "Lưu và thêm mới", hàm submitForm của trang):
  - payload = `{...data từ bước tìm kiếm, rebackTypeValue: data.returnType,
    rebackTypeCode: data.rebackReasonCode, rebackTransferReason: data.rebackTransferReason,
    applyTypeCode: <4|6>, newPackageChargeWeight: +data.chargeWeight}` và **xoá trường `reason`**.
  - type 4 → **POST** `/operatingplatform/rebackTransferExpress/add` (hàm reqAdd).
  - type 6 → **POST** `/operatingplatform/rebackTransferExpress/registerSecondReback`.
- Trang đăng ký theo lô (component MutilReturnBack2 — trang batch của JMS):
  - Tra cứu: **POST** `/operatingplatform/batchReturnRegistry/queryList`, payload
    `{waybillNos: [<mã>, ...]}` **tối đa 200 mã/lần**; response data = mảng dòng
    `{waybillNo, returnType, enteringFlag (1 = được phép, 2 = không được phép),
    remark, receiverName, receiverDetailedAddress}`.
  - Lưu: **POST** `/operatingplatform/batchReturnRegistry/afterFilterSave`, payload là
    MẢNG `[{waybillNo, rebackTypeCode}]` (rebackTypeCode = mã loại chuyển hoàn đã chọn
    trong form). Trang gốc CHẶN lưu nếu còn dòng enteringFlag = 2 (báo "loại ra rồi thử lại").
  - Từ điển loại chuyển hoàn: **GET**
    `/operatingplatform/returnTypePbmPieRelation/returnExpress/selectType?current=1&size=999`
    → danh sách `{returnType, code}` nạp vào ô chọn loại.
  - Đường nhập file Excel của trang gốc: tải mẫu **GET**
    `/operatingplatform/batchReturnRegistry/exportTemplate`, upload file **POST**
    `/operatingplatform/batchReturnRegistry/exportData` (multipart, kèm header auth);
    response `{successNum, errorNum, key}` — key dùng để tải danh sách lỗi.
    Tool v1 dùng đường tra cứu + lưu theo mã (không cần mẫu Excel); đường upload file
    thật để bản sau khi có token thật để test.

### 6.2 Tra ký nhận CSKH (module trang ServiceSignForQuery)
- Tra chính: **POST** `/operatingplatform/podTracking/inner/query/keywordList` (hàm traceDataList).
  Payload lõi: `{keywordList: [<mã>, ...], typeEnum: "WAYBILL", waybillId: <mã>}` + các trường lọc
  từ form (ngày, loại ký nhận...) do searchFunParamsHandle bổ sung — cần đối chiếu khi chạy thật.
  Response data.records = danh sách dòng ký nhận.
- Ảnh POD: POST `/operatingplatform/podTracking/img/path` (hàm getImageList).

### 6.3 Tra hành trình (module trang trackingExpress)
- Đơn hàng: **POST** `/operatingplatform/expressTracking/opsOrderList` (hàm orderList),
  payload là MẢNG: `[{id: <mã vận đơn>}]`.
- Danh sách vận đơn: POST `/operatingplatform/expressTracking/opsWaybillList` (hàm waybillList).
- Kiện vấn đề: **POST** `/operatingplatform/abnormalPieceScanList/pageList` (hàm matterList),
  payload `{current: 1, size: 100, waybillId: <mã>}` → data.records.
- Việc CSKH: **POST** `/operatingplatform/podTracking/queryCssWork` (hàm getCssWork),
  payload `{keyword: <mã>, trackingTypeEnum: <loại tra>}`.
- Đơn con/đa kiện: POST `/operatingplatform/podTracking/querySubOrderInfo` payload `{waybillIds: [<mã>]}`;
  POST `/operatingplatform/podTracking/queryMergerOrderInfo` payload `{parentWaybillId: <mã>}`.
- Cuộc gọi: POST `/operatingplatform/callHistory/qos/queryOutboundCall` payload `{waybillNo: <mã>}`;
  GET `/operatingplatform/order/queryShortMsgRecord?waybillNo=<mã>`.

### 6.4 Điều phối (hệ con customerPlatformIndex — chưa trích xuất JS)
Chưa tải mã của hệ con này; trang tổng hợp đọc dữ liệu khi mở. Làm sau nếu Hill cần.

### 6.5 Cơ chế xác thực + hằng số (đã giải mã xong từ mã JS, 2026-11-04 tối)
- Tiền tố: fz.OPE = **"operatingplatform"** (không có dấu / đầu; nối sau base URL).
  URL đầy đủ = https://jmsgw.jtexpress.vn/operatingplatform/... — test trực tiếp bằng
  trình duyệt đã cho envelope JMS chuẩn (code 401 vì thiếu header), chứng tỏ đường dẫn đúng.
- **Xác thực bằng header `authToken`**, giá trị = `localStorage["YL_TOKEN"]` của trang JMS
  (KHÔNG phải cookie). Thiếu/sai token → `{"code":401,"msg":"页面长时间未操作，请重新登录系统"}`.
  Kèm header `lang` (vd vi_VN), `langType`, `timezone` (dạng "GMT+07:00"), `routeName`.
- Mọi body POST dạng object được web JMS **tự thêm `countryId: "1"`** — cầu nối làm giống hệt.
- Hằng thành công (module cấu hình 87991): `SUCCESS = 1`, `SUCCESS_COPY = 1`, `EXPIRED = "000002"`.
  → Điều kiện thành công khi đọc response: `code === 1`.
- Hệ quả cho tool: extension phải lấy cả **YL_TOKEN từ localStorage** (content script trên
  trang JMS) chứ không chỉ cookie — đã cập nhật extension v1.1 + server.py + index.html.
- Còn mở (chỉ chốt được khi chạy thật trên máy Hill): payload phụ của keywordList
  (các trường lọc theo form) và opsWaybillList; routeName có bị kiểm tra chặt hay không.
