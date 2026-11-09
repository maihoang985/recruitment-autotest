# Masking che contact ứng viên trong CV: data và chỗ cần check

> Tổng kết ngày 09/11/2026 cho task test #73087 (task cha #70538). Dùng file này khi check tay hoặc tiếp tục làm task.
> Nhãn nguồn theo `task-73087-masking-test-tom-tat.md` mục 0. Tiêu chí chi tiết (BR1–BR12, Message list) xem file đó mục 2.
> Khi hai file khác nhau, file này mới hơn. Các điểm đã đính chính ghi ở mục 7.

## 1. Tình trạng

- RR **RR01415** (id 1802): Open, 20 slot, DL `dang.nguyenhuu`, Approver `hoai.nguyenthithu`. [STG-chạy 09/11]
- 16/17 dòng data đã tạo (id 32937–32952). D08 chưa tạo. D17 dùng hồ sơ có sẵn. [STG-chạy 09/11]
- Thêm 2 hồ sơ thử bằng ảnh CV do người dùng gửi: 32953, 32954 (mục 5). [STG-chạy 09/11]
- Kết quả check tay của người dùng: **chưa ghi vào file này**.
- Phạm vi: masking áp dụng cho mọi công ty, chỉ trừ VJP. [User 08/11, RM-75015] Redmine #70538 và SRS còn ghi chỉ VTI.

Link hồ sơ: `https://vms-ta.stg.vti.com.vn/web#id=<id>&action=739&model=hr.applicant&view_type=form&menu_id=569`
Link dòng Review CV: `https://vms-ta.stg.vti.com.vn/web#id=<line>&action=758&model=hr.applicant.lines&view_type=form&menu_id=585`
Tạo lại bảng đầy đủ: `python scripts/report_dataset_70538.py` → `output/dataset_70538.md`

## 2. Bộ data  [STG-chạy 09/11]

| ID | Hồ sơ | Nội dung | Trạng thái | Tài khoản | Check |
|---|---|---|---|---|---|
| D01 | 32937 | PDF có chữ | Đã che | `chau.phamminh` | BR1, 2, 3, 5, 6, tải/in |
| D02 | 32938 | PDF scan | Đã che | `chau.phamminh` | BR4, BR5 |
| D03 | 32939 | PNG | Đã che, 22 vùng | `chau.phamminh` | BR4, BR5 |
| D04 | 32940 | JPG | Đã che | `chau.phamminh` | BR4, BR5 |
| D05 | 32950 | Nhiều file | Đã che, 2 bản | `chau.phamminh` | BR5 |
| D06 | 32951 | Giới hạn BR12 | Đã che | `chau.phamminh` | Chỉ ghi nhận |
| D07 | 32941 | Source VJP | Không có bản che | `trung.phambao` | Như cũ |
| D08 | | Source GITS_REC | **Chưa tạo** | | Xem mục 6 |
| D09 | 32952 | Source HRI | Đã che | `thanh.hoang1` | BR9 |
| D10 | 32942 | Đổi CV | Đã che | `chau.phamminh` | Tự upload `output\dataset_70538\CV09_D10_minhdinh.pdf` |
| D11 | 32943 | Thay Masked | Đã che | `chau.phamminh` | Thay bằng `output\dataset_70538\CV11_D11_vyphan.pdf`, bấm Recreate |
| D12 | 32944 | Dòng Draft | Chờ người dùng Submit | `chau.phamminh` | BR7, BR8 |
| D13 | 32945 | Dòng 20364 | Submitted | `tinh.giangthi`, `dang.nguyenhuu` | BR7, BR9, E_007 |
| D14 | 32946 | Dòng 20365 | Accepted + Meeting | `minh.hoangkim` | BR7, BR9 |
| D15 | 32947 | File hỏng | Che lỗi, dòng Draft | `chau.phamminh` | E_005, Submit phải bị chặn |
| D16 | 32948 | File hỏng | Che lỗi, dòng Draft | `chau.phamminh` | Như D15 |
| D17 | 21550 | CV cũ (dự phòng 21549, 21547) | Không có bản che | `chau.phamminh` | Upload lại thì phải che |
| D18 | 32949 | Submit ngay | Submitted | `chau.phamminh` | BR8 đã khớp: trước Submit `pending`, sau Submit `done` |

File CV gốc để test link E_007: D13 `/web/content/331743?download=true`, D14 `/web/content/331746?download=true`. [STG-API 09/11]

## 3. Chỗ cần check theo tài khoản

### TA (`chau.phamminh`)
| Chỗ | Kỳ vọng | Nguồn |
|---|---|---|
| Form Application, ô CV Masked (D01) | Có `_masked.pdf`, liên hệ đã che | BR1–BR5, [SRS AP-01 S228] |
| Chatter (D01) | Có dòng báo đã tạo bản che | BR6 |
| Menu Review CV → dòng → mục "CV (s)" (D13) | `_masked.pdf` | BR7, [SRS AP-01 S229] |
| Form Application → icon con mắt (D13) | **Cần hỏi BA**, xem mục 6 | [SRS AP-01 S231] |

### Reviewer, Interviewer, DL
Dùng `tinh.giangthi` và `dang.nguyenhuu` với D13; `minh.hoangkim` với D14.

| Chỗ | Kỳ vọng | Nguồn |
|---|---|---|
| Recruitment → Applications → Review CV → mở dòng → mục "CV (s)" | Bản đã che | BR7 |
| Chatter của dòng | Không có CV gốc | BR9 |
| Dán link CV gốc | Bị chặn, báo E_007 | BR9 |

Ba role này **không có** All Applications, nên không vào được form Application. Phần "không thấy ô CV Attachment" của BR9 coi như đạt. [STG-chạy 09/11] [SRS sheet Phân quyền U31, U33, U34]

Không bấm Accept/Reject ở D13 để giữ data. `hieu.bachduy` cũng nằm trong Reviewer/Interviewer của RR, không dùng để check BR9 vì STG tự thêm theo DL. [STG-chạy 09/11]

### Các role khác theo [SRS mục 3.5]
| Role | Tài khoản | Tình trạng |
|---|---|---|
| Partner | `thanh.hoang1`, D09 | Làm được: CV gốc của mình xem được, CV Masked xem được, không thay được; file người khác phải E_007 |
| Partner Manager | `thuy.nghiemthanh` | Chưa có hồ sơ do tài khoản này upload |
| BOD | `giang.trinh` | Không đọc được D13, D14 [STG-API]; cần hồ sơ khác |
| Rec Manager | `trung.phambao` (VJP) | Hồ sơ VTI có thể không thấy [Claude] |
| Admin System không thuộc REC, nhân viên giới thiệu | | Chưa có tài khoản |

### Tài khoản và phân quyền đã xác minh  [STG-API, STG-chạy 09/11]
| Tài khoản | Group Recruitment | Gán vào RR01415 | Menu trong Applications |
|---|---|---|---|
| `tinh.giangthi` | Reviewer, Interviewer | Reviewer | Review CV, Applications Process |
| `minh.hoangkim` | Interviewer | Interviewer | Review CV |
| `dang.nguyenhuu` | DL, Interviewer | DL | Review CV, Applications Process |

Không phải do status: D13 (Submitted) và D14 (Accepted) đều không mở được form bằng link có `action=739`. `tinh.giangthi` nhận Access Error "Ban khong co quyen mo man hinh nay"; với `minh.hoangkim` sau 7 giây không hiện form. Thanh menu bên trái thu gọn mục con, phải mở Recruitment mới thấy.

`minh.hoangkim` không đọc được dòng D13 là đúng: Interviewer chỉ thấy dòng đã Accept. [SRS sheet Phân quyền, bảng Review CV]

## 4. Màn View CV và mail

**"Màn View CV (review CV / phỏng vấn)"** [RM-70538 BR7] là chỗ đọc CV ở hai thời điểm: DL/Reviewer đọc để Accept/Reject, Interviewer đọc để phỏng vấn. [SRS AP-01 P231] gọi là popup. Không có menu tên View CV. Redmine không nêu nút cụ thể.

Lối vào trên STG [STG-API 09/11]:
| Chỗ | Ghi chú |
|---|---|
| List Applications: nút View CV | Chỉ có nút này, không có nút tên "Review CV". [SRS AP-01 P115] để trống mô tả |
| Form Application: icon con mắt không chữ | Hiện khi không ở chế độ Edit. Cùng chức năng với nút trên list, mở popup view 8293 |
| Menu Review CV: nút View CV trên dòng | TA thấy; Reviewer, Interviewer, DL bị ẩn |
| RR → bảng Applicants: icon con mắt | Chưa thử mở file nào |
| Form Interview Result: `view_cv` | Chưa thử; D14 chưa có Interview Result |

Popup 8293 dùng trường `cv_view_attachment_ids`, giá trị khác theo người xem: TA ra **CV gốc**, Reviewer/DL/Interviewer ra `_masked.pdf`. Mục "CV (s)" dùng `cv_attachment_ids`, mọi tài khoản đều ra `_masked.pdf`. [STG-API 09/11]

**Mail "Applicant: Submit CV"** (mail.template id 74) [STG-API 09/11]:
- Gửi khi TA bấm Submit CV và qua điều kiện: không Duplicate, RR Open còn số lượng [SRS AP-01 S64]; có Working/Intern History, trừ RR VJP [SRS AP-12 K38]; CV Masked sẵn sàng [BR8].
- To lấy từ `get_created_user_email` và `get_reviewer_email`, theo tên hàm là DL và Reviewer [Claude]. CC là email của Source (Source TA: `hoai.nguyenthithu@vti.com.vn`). File lấy từ `cv_attachment_ids` của dòng.
- Không tìm thấy mail thật: chatter D13 không có file, `mail.mail` không có kết quả. Ghi **Blocked**, nhờ Dev xác nhận.

## 5. Lỗi nghi ngờ: CV dạng ảnh vẫn lộ liên hệ  [STG-chạy 09/11]

Ảnh CV do người dùng gửi, `chau.phamminh`, Source TA, Save. Tên/SĐT/email trên form là dữ liệu test. Ảnh gốc nằm ở `output/cv/` (không commit vì chứa liên hệ thật).

| | 32953: ảnh gốc | 32954: ảnh x3 |
|---|---|---|
| Kích thước | 557 × 716 px, màu | 1671 × 2148 px, xám (để dưới 800 KB) |
| Trạng thái | Done | Done |
| Chatter | 0 vùng | 1 vùng |
| SĐT | **Lộ** | Đã tô đen |
| Email | **Lộ** | **Lộ** |

- Trái BR1, BR4. BR12 không loại trừ trường hợp này. Hệ thống báo Done nên TA không biết còn sót.
- D03 (PNG tự sinh) che được 22 vùng, nên không phải mọi PNG đều lỗi. Độ phân giải có ảnh hưởng nhưng 32954 khác 32953 cả màu lẫn kích thước, chưa tách riêng được. [Claude]

## 6. Cần hỏi BA/Dev

1. Popup View CV của TA đang là CV gốc. [SRS AP-01 S231] ghi hiển thị CV Masked; [RM-70538 mục 2] ghi "Reviewer và TA xem bản CV Masked". Có phải bug không?
2. "Màn View CV" trong BR7 gồm những chỗ nào: "CV (s)", nút ở list Applications, icon trong RR, hay cả Interview Result?
3. Sửa link bỏ `action` thì Reviewer/Interviewer vẫn mở được form qua "My Applications Reference" (`/web#id=<id>&model=hr.applicant&view_type=form`): không có CV gốc nhưng **Email, Mobile hiện rõ**. Có chấp nhận được không? [STG-chạy 09/11]
4. D09: Partner bấm Save báo Access Error đọc `vti.recruitment.nda` nhưng hồ sơ vẫn tạo. [SRS AP-01 L176] ghi Partner được tạo CV.
5. Chữ "Github" trong CV dạng ảnh, không có địa chỉ link, có phải che không?
6. Các câu còn mở ở `task-73087-masking-test-tom-tat.md` mục 6.

**D08 (GITS_REC) chưa quyết:** `chau.phamminh` đang ở VTI nên dropdown không có. Đề xuất bỏ vì D09 đã phủ công ty khác VTI [Claude]; nếu cần thì đổi tạm công ty hoặc xin tài khoản GITS. [STG-API 09/11]

Chưa chuẩn bị được: Get CV Info, Website, Copy, BR11/E_003, Word, E_001, TCVN3.

## 7. Đính chính so với `task-73087-masking-test-tom-tat.md`

- Mục 6 ghi "Form Application không có nút View CV": **sai**, có icon con mắt. [STG-API 09/11]
- "Dòng Review CV, cột CV Attachment": cột này bị ẩn trên bảng ở form Application. File xem ở mục "CV (s)" của form CV Review. [STG-API 09/11]

## 8. File liên quan

| File | Vai trò |
|---|---|
| `data/application/dataset_70538.json`, `data/rr/rr_70538.json` | Data đã chốt |
| `tests/test_dataset_70538.py` | Tạo data, chạy lại an toàn (dòng xong thì bỏ qua) |
| `tests/test_rr_set_people.py` | Đặt Reviewer/Interviewer cho RR |
| `scripts/report_dataset_70538.py` | Xuất bảng kết quả, chỉ đọc |

Hàm chọn Reviewer/Interviewer khi tạo RR đã sửa nhưng chưa chạy lại trọn bước tạo RR. [Claude]
