# Tóm tắt phiên: tự động tạo và duyệt RR (Resource Request)

> Phiên làm việc 04/11/2026. Nối tiếp `task-73087-masking-test-tom-tat.md` (Masking CV) và `docs/resource-request.md` (form RR, dropdown).
> Không chứa mật khẩu hay session. Mật khẩu chỉ nằm trong `.env`.
> **Nguồn:** toàn bộ file là **[STG-chạy]**: kết quả chạy script và thao tác thật trên STG ngày 04/11/2026, không lấy từ SRS hay Redmine. Quy ước nhãn nguồn xem mục 0 của `task-73087-masking-test-tom-tat.md`.

## 1. Kết quả
- **RR01413** (id 1799) đã được tạo bằng script, Submit, rồi BOD Approve → trạng thái **Open**, quota 20.
- DL, SM, Reviewer, Interviewer: `truong.dangvan`. Approver (BOD): `hoai.nguyenthithu`. Company Follow: VTI Corporation.
- Dùng được RR này cho test Masking: Add a line Review CV → Submit CV (mỗi CV Submit trừ quota).
- Trên STG chỉ còn RR01413, không còn RR rác do phiên này tạo.
- Chưa làm: tạo Application, upload CV, xem CV Masked, Review CV → Submit CV, popup View CV (các bước 2–6 của lộ trình).

## 2. File đã tạo/sửa trong `D:\Auto-test\recruitment`
| File | Vai trò |
|---|---|
| `data/rr/rr_default.json` | Data RR. Muốn đổi data thì sửa file này, không sửa code. Ngày lưu dạng số ngày (`deadline_days`, `onboard_days`) |
| `pages/resource_request_page.py` | Các thao tác trên form RR: `goto_list`, `open_create`, `fill_form`, `save`, `submit`, `code`, `open_rr`, `status`, `approve` |
| `tests/test_create_rr.py` | DL tạo RR → Save → Submit, ghi Code vào `output/last_rr.txt` |
| `tests/test_approve_rr.py` | BOD mở RR theo Code → Approve |
| `tests/conftest.py` | Thêm: test lỗi thì tự chụp ảnh vào `output/fail_<tên test>.png` |
| `core/login.py` | Đăng nhập: thử lại 3 lần, chờ lâu hơn, không chờ navbar Helpdesk |
| `.env` | `BOD_USER` đổi sang `hoai.nguyenthithu` |

Chạy: `pytest tests/test_create_rr.py` rồi `pytest tests/test_approve_rr.py` (dùng `.\.venv\Scripts\python.exe -m pytest ...`).
Lưu ý: bản sửa `approve()` (chỉ bấm Confirm một lần) chưa được chạy lại vì RR01413 đã Open.

## 3. Data RR mẫu (đã dùng)
Project "Hệ thống quản lý học viên", Job Location Hồ Chí Minh, Expect Qty **20**, Job Position Business Development, Level Junior, Main skill General Manager, Priority Normal, Salary 25.000.000 VND, Job Type Full time, Interview type Face to face, Experience Fresher/Intern, Languages Vietnamese, Deadline +45 ngày, Onboard +60 ngày.
Job Description VN/EN và Experience Required VN/EN viết nội dung thật, **mỗi ô trên 150 từ**, không nêu tên khách hàng.

## 4. Những điều học được về form RR trên STG
- **Department Leader** mặc định không phải user đăng nhập → phải chọn lại `truong.dangvan`; Department đổi theo.
- **SM, Reviewer, Interviewer** để trống → phải điền; **Company Follow** tự có VTI Corporation (bỏ qua).
- **Định dạng ngày:** `dd/mm/yyyy`.
- **Currency:** ô có chữ "VND" nhưng vẫn phải chọn VND từ danh sách, nếu không Save báo Currency không hợp lệ. Locator: `get_by_role("textbox", name=re.compile("C\s*u\s*r\s*r\s*e\s*n\s*c\s*y"))`.
- **Ô "Quy mô dự án / Domain dự án"** là **Project Description**; **Note** là ô riêng bên dưới.
- **Dropdown** (many2one): phải click vào giá trị trong danh sách thì dropdown mới tắt; chưa tắt thì che ô kế tiếp.
- **Submit** yêu cầu 4 ô văn bản ≥ 150 từ, có hộp xác nhận "đừng nêu tên khách hàng" → Confirm. Hộp Confirm chỉ bấm **một lần**, bấm thêm sẽ báo lỗi "not in submit or pending state".
- **Approve** (BOD) cũng có hộp Confirm. **Reject** có thêm hộp "Reject Reason" (điền Message rồi bấm Reject).
- **Tìm RR trong list:** mặc định có bộ lọc "Processing" → xóa bộ lọc rồi mới gõ Code.
- Odoo sau đăng nhập mở Helpdesk; vào thẳng `LIST_URL` và chỉ chờ menu "Resource Requests" của Recruitment. Với BOD, sau đăng nhập đã ở màn RR, không cần click menu.
- Không dùng `networkidle` (Odoo luôn có kết nối nền). STG đôi lúc chậm hoặc trả trang trắng, thử lại sau ít phút.
- Xóa RR chỉ được khi **Draft**. RR đã Submit muốn xóa: BOD Reject → Set to draft → Delete (mail vẫn đã gửi, không thu hồi được).

## 5. Dọn data rác trên STG (quy ước)
- Mỗi lần chạy lỗi giữa chừng có thể để lại RR Draft (hoặc RR đã Submit nếu lỗi sau Submit). Sau mỗi lần chạy thử, kiểm tra và xóa RR thừa, **giữ lại RR thành công**.
- Phiên này đã xóa: RR01411 (Draft), RR01412 (đã Submit, xử lý bằng Reject → Set to draft → Delete) và 3 RR Draft ban đầu (id 1794–1796).
- Xóa qua API (XML-RPC `unlink`) từng bị hệ thống chặn, phải được người dùng đồng ý rõ ràng trước. Chỉ xóa đúng id đã liệt kê, đã kiểm tra Code, Project, trạng thái.
- Tác dụng phụ không hoàn tác: các mail "To approve", "Reject", "Approve" đã gửi cho BOD, REC, DL.

## 6. Bảo mật
- Người dùng từng gửi một session cookie của `hoai.nguyenthithu` để xử lý RR01412. Tôi chỉ dùng với STG, không ghi vào code hay file. Nên đăng xuất tài khoản đó để session hết hiệu lực.

## 7. Việc tiếp theo
1. Mở màn Applications, tạo Application (Source VTI), upload CV (bước 2–3 lộ trình).
2. Chờ bản che, xem và tải CV Masked (kiểm tra `_masked.pdf`, copy chữ ra Notepad).
3. Review CV → chọn RR01413 → Submit CV; kiểm tra mail và popup View CV.
4. Chuẩn bị bộ CV mẫu (< 800KB mỗi file) trong `data/cv_samples/`.
