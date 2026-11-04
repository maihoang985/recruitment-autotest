# Resource Request (RR): form, dropdown, data mẫu

> Dữ liệu đọc qua Odoo XML-RPC ngày 04/11/2026 trên STG (DB `vms_rec_stg`, Odoo 12), bằng tài khoản `truong.dangvan`.
> Đọc kèm `E:\Downloads\task-73087-masking-test-tom-tat.md` (bối cảnh task #73087 Masking CV).
> Toàn bộ trường và giá trị dropdown: `output/inspect_vti.resource.request.json` (chạy lại bằng `scripts/inspect_model.py`).

## 1. Có cần tạo RR không?
Test Masking chỉ cần **một RR đang Open và còn quota** để Add a line Review CV → Submit CV. **Nên dùng RR có sẵn**, không tự động tạo RR (tạo cần thêm bước BOD duyệt).

| Code | id | Phòng | Job Position | Level | Quota còn | Deadline |
|---|---|---|---|---|---|---|
| **RR01378** | 1748 | VTI.VMS | Business Development | Fresher | 4 | 2026-12-22 |
| RR01377 | 1747 | VTI.VMS | Lecturers | Fresher | 1 | 2026-12-22 |

Người trên RR01378:
- DL / SM / Reviewer: `truong.dangvan`
- Interviewer: `truong.dangvan`, `tung.bachduy1`
- Approver (BOD): `thao.nguyenminh` (khác `BOD_USER=hien.daothithu` trong `.env`)
- Company Follow: VTI Corporation

Mỗi CV Submit sẽ làm giảm quota. Hết quota thì lấy RR khác:
`search_read vti.resource.request [state=open, quantity>0, create_user_id=truong.dangvan]` (hiện có 7 RR).

Thống kê state trên STG: open 152, draft 53, submit 41, cancel 32, done 14, pending 6, reject 1.

## 2. Form RR (model `vti.resource.request`): chỉ khi thật sự cần tạo RR
URL list: `/web?#action=756&model=vti.resource.request&view_type=list&menu_id=565`
Luồng: DL tạo (Draft) → **Submit** (To approve) → BOD Approve → **Open**.

Cột "Bắt buộc": **Có** = luôn bắt buộc; **Lúc tạo** = bắt buộc khi tạo mới (`write_date=false` hoặc `id=false`).
Áp dụng cho công ty VTI (company_code ≠ vjp). Giá trị mẫu lấy từ RR01378.

| Nhãn trên UI | `name` | Kiểu | Bắt buộc | Giá trị mẫu | Một số lựa chọn (tổng số) |
|---|---|---|---|---|---|
| Department Leader | `create_user_id` | many2one res.users | Có | tự điền user đăng nhập | (2824 user) |
| Department | `department_id` | many2one | Có | tự điền VTI.VMS | (228) |
| Project | `project` | char | Lúc tạo | `Auto test masking` | |
| Job Location | `job_location_id` | many2one | | Hồ Chí Minh | Hồ Chí Minh, Tokyo, Osaka, Korea… (14) |
| SM | `sm_ids` | many2many tags | | tự điền | |
| Reviewer | `reviewer_ids` | many2many tags | | tự điền | |
| Interviewer | `interviewer_ids` | many2many tags | | tự điền | |
| Approver | `bod_approve` | many2many res.users | Có | NGUYEN MINH THAO (VTI.D9) | |
| Expect Qty | `expect_quantity` | integer | Lúc tạo | `1` | |
| Deadline Date | `deadline` | date | Lúc tạo | ngày tương lai | |
| Job Position | `job_position` | many2one | Có | IT | IT, Intern, CTV, HR, Designer, Recruitment… (456) |
| Level | `level` | many2one | Có | Fresher | Intern, Fresher, Junior, Senior, Middle, Software Architecture… (8) |
| Main skill | `skill_id` | many2one | Lúc tạo | General Manager | 第二新卒, 新卒, General Manager, Robotics… (361) |
| Sub skill | `skill_ids` | many2many | | | cùng danh sách skill |
| Priority | `priority` | selection | Có | Very Urgent (`"3"`) | `"0"` Not urgent, `"1"` Normal, `"2"` Urgent, `"3"` Very Urgent |
| Salary Upto | `salary` | integer | Lúc tạo | `25000000` | |
| Currency | `currency_id` | many2one | khi salary ≠ 0 | VND | |
| Job Type | `job_type_id` | many2one | Lúc tạo | Full time | Part time, Full time, Freelance… (10) |
| Interview type | `interview_type_id` | many2one | Lúc tạo | Face to face | Face to face, Skype, Online, Offline |
| Experience | `experience` | selection | Lúc tạo | Fresher/Intern (`fresher_intern`) | 1 Year, 2 Year, 3 Year, 4 Year, Above 5 Years (`avobe_5_years`, đúng chính tả hệ thống) |
| Gender | `gender` | selection | | | Nam, Nữ |
| Languages | `lang` | many2one | Lúc tạo | Vietnamese / Tiếng Việt | English, Japanese… (6) |
| CV Accepted From | `candidate_country_policy` | selection | Có | All countries (`all`) | Vietnamese only, Specific countries (chọn cái này thì bắt buộc `accepted_country_ids`) |
| Expect Onboard Date | `estimated_onboard` | date | Lúc tạo | ngày tương lai | |
| Company Follow | `company_follow_ids` | many2many | Lúc tạo | VTI Corporation | (16) |
| Project Description | `project_description` | text | Lúc tạo | `Auto test` | |

Chỉ hiện với VJP (bỏ qua khi test VTI): `job_location_ids`, `business_domain_id`, `keyword_tag_ids`, `highlight*`, `description_*_jp`, `experience_required_*_jp`.

## 3. Mẫu locator Odoo 12 (đoán từ `name`, cần xác nhận bằng Pick locator)
Odoo hay dùng id động (`#o_field_input_123`), nên **không dùng id**. Thay vào đó, bám theo thuộc tính `name`:

| Kiểu trường | Locator gợi ý |
|---|---|
| char / integer | `input[name="project"]` |
| text | `textarea[name="project_description"]` |
| selection | `select[name="experience"]` → `select_option(label="Fresher/Intern")` |
| many2one | `div[name="job_position"] input` → gõ chữ → chọn trong `ul.ui-autocomplete li a` |
| many2many tags | `div[name="reviewer_ids"] input` → gõ → chọn trong `ul.ui-autocomplete` |
| date | `div[name="deadline"] input` |
| nút trên header | `button[name="<tên method>"]`, hoặc `get_by_role("button", name="Submit")` |

Riêng `priority` trên ảnh form không hiện ô select. Có thể đây là widget khác, nên cần Pick locator.

## 4. Cách phối hợp với người dùng
Người dùng **không gửi code codegen**. Mỗi lần làm **một bước nhỏ** và gửi:
1. Kịch bản bằng lời (làm gì, theo thứ tự).
2. Ảnh chụp màn hình.
3. Locator lấy bằng **Pick locator** trong Playwright Inspector, ví dụ: `Nút Create: get_by_role("button", name="Create")`.

Claude viết code vào project `D:\Auto-test\recruitment`. Locator nào không ổn định thì đổi sang dạng `[name="..."]` như bảng ở mục 3.
Dữ liệu dropdown thì tra bảng ở mục 2 hoặc file JSON, không cần người dùng chụp từng dropdown.

## 5. Công cụ trong project
| Việc | Lệnh |
|---|---|
| Mở codegen đã đăng nhập sẵn | `powershell -ExecutionPolicy Bypass -File scripts\codegen.ps1 <ten> -User truong.dangvan -Url "<url>"` |
| Lưu phiên đăng nhập (`.auth/<user>.json`) | `.\.venv\Scripts\python.exe scripts\save_auth.py <user>` |
| Đọc form + dropdown + record mẫu của một model | `.\.venv\Scripts\python.exe -X utf8 scripts\inspect_model.py <model> <user>` |
| Chạy test | `.\.venv\Scripts\python.exe -m pytest` |

Trạng thái ngày 04/11/2026: thư viện và Chromium đã cài, `.env` đã điền, đăng nhập bằng `truong.dangvan` qua UI và API đều chạy được.
Lưu ý: chưa cài `chromium_headless_shell`, nên khi chạy ngầm dùng `launch(headless=True, channel="chromium")`.
