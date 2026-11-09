# Task #73336 / #73337: kiểm chứng lỗ hổng sửa lương OL (OL Reject)

> Bàn giao phiên 09/11/2026. **Đang làm dở, chưa test phá lần nào.**
> Mục tiêu [User]: chạy thật trên STG để xác nhận **hiện trạng**, kiểm tra 6 lỗ hổng do AI rà từ code có đúng không. Việc "có phải bug không" để BA chốt sau.
> Nhãn nguồn: [RM-73336] Redmine task cha; [RM-73337] task con; [SRS ô] file `VMS_Module_TA_SRS_v1.1 (1).xlsx`; [STG-API] đọc qua API; [STG-chạy] kết quả chạy thật; [User]; [Claude] suy đoán, chưa chứng thực.

## 1. Đang dừng ở đâu

| Mục | Giá trị | Nguồn |
|---|---|---|
| RR riêng cho flow | RR01416 (id 1803), Open | [STG-chạy] |
| Hồ sơ A | 32955, Trần Quốc Lương A | [STG-chạy] |
| Kết quả phỏng vấn | KQ08356 (id 8631), `state = pass`, `stage_interview = bod_review`, `is_noti_dl = done` | [STG-chạy] |
| Mức offer đã nhập | Range 20.000.000 – 22.000.000 VND, Member, thử việc 85% | [STG-chạy] |
| Stage ứng viên | Pass (id 4) | [STG-chạy] |
| OL | **Chưa tạo** | [STG-chạy] |

Sau khi Confirm offer, kết quả nhảy thẳng sang `bod_review`, không qua `dl_review`. Lý do chưa rõ. [STG-chạy] + [Claude]

**Việc tiếp theo cho hồ sơ A:**
1. Duyệt offer ở bước BOD Review, có thể cả RM Review. Nút nằm ở bảng `answer_ids` trên form Application (Approved / Reject / Pending Offer theo vai trò). [STG-API, chưa chạy]
2. Đến bước Recer Feedback, TA bấm **Accept OL** (`pop_up_approved_offer`). Ứng viên sang stage Accept OL (id 53). [SRS OF-04 ô M43]
3. Bấm **Offer** (`create_offer`) trên form Application, chỉ hiện ở stage 5 hoặc 53. [STG-API + SRS OF-01 ô D11]
4. OL: Submit (`set_to_submit`) → Rec Manager Approve (`pop_up_set_to_approve`). [STG-API + SRS OF-01 ô E118, E119]
5. Có OL Approved thì bắt đầu test phá mục 2 (mục 4 bên dưới).

## 2. Yêu cầu của task

- #73337 giao cho Mai, là task BA: đọc 6 lỗ hổng, chốt quy tắc sau khi có OL, chốt mục 4 và 5, cập nhật SRS, báo tạo task Dev/Test/Deploy. [RM-73337]
- Bằng chứng chạy thử STG "sẽ bổ sung ở note", hiện chưa có note. [RM-73336]

## 3. Bảng 6 lỗ hổng: AI nói gì, đã kiểm được gì

Mới quét đọc qua API, **chưa mục nào có kết quả test phá**.

| # | AI nói [RM-73336] | Đã kiểm [STG-API] | SRS | Còn phải chạy |
|---|---|---|---|---|
| 1 | Stage nào cũng sửa được lương, gọi thẳng `action_recer_confirm` qua RPC bỏ qua kiểm tra | Khớp một phần: 2 nút Update salary không xét stage ứng viên. Nút Update chỉ hiện ở OL Rejected (6) và Accept OL (53) | | Sửa ở Pass, On board; gọi RPC |
| 2 | OL Submitted/Approved vẫn sửa được lương qua RPC/Import; PDF in lại; OL vẫn Approved | Chưa đủ căn cứ: `final_salary` không readonly ở model; 2 tài khoản không đọc được `ir.rule` | Chỉ sửa khi Draft [OF-01 ô D13] | Sửa theo từng role, xem PDF |
| 3 | OL Final không đối chiếu lương đã duyệt | Chưa kiểm được | Final salary tự lấy mức đã duyệt; chỉ Pre-offer có luật Min–Max [OF-01 ô S43] | Nhập lệch mức 20–22 triệu |
| 4 | VJP: nút Update không ẩn "như 2 nút Update salary"; OL đang DL/BOD Review không bị chặn | **Đúng một nửa:** nút Update đúng là không có điều kiện VJP, nhưng chỉ 1 trong 2 nút Update salary ẩn với VJP. Nút ở nhánh `dl_reject_offer` không có điều kiện `company_code` | DL/BOD Review chỉ dùng cho Offer VJP [OF-01 ô S22] | Quét bằng tài khoản VJP; chạy thử |
| 5 | Update salary vẫn hiện khi Pre-offer đã Submitted/Approved | Khớp phần nút: điều kiện hiện không xét trạng thái Pre-offer letter | | Bấm thử, xem Pre-offer cũ |
| 6 | Đoạn code không bao giờ chạy | Không kiểm được từ ngoài | | Cần source hoặc Dev xác nhận |

Số dòng code và commit AI trích dẫn: **chưa đối chiếu được**, vì không có source. [User 08/11]
Quét bằng 2 tài khoản VTI: `chau.phamminh`, `truong.dangvan`. `chau.phamminh` có quyền ghi OL ở mức model dù task không liệt kê TA ở mục 2, nên thử cả role này. [STG-API]

## 4. Kế hoạch test phá

| Hồ sơ | Dừng ở | Mục | Cách phá |
|---|---|---|---|
| A | OL Approved | 2 | Từng role sửa lương qua RPC; xem OL còn Approved không, PDF có in lại không |
| B | OL Submitted | 2 | Như A |
| C | OL Draft | 3 | Nhập lương lệch mức đã duyệt |
| D | Stage Pass | 1 | Sửa lương; gọi thẳng `action_recer_confirm` |
| E | On board | 1 | Sửa lương, xem có bị chặn không |
| F | Pre-offer Submitted/Approved | 5 | Update salary, xem Pre-offer cũ |
| G | OL VJP đang DL/BOD Review | 4 | Update khi OL đang review |

Người dùng đã đồng ý tạo hồ sơ test và cố ý sửa lương, gọi thẳng RPC trên STG, **chỉ trên hồ sơ do test tạo**, không đụng OL có sẵn. [User 09/11]

Tài khoản thử: BOD `giang.trinh`; Rec Manager `truong.dangvan` (nhiều role); Module Admin `hoai.nguyenthithu` (nhiều role, người duy nhất của nhóm); HRI `thanh.hoang1`; Partner Manager HRI `thuy.nghiemthanh`, dự phòng `hong`. [STG-API] Chưa thử đăng nhập `thuy.nghiemthanh`, `hong`.

## 5. SRS nói gì về OL

- "OL Reject" có hai nghĩa: ứng viên trong RR bị chuyển sang OL Reject, hoặc Offer của ứng viên bị reject. [SRS AP-11 ô B7]
- Trạng thái Offer: Draft → Submitted → Approved; Rejected khi bị từ chối. DL/BOD Review chỉ cho VJP. [SRS OF-01 ô S22]
- Reject chỉ ở Submitted, do Rec Manager. [SRS OF-01 ô E120] Trên form, nút Reject cũng chỉ hiện khi Submitted, Set to draft chỉ khi Rejected. [STG-API, tài khoản `truong.dangvan`]
- OL Approved quay lại được bằng Adjusted OB date (về Submitted, chỉ để đổi ngày onboard). [SRS OF-01 ô E122]
- Update Salary: TA bấm ở bước Recer Feedback. [SRS OF-04 ô M45] Đổi Signing Bonus, Adhoc Project, Onsite Allowance, Incentives, Adjusted income thì quay lại DL duyệt. [SRS OF-04 ô M145–M149]
- SRS **không nói** cách Reject một Offer đã Approved, dù AP-11 ô M18 nhắc Offer bị reject khi New Employee đang xử lý. Cũng không có câu nào quy định phải Reject OL trước khi sửa lương theo từng vai trò. [Claude đọc SRS theo từ khóa, chưa đọc hết]

## 6. Flow đã chạy được (hồ sơ A)

| Bước | Ai | Thao tác | Kết quả |
|---|---|---|---|
| 1 | DL `truong.dangvan` | Tạo RR, Submit | To approve |
| 2 | BOD `hoai.nguyenthithu` | Approve RR | Open |
| 3 | TA `chau.phamminh` | Tạo hồ sơ, Working History, dòng Review CV, Submit CV | Dòng `submit` |
| 4 | DL | Accept CV (2 hộp thoại) | Dòng `accept` |
| 5 | TA | Add a Meeting giờ quá khứ | Có Meeting |
| 6 | DL | Màn RR → Create Result → Save | KQ `draft` |
| 7 | DL | Bấm Pass (`create_next_pass_result`) | KQ `in_progress`, ứng viên Interviewed, mở popup phiếu |
| 8 | DL | Link Edit → điền phiếu → Final Result **trong popup** (`action_final_result`) | `interview_result = pass`, mở popup Nhập Offer |
| 9 | DL | Nhập Offer → Confirm (`confirm_submit_interview`) → hộp xác nhận | KQ `pass`, `bod_review`, ứng viên Pass |

## 7. Bài học khi chạy [STG-chạy]

- Form kết quả phỏng vấn **phải vào từ dòng ứng viên trên RR**. Mở thẳng URL thì Odoo dùng form 1680, không có nút Pass.
- Sau khi có kết quả, `create_result` của RR đổi thành False, bảng ứng viên đổi từ `new_rr_applicants_ids` sang `rr_applicants_ids`. Tìm nút `view_interview_result` không gắn với bảng nào.
- Sau đăng nhập Odoo có lúc đè trang mặc định lên URL vừa mở: dùng `_open_until`.
- Nút Final Result trên form chính (`finish_interview`) bấm không có tác dụng gì; phải dùng nút trong popup phiếu.
- Phiếu lưu ở `vti.multi.interview.answer`, không phải `line_ids`. Mỗi câu có đủ các ô `answer_*`, chỉ 1 ô hiện: ghép theo thứ tự nhãn và ô đang hiện.
- Câu chọn lấy dòng đầu danh sách sẽ ra Level "Thực tập", nên điền giá trị theo phiếu mẫu KQ08353.
- Popup Nhập Offer: `salary_rate` là `<select>`, không phải radio.
- `save()` của RR chờ 5 giây là quá ngắn, đã nới 30 giây (`pages/resource_request_page.py`). Chưa chạy lại `test_create_rr` đầy đủ, mới chạy qua `test_rr_set_people`.
- Khi Submit RR có hiện lỗi "records are not in draft state", RR vẫn sang To approve. [Claude] có vẻ Submit bị gọi hai lần, chưa điều tra.

## 8. Chạy tiếp trên máy khác

- Code: `tests/test_offer_73336.py`, data: `data/application/offer_73336.json`.
- `output/` không theo git. Tạo lại `output/offer_73336_state.json`:

```json
{"A": {"app_id": 32955, "user": "chau.phamminh", "rr": "RR01416", "name": "Trần Quốc Lương A", "answer_id": 8631, "meeting_done": true}}
```

- Không chạy lại `test_fill_score_popup` cho hồ sơ A: kết quả đã `pass`, không sửa được nữa. `test_application_to_meeting`, `test_create_interview_result` chạy lại an toàn (có kiểm tra trước khi tạo).
- `test_click_answer_button`: bấm một nút trên form kết quả. Biến môi trường: `BTN`, `ACT_USER`, `RID`, `DRY=1` (chỉ ghi lại các nút).
- `SRS`: chỉ có ở `E:\Downloads` máy nhà, không đưa lên git, cần file ở máy công ty nếu muốn tra lại.
- Rác trên STG cần dọn khi xong: RR01416, hồ sơ 32955 và các hồ sơ test sau này (xin phép người dùng trước). `output/inspect_*.json` có dữ liệu mẫu, đang nằm ở máy nhà.
