# Mục lục tài liệu project auto test VMS TA (Recruitment)

> Đọc file này trước, rồi đọc **trọn các file liên quan** đến flow đang làm. Viết thêm file mới trong `docs/` thì thêm một dòng vào đây.

| File | Nói về gì | Đọc khi |
|---|---|---|
| `CHECKLIST-auto-test.md` | Quy trình tổng (mục 0) và các quy tắc viết auto test | **Luôn đọc**, trước khi viết hoặc sửa test |
| `resource-request.md` | Form RR, dropdown, data mẫu (quét API 04/11/2026, tài khoản `truong.dangvan`) | Làm với RR |
| `session-tao-rr-tom-tat.md` | Kết quả và bài học khi tự động tạo, duyệt RR; cách xóa và dọn RR rác | Tạo, Submit, Approve, xóa RR |
| `du-lieu-quet-api-form-va-dropdown.md` | Kết quả quét API các form và dropdown; quy tắc popup (mục 0b); tài khoản theo role (mục 4); Accept CV, Add a Meeting, Interview Result | Làm với Application, Review CV, popup, chọn tài khoản |
| `task-73087-masking-test-tom-tat.md` | Task #73087 che contact trong CV: phạm vi, BR, kịch bản, câu hỏi BA; quy ước nhãn nguồn (mục 0) | Làm task Masking, hoặc cần quy ước nhãn nguồn |
| `masking.md` | Tổng kết Masking 09/11/2026: bộ data RR01415, chỗ cần check theo tài khoản, View CV, mail, lỗi CV ảnh, câu hỏi BA | Check tay hoặc làm tiếp task Masking |

## Thông tin riêng của project

- STG **không gửi mail thật**, nên chạy lại flow không cần báo người nhận. [User 08/11/2026]
  Các chỗ ghi "mail đã gửi, không thu hồi được" trong `session-tao-rr-tom-tat.md` được viết trước khi có xác nhận này.
- Flow chạy **từ đầu từ RR**, không dùng data cũ, vì người dùng vừa chạy vừa học nghiệp vụ. [User 08/11/2026]
  `resource-request.md` mục 1 khuyên dùng RR có sẵn: đó là bối cảnh riêng của test Masking.
- Không lấy được source code module Odoo của VMS, nên popup do code trả về phải chạy mới biết. [User 08/11/2026]
- Danh sách điều cấm làm trên STG: **chưa có**. [Claude]
