# Dữ liệu form và dropdown đã quét qua XML-RPC (STG, 04/11/2026)

> Ghi lại để lần sau tạo data cho tài khoản khác không phải quét lại. Nguồn tất cả: **[STG-API]**, tài khoản `chau.phamminh` (TA).
> Cách quét: `scripts/inspect_model.py <model> <user> [view_id]`. Gọi API tự viết thì lưu ý bên dưới.

## 0. Bài học khi quét (đã vấp)
- **Dropdown phải áp domain của ô**, không chỉ đọc cả bảng. Lấy domain bằng `fields_get(<ô>, attributes=["domain"])`, rồi `search_read` với domain đó. Ví dụ: "Others" có trong bảng `recruitment.reject.reason` nhưng **không hiện** ở ô Resignation Reason vì ô lọc `apply_for = 'resignation_reason'`.
- `fields_view_get` của `hr.applicant` và `hr.applicant.lines` phải truyền `[]` làm tham số đầu: `call(model, "fields_view_get", [], view_id, "form")`. Của `applicant.working.history` thì truyền tham số tên: `view_id=..., view_type="form"`.
- API **không** cho biết class HTML của widget (nút xóa file CV là `.oe_attachment .oe_delete`, ô upload là `div[name=cv_attachment_ids] input[type=file]`).
- API **không** biết lỗi do Python kiểm tra lúc bấm nút. Ví dụ Submit CV báo "Please kindly provide Working History or Intern History details information." chỉ lộ ra khi chạy.


## 0b. Quy tắc chung cho popup (form mở trong hộp thoại)  [STG-chạy, User xác nhận 04/11/2026]
API **không** báo trước các điều này, nên áp dụng sẵn cho mọi popup có nút Save:
1. **Save xong popup VẪN MỞ**, chuyển sang chế độ xem (hiện nút **Edit** và **Create** ở chân). Phải bấm nút **×** góc phải đầu popup (`.modal-header button.close`) mới đóng. Đã gặp ở Add Working History và Create a meeting.
2. Cách biết đã lưu xong: chờ nút `button.o_form_button_edit` hiện **trong popup**. Nếu không hiện mà có thông báo lỗi thì Save bị chặn.
3. **Ô dropdown (many2one, many2many tags) và ô ngày giờ phải chốt giá trị**: dropdown chọn dòng trong danh sách rồi đóng danh sách; ô ngày giờ gõ xong phải nhấn **Enter** (bảng chọn ngày vẫn mở, giá trị chưa nhận nếu không Enter). `set_field` đã làm sẵn.
4. Nút trong thân form popup là `button.o_form_button_save` (không phải `.modal-footer`). Hộp xác nhận (Confirm/Cancel) thì ở `.modal-footer`.
5. Trước khi điền ô trong popup phải đổi phạm vi tìm ô sang popup (`_scope`), vì tên ô trùng với form chính (ví dụ `business_domain_id`, `current_company_id`).

## 1. Popup Add Working History (nút `action_open_add_working_history`, model `applicant.working.history`, form view 8358)
Nút nằm trên form Application, bấm được khi hồ sơ đã Save. Popup có nút **Save / Discard** nằm trong thân form (không phải `.modal-footer`).

| Ô (name) | Nhãn | Bắt buộc | Loại / nguồn dropdown | Giá trị đã dùng |
|---|---|---|---|---|
| `current_company_id` | Current Company | **Có** | many2one `recruitment.company`, domain `waiting_approve = False` | Đại học FPT |
| `company_size` | Company Size | **Có** | selection | `100 - 500 người` |
| `package` | Package | **Có** | selection | `13 Tháng / Năm` |
| `benefit` | Benefit | Không | text | |
| `business_domain_id` | Business Domain | **Có** | many2one `business.domain`, domain: không gắn công ty hoặc công ty id 1 | Giáo dục |
| `business_domain_ids` | Sub Business Domains | Không | many2many | |
| `personal_healthcare` | Personal Healthcare | **Có** | selection `Yes` / `No` | Yes |
| `project_scale` | Project Scale | **Có** | selection | `10 - 20 người` |
| `role_project_ta_ids` | Role in the Project | **Có** | many2many tags `hr.job.ta` (647 bản ghi), domain `waiting_approve = False` | Others (có 2 bản ghi trùng tên: id 26 và 364) |
| `reason_resignation_job_id` | Resignation Reason | **Có** | many2one `recruitment.reject.reason`, domain `apply_for = 'resignation_reason'` | Có lý do cá nhân |
| `reason_detail` | Reason Detail | **Có** | text | Tim moi truong phat trien hon |
| `market_id`, `country_location_id`, `province_location_id`, `notes` | Market, Location, Province, Notes | Không | | |

Giá trị selection đầy đủ:
- `company_size`: `<100 người`, `100 - 500 người`, `500 - 1000 người`, `1000 - 1500 người`, `>2000 người`
- `package`: `12`, `13`, `14`, `15`, `>15 Tháng / Năm`
- `project_scale`: `<10 người`, `10 - 20 người`, `20 - 50 người`, `>50 người`

**Resignation Reason hợp lệ (11, `apply_for = resignation_reason`):** Có lý do cá nhân (78), Chuyển nơi sinh sống nên quãng đường đi lại quá xa (79), Có kế hoạch đi du học hoặc tập trung học tập dài hạn (80), Do môi trường làm việc chưa phù hợp (81), Thu nhập hiện tại chưa phù hợp với năng lực và kỳ vọng (82), Chính sách hoặc chế độ của công ty thay đổi (83), Muốn thay đổi môi trường làm việc để học hỏi và trải nghiệm thêm (84), Công ty cắt giảm nhân sự (85), Hết hạn hợp đồng và không tiếp tục ký gia hạn (86), Muốn thay đổi định hướng nghề nghiệp (87), Lý do khác (Other). (88)

**Business Domain hợp lệ (13):** 42 Bán lẻ, 43 Giáo dục, 44 Logistics, 45 Viễn Thông, 46 Tài Chính, 47 Bất Động Sản, 48 Fintech, 49 Bảo Hiểm, 50 Thương mại điện tử, 51 Gọi xe, 52 Ngân Hàng, 53 Y Tế, 54 Khác. (Các id 1–8 là tên tiếng Nhật, thuộc công ty khác.)

Hồ sơ thực tập sinh dùng `applicant.intern.history` (nút Intern History), chưa quét form. Các ô model: `current_company_id` (Current University), `major`, `class_size`, `current_year_id`, `expect_graduation`, `gpa`, `gpa_scale` (`4`/`10`), `notes`.

## 2. Review CV (bảng `applicant_line_ids`, model `hr.applicant.lines`)
- Bảng sửa ngay trên form Application (widget `section_and_note_one2many`, mode tree). Thêm dòng bằng **Add a line**.
- Ô chính: `resource_request_id` (RR), `state` (`draft` / `submit` / `accept` / `reject`), `cv_attachment_ids` (**file CV hiện trên dòng, nơi kiểm tra BR7**), `submit_date`, `interviewer_ids`, `department_id`.
- Nút trên dòng: **Submit CV** (`submit_cv`, xác nhận "Submit this CV and send an email to reviewer."), Accept CV (`accept_cv_form`, ẩn khi chưa Submit, xác nhận "Accept this CV and send an email to recruitment."), Reject CV (`reject_cv`), Set to Draft (`set_to_draft`, xác nhận "Draft CV."), Fail CV (action 4016), Pending Process.
- RR tìm theo `code` (không phải `name`). RR01413 id 1799 đang `open`. RR01414 id 1801 đang `draft`.
- **Submit CV bị chặn nếu hồ sơ chưa có Working History** (hoặc Intern History).

## 3. Source VTI và VJP (`utm.source`, có ô Company)
- VJP: 23 VJP, 115 Facebook, 116 Linkedin, 117 Hellowork, 118 Fanpage, 119 説明会, 120 Mail, 121 Jobfair, 122 Webinar, 123 Others, 124 ERP, 167 VJP Recruitment: Mail Offer, 168 Web_Active_VJP.
- VTI (một phần): 6 TA, 9 ITViec, 10 ERP, 11 Topdev, 12 TopCV, 27 Web_Active, 105 Website_ERP, 160 Web_Refer, 24 VTI - VJP.
- Bẫy trùng tên: "ERP" có ở VTI (10) và VJP (124); "Facebook", "Others" có ở VJP và ở source không công ty. Khi test VJP chọn **"VJP"** (id 23, tên duy nhất).
- Source VJP làm ẩn 4 ô Business Domain, Recruitment Type, Working Type, Main Market trên form Application.

## 4. Tài khoản theo role
Xem `docs/task-73087-masking-test-tom-tat.md` mục 12, và `output/accounts_by_group.txt`, `output/accounts_pure_roles.txt`.

## 5. Ai thấy dòng Review CV  [STG-API 04/11/2026]
- Dòng Review CV chỉ hiện với người **gắn với RR của dòng đó** (Reviewer, Interviewer, DL của RR), cộng nhóm TA. Tài khoản thuần role nhưng không gắn RR thì **không thấy cả Application lẫn dòng Review CV**.
- RR01413 (id 1799): DL = Reviewer = Interviewer = SM = `truong.dangvan`. BOD Approve gồm 6 người. Người duy nhất thấy dòng 20260 và hồ sơ 32721 là `truong.dangvan` và `hoai.nguyenthithu`, cả hai đều có role Rec Manager nên **thấy CV gốc, không dùng để test BR9**.
- Đã thử không thấy: `dang.nguyenhuu` (DL thuần), `tinh.giangthi`, `tuan.maivan` (Reviewer thuần), `minh.hoangkim`, `viet.hoangquoc` (Interviewer thuần), `giang.trinh` (BOD thuần).
- Dòng 20260: Department VTI.VMS, Department Manager = Đào Thị Thu Hiền (`hien.daothithu`, thuộc DL, BOD, Rec Manager).
- Muốn test BR9 phải tạo RR có Reviewer/Interviewer/DL là tài khoản thuần, ví dụ Reviewer `tinh.giangthi`, Interviewer `minh.hoangkim`.

## 6. Luồng Accept CV của DL  [STG-chạy 04/11/2026]
Vào: menu **Recruitment > Applications > Review CV** (menu 585, action 758), mở dòng, hoặc link trực tiếp `/web#id=<line_id>&action=758&model=hr.applicant.lines&view_type=form&menu_id=585`.
- Nút **Accept CV** (`accept_cv_form`) chỉ hiện khi dòng ở trạng thái `submit` (và không trùng CV). Reject CV cùng điều kiện. Set to Draft chỉ hiện khi dòng `reject`.
- **Accept có 2 hộp thoại liên tiếp:**
  1. Hộp xác nhận: "Accept this CV and send an email to recruitment." (Confirm / Cancel). Dòng này **có thể quét trước** từ thuộc tính `confirm` của nút.
  2. Popup **"Accept CV"**: ô **Interviewer** (many2many, tự điền sẵn người phỏng vấn của RR) và ô **Message** (không bắt buộc), nút **Accept** (`name="accept_cv"`) / Cancel. Popup này do hàm Python của nút trả về nên **API không báo trước**. Chưa tìm ra model của wizard qua `ir.ui.view`.
- Form dòng Review CV hiển thị mục "CV (s)" nhúng trực tiếp file CV (iframe `/web/content/<id>?embedded=true`). Ở dòng 20260 file này là bản `_masked.pdf` (id 326249).
- Sau Accept: `state` = `accept`. File CV trên dòng vẫn là bản Masked.
- Lưu ý khi viết test: xử lý từng hộp thoại, thấy nút `accept_cv` thì bấm nó, không thì bấm Confirm.

## 7. Add a Meeting (TA)  [STG-API + STG-chạy 04/11/2026]
- Nút `add_meeting_room` trên form Application, hiện khi hồ sơ đã Save, không phải draft, không trùng CV. Bấm mở wizard `meeting.room.wizard`. Quét API: các ô `resource_request_id` (many2many RR), `action` (`add` Add Meeting / `cancel` Cancel Interview / `add_rr` Add RR), `interview_type_id` (Face to face, Skype, Online, Offline), `interview_round_id` (日本語面談, 一次面接, 最終面接, 内定面談), `stage_id` và `reason_id` (chỉ cho Cancel Interview, reason domain `apply_for = cancel_interview`), `message`, `update_status` (No/Yes).
- Meeting lưu ở model `recruitment.interview.meeting` (field `meet_ids` trên Application). Hồ sơ 32721 chưa có meeting nào trước lần thử này.
- **Popup đầu tiên (chạy thật)**: "Create a meeting", ô **Resource Request** (bắt buộc) tự điền **RR01413** (RR đã Accept), câu "We have automatically added the accepted requests. Please check the information again before confirming!", nút **Confirm** (`name="add_meeting"`) và Cancel.
- Ô Interview Type và Interview Round **không hiện ở popup đầu tiên**, có thể ở bước sau.
- **Popup thứ hai (chạy thật, sau khi bấm Confirm)**: form "Create a meeting" (lịch họp `calendar.event` dạng tiện ích của VTI), nút **Save / Discard**. Các ô:

| Ô (name) | Nhãn | Bắt buộc | Giá trị tự điền |
|---|---|---|---|
| `name` | Subject | Có | "Phỏng vấn Business Development Junior - Nguyễn Văn Kiểm" |
| `partner_ids` | Attendees | | VTI Corporation, Đặng Văn Trường, Phạm Minh Châu, Nguyễn Thị Thu Hoài, Ngô Bích Diệp, Phạm Bảo Trung |
| `invite_by_email` | Invite email | | **bỏ tích** |
| `create_meet_link` | Google Meet | | bỏ tích |
| `start_datetime` | Starting at | **Có** | trống |
| `stop_datetime` | Ending at | **Có** | trống |
| `duration` | Duration | | 00:00 |
| `department_ids` | Cost-bearing departments | Có | VTI.VMS |
| `project_id`, `room_id`, `description`, `allday` | Project, Room, Description, All Day | | trống |
- Attendees tự thêm nhiều người thật (kể cả `hien.daothithu`, `diep.ngobich`, `trung.phambao`). Lưu cuộc họp có thể gửi thư mời đến họ trừ khi ô Invite email bỏ tích. Chưa kiểm chứng việc có gửi mail hay không.
- **Tạo được cuộc họp** (id 200, hồ sơ 32721) với giờ ở quá khứ: 03/11/2026 10:00–11:00 (định dạng ô giờ `dd/mm/yyyy HH:MM:SS`), chỉ giữ người tham dự `Đặng Văn Trường`, Invite email và Google Meet bỏ tích. Sau Save popup **vẫn mở** ở chế độ xem (nút Edit, Create), phải bấm × để đóng. Hệ thống không chặn giờ trong quá khứ. [User]: phải dùng giờ quá khứ thì mới tạo được Interview Result.

## 8. Interview Result (quét API 04/11/2026, chưa chạy thật)
Model `vti.interview.answer`. Có **2 chỗ** liên quan:
1. **Trên form Application**, khối "Interview result" (`interview_result`): ô `answer_ids` (widget tùy biến `multi_interview_result_o2m`, hiện khi `has_vti_interview`), và `multi_answer_ids` (cùng widget, hiện khi `has_vjp_interview`, dùng cho VJP). Khối chỉ hiện khi hồ sơ đã Save. Nút thêm kết quả nằm trong widget, **chưa biết tên nút**, API không báo.
2. **Menu Recruitment > Interviews > Interview Result** (menu 587, action 764, domain: RR không thuộc VJP) là danh sách các kết quả, có thể dùng để kiểm tra. Menu VJP: "VJP Interview Results V1" (2938) và "V2" (2936).
- Ô bắt buộc của bản ghi: `applicant_id`, `vti_survey_id` (mẫu đánh giá, `vti.interview.template`), `state` (`draft`, `in_progress`, `fail`, `pass`).
- Ô khác: `user_id` (Assignee), `stage_interview` (Done, Approved, Pre Offer, Waitting Accept, DL Review, BOD Review, RM Review, Rejected), `offer_status` (Offer, Pending Offer).
- Cần chạy thăm dò: mở hồ sơ 32721 (đã có cuộc họp ở quá khứ), ghi lại khối Interview result để biết nút và popup.
- **Kết quả thăm dò (04/11/2026, tài khoản `truong.dangvan`, hồ sơ 32721, đã có cuộc họp id 200 ở quá khứ):** khối `answer_ids` là **bảng trống** với cột Code, Interviewer, State, Department, RR, Probationary rate, Status, **không có nút thêm** (chỉ có nút chuyển trang). Các nút trên form Application: Add a Meeting, Add a Resource Request, Edit Meeting, Cancel Interview, TA Feedback, Add a Test, **không có nút nào tên Interview Result**.
- API: `vti.interview.answer` của 32721 = **0 bản ghi** (đã thử TA, `truong.dangvan`, `hoai.nguyenthithu`), `has_vti_interview = False`. Mẫu đánh giá: 1 "VTI - KẾT QUẢ PHỎNG VẤN", 2 "VJP - INTERVIEW RESULT", 8 "VTI - TEST".
- Chưa biết kết quả phỏng vấn được tạo bằng cách nào (tự động khi qua giờ họp? bấm ở màn khác?). Tài khoản TA không đọc được `ir.cron`, nên không xem được lịch job.

## 9. Tạo Interview Result từ màn RR  [STG-API + STG-chạy 04/11/2026]
- [SRS, trích từ phiên khác do User dán ảnh] Người tạo là DL (RR thuộc bộ phận mình), Reviewer/Interviewer (RR họ là reviewer); REC User (TA) chỉ xem, không tạo. Màn RR có nút **Create Result**, tạo xong hiện nút **Interview Result** để sửa. Xem lại ở menu Interviews > Interview Result (có nút View CV). Chưa tự đối chiếu với SRS gốc.
- [STG-chạy] Màn RR (`/web#id=<rr_id>&model=vti.resource.request&view_type=form`, action 756, menu 565) có danh sách ứng viên `new_rr_applicants_ids` (model `vti.resource.request.applicant`, khi `create_result = True`; ngược lại là `rr_applicants_ids`). Cột: HR Applicant, Project, Interview Date, Stage, Offer Process, Skill, Level, Expect OB Date.
- [STG-chạy] **Nút trên mỗi dòng ứng viên:** `view_cv` (biểu tượng), **`view_interview_result` "Create Result"**, `status_application` "Update status".
- [STG-chạy] RR01413 (id 1799): dòng 21136 = Nguyễn Văn Kiểm (CV30118), Stage "Processing_Waiting for result", Interview Date trống. Số liệu bấm được: Interviewing 0, Waiting for result 1, Interviewed 0.
- [STG-API] Dòng ứng viên có field `interview_answer_ids`, `stage_interview_display`, `interview_date`, `submit_interview_date`, `processing_state`. Tài khoản thấy dòng này: `truong.dangvan` (DL/Interviewer của RR01413).
- [STG-chạy] Bấm **Create Result** mở **trang form đầy đủ** (không phải popup, không cần bấm ×) `New Interview Result` (`vti.interview.answer`, URL có `active_id=<id dòng ứng viên>`), breadcrumb "Resource Requests > RR01413 > New". Nút: Save, Discard, **Pass** (`create_next_pass_result`), **Fail** (`create_next_fail_result`), thanh trạng thái Draft, `view_cv`. Lúc ghi probe (8 giây sau khi bấm) ô Tên ứng viên và Mã YCTD vẫn trống.
- [STG-API] Ô: `state` (Draft, In Progress, Failed, Pass, bắt buộc), `applicant_id` (bắt buộc, domain: không draft, không trùng CV), `resource_request_id` (domain: RR không ở draft/reject/pending), `number_of_rounds` (One Round / Multiple Rounds), `interview_type` nhãn "Interview Format" (bắt buộc trên màn, many2one `vti.multi.interview.type`), `vti_survey_id` nhãn "Template phỏng vấn" (bắt buộc), `multi_interview_answer` (html). Applicant, RR và Template chỉ sửa được khi `state = draft`.
- [STG-API] Nút trên form kết quả: Submit (`show_popup_offer`, chỉ khi In Progress), Send to DL / Send to SM (xác nhận "Are you sure ?"), Set to In Process, Clone Interview, Pass (`pass_cv`), Fail (`fail_cv`), Confirm New Offer, Update Salary, Pending Offer.
