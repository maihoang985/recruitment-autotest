# Task #73087: Test Masking che contact ứng viên trong CV (VMS_2026_S2)

> Tổng hợp các phiên làm việc với Claude, cập nhật 04/11/2026.

## 0. Quy ước ghi nguồn (đọc trước)
Mỗi thông tin đều có nhãn nguồn. Phiên sau dựa vào nhãn để biết thông tin nào chắc chắn, thông tin nào chỉ là suy đoán.

| Nhãn | Nguồn | Độ tin cậy |
|---|---|---|
| **[RM-70538]** | Redmine task cha https://redmine2.vti.com.vn/issues/70538, phần Description (đọc lại 04/11) | Yêu cầu chính thức |
| **[RM-73087]** | Redmine task test https://redmine2.vti.com.vn/issues/73087 (đọc ở phiên trước) | Thông tin task, có thể đã thay đổi |
| **[SRS ô X]** | File `E:\Downloads\VMS_Module_TA_SRS_v1.1.xlsx`, sheet " Applications" (trừ khi ghi sheet khác), ô X | Yêu cầu chính thức |
| **[GSheet]** | Bản Google Sheet SRS online (phiên trước đọc). Không có trong file tải về | Chính thức, chưa đối chiếu lại |
| **[STG-API]** | Claude đọc dữ liệu thật trên STG qua XML-RPC (chỉ đọc), ghi kèm ngày | Thực tế hệ thống, chưa chắc đúng SRS |
| **[STG-chạy]** | Kết quả chạy script/test trên STG | Thực tế hệ thống |
| **[Claude]** | Claude suy luận hoặc đề xuất | **Chưa chứng thực**, cần hỏi hoặc kiểm tra |
| **[User]** | Người dùng cung cấp hoặc quyết định trong chat | Theo người dùng |

**Lưu ý:** Description của #70538 **trùng gần hết** với SRS mục 3.3.6, phần 1. Hiện trạng → 3.3 Business rule. Redmine **không có** mục 3.4 Giao diện, 3.5 Phân quyền, 3.6 Message list, 3.7 Email và ghi chú định dạng ô CV Attachment. Các mục đó chỉ có trong SRS.

## 1. Thông tin task  [RM-73087]
- **Link:** https://redmine2.vti.com.vn/issues/73087
- **Task cha:** #70538 [TA] Masking che contact ứng viên trong CV và lịch phỏng vấn. [RM-70538]: người tạo Hạnh Nguyễn Duy, start 12/10/2026, % Done 50%.
- **Assignee:** Mai Nguyễn Phạm Hoàng | **BA:** Anh Trần Thị Lan | **Category:** REC | **Priority:** Major
- **Start:** 29/10/2026, **Due:** 02/11/2026 (đang trễ hạn), **% Done:** 0% (lúc đọc ở phiên trước)
- **Các task anh em** [RM-70538]: #73085 BA (Closed), #73086 Dev (Closed, Linh Đinh Văn), #73088 Deploy (New)
- **Yêu cầu:** viết testcase theo SRS và test trên **STG**: luồng chính, trường hợp biên, user thường và user không có quyền.
- **SRS:** `VMS_Module_TA_SRS_v1.1`, mục **3.3.6** (bắt đầu ở [SRS ô B191]). Ghi chú "Mới trên STG, chưa lên Prod" và tên sheet "AP-01 Applications" là **[GSheet]**. Bản tải về tên sheet là " Applications".
  - Google Sheet: https://docs.google.com/spreadsheets/d/1PsXmNFIF8EapMZzq1LGTODRs0Gt9CdqnLp5CQR3eODY/edit?gid=1654601155 (link cũng có trong [RM-70538])
  - Bản tải về: `E:\Downloads\VMS_Module_TA_SRS_v1.1.xlsx`. Record of Change ô N20 ghi việc bổ sung Masking (#70538).

## 2. Tính năng cần test  [RM-70538] + [SRS ô B191–B223]
Khi TA upload CV gốc, hệ thống **tự tạo bản "CV Masked"** (PDF) đã che hết thông tin liên hệ. Mọi chỗ đưa CV ra ngoài nhóm TA đều dùng bản Masked.

### Trigger  [RM-70538 mục 3.1] [SRS ô B204–B205]
- Upload hoặc đổi CV Attachment của ứng viên VTI **từ mọi nguồn**: form Applications, Get CV Info, Website (API upload CV), copy từ hồ sơ cũ. Đây là **4 nguồn riêng biệt**. Ngoài tên ra, cả Redmine lẫn SRS không mô tả thêm gì về 3 nguồn sau (xem mục 11).
- TA bấm **Submit CV** ở dòng Review CV.

### Phạm vi  [RM-70538 mục 3.2] [SRS ô B208–B210]
- Chỉ áp dụng cho ứng viên có **Source thuộc công ty VTI**. VJP và công ty khác giữ nguyên như cũ.
- CV upload trước khi bật tính năng thì không tạo bản che. TA upload lại thì áp dụng.
- "Lịch phỏng vấn" là các màn View CV/phỏng vấn trên **Odoo 12**. Odoo 17 không thuộc phạm vi.

### Business rules  [RM-70538 mục 3.3] [SRS ô B213–B223]
| BR | Nội dung |
|---|---|
| BR1 | Phải che: SĐT (VN và quốc tế), email, địa chỉ, link GitHub/GitLab/Facebook/LinkedIn/Twitter-X/Instagram/TikTok/Zalo/Skype/Telegram (kể cả link ẩn gắn trên chữ) |
| BR2 | Nhận diện địa chỉ qua nhãn (Address, Địa chỉ, Nơi ở, Thường trú, Tạm trú…) hoặc từ khóa (Phường, Quận, Huyện, Thị xã, Ngõ, Ngách, Hẻm, Ward, District…) |
| BR3 | Không che: họ tên, ngày sinh, ảnh chân dung, học vấn, kinh nghiệm, website/portfolio cá nhân |
| BR4 | Che tự động, bắt buộc với "mọi định dạng CV hệ thống nhận": PDF có chữ, PDF scan, PNG, JPG |
| BR5 | File che tên `<tên gốc>_masked.pdf`. Chữ đã che **bị xóa hẳn**, copy không lấy ra được. Ảnh/scan thì tô đen. CV gốc nhiều file thì mỗi file một bản che |
| BR6 | Bản che chạy nền, mất khoảng 1–2 phút sau khi lưu. Tạo xong, chatter ghi "Đã tạo CV che: N vùng được che" |
| BR7 | Dòng Review CV, mail "Applicant: Submit CV", màn View CV đều dùng CV Masked |
| BR8 | Bấm Submit CV: phải có CV Masked. Chưa có thì hệ thống tạo ngay, tạo lỗi thì chặn gửi (E_001, E_002) |
| BR9 | Chỉ REC User, Rec Manager và người upload xem/tải được CV gốc. Người khác không thấy ô CV Attachment, mở link thì bị chặn (E_007), chatter không hiện CV gốc |
| BR11 | Bật/tắt bằng cấu hình hệ thống (cần PyMuPDF, Tesseract OCR Việt/Anh). Tắt thì hệ thống chạy như cũ |
| BR12 | Giới hạn: địa chỉ không có nhãn, ảnh chèn trong PDF có chữ, font TCVN3/VNI có thể bị sót. TA tự kiểm tra rồi thay tay. **Không tính là bug** ([Claude] suy ra từ chữ "Giới hạn") |

### Ô trên form  [SRS ô O226–S231, mục 3.4] (chỉ có trong SRS)
- **CV Attachment** [SRS ô S46]: "Định dạng word, pdf, ảnh <= 800KB". [SRS ô S227]: ứng viên VTI thì chỉ REC User, Rec Manager và người upload thấy. Lưu hoặc đổi file thì tạo lại CV Masked.
- **CV Masked** [SRS ô S228]: hiện khi ứng viên VTI có CV upload sau khi bật tính năng. Ai xem được hồ sơ cũng xem/tải/in được. Chỉ REC User, Rec Manager được thay file.
- **Review CV › CV Attachment** lấy CV Masked [S229]. **Submit CV** kiểm tra BR8 [S230]. **View CV** hiển thị CV Masked [S231].

### Phân quyền  [SRS ô B236–L249, mục 3.5] (chỉ có trong SRS)
Ký hiệu SRS: y = toàn bộ, x = dữ liệu mình được xem, --- = không có quyền.

| Role | Xem/tải CV gốc | Xem/tải CV Masked | Thay CV Masked | Tạo lại CV che | Ghi chú SRS |
|---|---|---|---|---|---|
| Admin System | --- | x | --- | --- | Muốn xem CV gốc phải thuộc thêm REC User/Rec Manager |
| BOD | --- | x | --- | --- | |
| Rec Manager | y | y | y | y | |
| REC User | y | y | y | y | |
| Partner (HRI) | x | x | --- | --- | CV gốc: chỉ file mình upload |
| Partner Manager (HRI Manager) | x | x | --- | --- | CV gốc: chỉ file mình upload |
| DL, Reviewer, Interviewer | --- | x | --- | --- | |
| VTI Website User | --- | --- | --- | --- | Upload CV qua API, hệ thống tự tạo CV Masked |
| Nhân viên giới thiệu (Referrals) | x | --- | --- | --- | CV gốc: chỉ file mình upload |

### Message list  [SRS ô B251–L257, mục 3.6] (chỉ có trong SRS)
| ID | Tiếng Việt (cột L) | English (cột C) |
|---|---|---|
| E_002 | Không gửi được CV của ứng viên %s: CV che chưa sẵn sàng (%s). | Cannot send CV of applicant %s: the masked CV is not ready (%s). |
| E_003 | Máy chủ chưa cài công cụ che CV. Vui lòng liên hệ quản trị hệ thống. | The server is missing the CV masking libraries… |
| E_004 | Định dạng file CV này không hỗ trợ che. Chỉ hỗ trợ PDF, PNG, JPG. | This CV file type is not supported for masking. Only PDF, PNG and JPG are supported. |
| E_005 | File CV bị lỗi hoặc không đọc được nên không che được. | The CV file is unreadable or corrupted, so it cannot be masked. |
| E_007 | Chỉ TA được mở CV gốc của ứng viên này. Vui lòng dùng CV đã che. | Only Talent Acquisition can open the original CV… |

SRS không có E_001 và E_006 (xem mục 6).

### Email  [SRS ô B260, mục 3.7] (chỉ có trong SRS)
Mail "Applicant: Submit CV" (đã có sẵn): với ứng viên VTI, file CV nhúng trong mail là CV Masked. Không thêm mail mới, To/CC giữ nguyên.

### Bối cảnh các màn  [SRS ô B186–B189]
- Draft Applications: "Web đổ về → Màn Draft Applications quyền RM Confirm → assign cho Rec User follow".
- Referrals >> All Referral: nhân viên trong công ty tạo Applications ở màn My Referral, sau đó RM Confirm ở màn All Referral.

## 3. Giải thích các điểm đã hỏi  [Claude], tổng hợp từ BR7–BR9 và mục 3.4
- **CV Masked dùng ở đâu:** dòng Review CV, mail Submit CV, popup View CV. Đây là những chỗ người ngoài TA nhìn thấy CV.
- **CV gốc dùng ở đâu:** ô CV Attachment và chatter (chỉ nhóm TA thấy). Ngoài ra CV gốc là đầu vào để hệ thống tạo bản che, và TA dùng để đối chiếu khi cần thay bản Masked bằng tay.
- **Submit CV (BR8):** hệ thống phải có bản Masked rồi mới cho gửi mail. Chưa có thì tạo ngay, lỗi thì chặn gửi.

## 4. Phạm vi test  [Claude] (đề xuất, dựa trên mục 2)
1. Che đúng và đủ, theo từng định dạng và từng nguồn upload.
2. Chỗ dùng bản Masked: Review CV, mail, View CV.
3. Submit CV: tạo bản che ngay khi chưa có, chặn gửi khi lỗi.
4. Phân quyền theo từng role.
5. Phạm vi áp dụng: VTI so với VJP, CV cũ, bật/tắt cấu hình.
6. Các thông báo lỗi E_002, E_003, E_004, E_005, E_007.
7. Giới hạn BR12: chỉ ghi nhận hành vi, không tính là bug.

> **Mẹo test tay** [Claude], suy ra từ BR5: mở file `_masked.pdf`, bấm Ctrl+A rồi copy và dán ra Notepad. Nếu vẫn còn SĐT hay email thì là bug: chữ chỉ bị phủ đen chứ chưa bị xóa.

## 5. Chuẩn bị trước khi test  [Claude] (đề xuất)
| Phần test | Cần chuẩn bị |
|---|---|
| Che đúng/đủ, định dạng, chatter, bật/tắt, VTI hay VJP | Chỉ cần tạo Application (Source VTI) và upload CV. STG phải bật masking (đã bật, xem mục 10) |
| Phân quyền trên form | Tài khoản test cho từng role |
| Review CV / Submit CV / mail | **RR đang Open và còn quota**. Đã có **RR01413** (xem `docs/session-tao-rr-tom-tat.md`). Sau đó Add a line Review CV → chọn RR → Submit CV |
| View CV lúc phỏng vấn | DL Accept CV → TA Add a Meeting → đăng nhập bằng Interviewer/DL để mở View CV |

### Data cần chuẩn bị  [Claude]
- **Bộ CV mẫu**, mỗi file dưới 800KB ([SRS ô S46]):
  - định dạng: PDF có chữ, PDF scan, PNG, JPG, nhiều file;
  - trường hợp đặc biệt: link ẩn gắn trên chữ, số quốc tế, địa chỉ có nhãn và không nhãn, website/portfolio (không được che), file Word, file hỏng, font TCVN3/VNI, ảnh chèn trong PDF.
- Application có Source VTI và có Source VJP. Thêm một hồ sơ có CV upload từ trước khi bật tính năng.
- Tài khoản test theo bảng phân quyền.

### Luồng chính tạo mới hoàn toàn  [Claude] tổng hợp từ các sheet SRS Resource Request, Applications, Phân quyền
Phần RR đã kiểm chứng trên STG ([STG-chạy], xem `docs/session-tao-rr-tom-tat.md`). Phần Application → Meeting chưa kiểm chứng.

**Ai làm gì:**
| Tài khoản | Việc trong luồng |
|---|---|
| Admin hoặc Dev | Bật cấu hình masking trên STG (BR11). Đã bật [STG-API] |
| DL | Tạo RR, Submit RR, Accept CV |
| BOD | Approve RR |
| REC User (TA) | Tạo Application, upload CV, Submit CV, Add a Meeting |
| Reviewer, Interviewer | Mở View CV để kiểm tra bản Masked |

**Các bước:**
1. **DL**: tạo RR → Save → Submit (có hộp xác nhận) → **BOD** Approve (có hộp xác nhận) → **Open**. Đã làm xong: **RR01413** [STG-chạy].
2. **REC User**: Recruitment → Applications → Create → điền form, upload **CV Attachment**, rồi **Save**. Đã tự động hóa [STG-chạy], xem mục 10.
   - Kiểm tra BR4–BR6: ô CV Masked có file `_masked.pdf`, chatter có dòng báo tạo bản che.
3. **REC User**: Review CV → **Add a line** → chọn RR → **Submit CV**. Hộp xác nhận "Submit this CV and send an email to reviewer." [STG-API]
   - Kiểm tra BR7, BR8: dòng Review CV và file đính kèm mail đều là bản Masked. Submit khi bản che chưa xong thì hệ thống phải tạo ngay hoặc báo E_002.
4. **DL hoặc Reviewer**: View CV → **Accept**.
   - Kiểm tra BR7, BR9: thấy bản Masked, không thấy ô CV Attachment, mở link CV gốc bị chặn (E_007).
5. **REC User**: Application → **Add a Meeting**.
6. **Interviewer**: mở **View CV**. Phải là bản Masked, không xem được CV gốc.

> **Đính chính:** Interviewer thấy CV là nhờ **Accept**, không phải nhờ Add a Meeting. Sheet Phân quyền, bảng Review CV ghi Interviewer "view bản ghi ở trạng thái Accept vào RR mà họ là interviewer" [SRS sheet Phân quyền]. Add a Meeting chỉ để đúng ngữ cảnh "lịch phỏng vấn". Chi tiết các công đoạn kiểm tra xem mục 13.

## 6. Điểm cần hỏi BA (chị Lan Anh)
- **E_001** được nhắc trong BR8 [RM-70538] [SRS ô B220] nhưng Message list [SRS ô B253–B257] không có. Danh sách cũng thiếu E_006.
- **Không có BR10**: cả Redmine lẫn SRS đều nhảy từ BR9 sang BR11.
- **File Word:** ô CV Attachment nhận Word [SRS ô S46], nhưng E_004 [SRS ô C255] chỉ hỗ trợ PDF/PNG/JPG, còn BR4 ghi "mọi định dạng hệ thống nhận". Upload Word thì xử lý thế nào, Submit CV có bị chặn không?
- **Giới hạn 800KB** [SRS ô S46] gây khó khi test PDF scan chất lượng cao, nhiều trang. Lưu ý [STG-API]: hồ sơ 32625 có CV PNG 1MB vẫn upload được.
- **Chatter BR6:** SRS ghi tiếng Việt "Đã tạo CV che: N vùng được che", STG ghi tiếng Anh "Masked CV created: N area(s) masked." [STG-API]. Có cần song ngữ không?
- **Thời gian che BR6 (1–2 phút):** trên STG bản che Pending > 5 phút, hồ sơ 32719 mất khoảng 2 giờ 20 phút [STG-API]. Hỏi Dev Linh Đinh Văn về job nền.
- **Get CV Info**: nút này nằm ở đâu, thao tác thế nào? Cả Redmine lẫn SRS chỉ nhắc tên.
  - [SRS sheet Configuration ô B482, B495]: có luồng "Upload CV (đọc CV tự điền Current Company)" / "Đọc CV", nhưng không gọi tên "Get CV Info".
  - [STG-API 04/11]: có wizard `wizard.get.cv.info` ("Wizard Get CV Info") với 3 ô Applicant, Source, Attachments. Wizard không có nút trong form, nên được mở bằng nút JS. Menu All Applications có context `button_upload_cv: 'upload_cv'`. Form Application có nút **Upload CV** (`open_cv_upload`), chỉ hiện sau khi Save.
  - [Claude]: đoán Get CV Info = nút Upload CV (ở danh sách hoặc trên form). **Chưa chứng thực.**
- **Nguồn Website**: test bằng cách nào? Có website STG để nộp thử không, hay phải gọi API?
  - [SRS ô L248]: "Tài khoản website upload CV qua API; hệ thống tự tạo CV Masked". [SRS ô B187]: hồ sơ web đổ về Draft Applications. [SRS sheet Phân quyền ô C24]: VTI Website User chỉ tạo và xem Referrals của mình.
  - [STG-API 04/11]: 3 hồ sơ Referral Source **Website_ERP** do **Rec Website User** tạo đã che xong (id 32620, 32012, 31996, Referred = `chau.phamminh`).
- **"Copy từ hồ sơ cũ"** là thao tác Duplicate trên Application hay chức năng khác? Cả Redmine lẫn SRS chỉ nhắc tên. Các sheet Duplicate CV trong SRS chỉ nói luật kiểm tra trùng.
  - [STG-API 04/11]: Application có ô **Previous Application** (`old_applicant_id`, chỉ đọc), cùng Duplicate CV và Waring. 64 hồ sơ có Previous Application, mới nhất 08/06/2026 (trước khi có masking).
  - [Claude]: có 2 giả thiết, (a) nút Duplicate, (b) luồng nối hồ sơ trùng (Previous Application). **Chưa chứng thực.**
- Upload CV ở màn **My Referral** có thuộc phạm vi masking không? Trigger không liệt kê. Sheet Referrals [SRS sheet Referrals ô S46] có ô CV Attachment nhưng không nhắc masking. Chỉ bảng 3.5 có dòng "Nhân viên giới thiệu".
  - [STG-API 04/11]: menu Recruitment → Referrals → My Referrals (action 2069) và All Referrals (2070), form 4464/4468. Form có CV Attachment, **CV Masked không có điều kiện ẩn**, nút **Recreate masked CV**, luồng Send to RM → Confirm. Có 291 hồ sơ Referral, 3 hồ sơ đã che (đều từ Website). Bảng 3.5 ghi nhân viên giới thiệu **không** xem được CV Masked. Mình mới đọc bằng tài khoản TA, nên cần đăng nhập bằng nhân viên thường để kiểm tra.
- **Dòng Review CV lúc còn Draft hiện CV gốc** [STG-chạy]. Bảng 3.4 ghi chung "Review CV › CV Attachment: lấy CV Masked", không phân biệt trạng thái. Lúc Draft chỉ TA thấy dòng, nên có thể không vi phạm. Cần BA xác nhận.
- **View CV của BR7 là màn nào trên STG?** Form Application không có nút View CV [STG-API]. SRS ghi nút View CV ở **list view** Applications và Interview Result [SRS 3.3.2; sheet Interviews 3.3.2]. Trên STG, View CV thực tế là mục **"CV (s)"** nhúng file trên form CV Review [STG-chạy]. Hỏi BA: cách hiểu này đúng không, và nút View CV ở list view (nếu có) có thuộc phạm vi BR7 không?
- **View CV ở màn Interview Result có thuộc phạm vi BR7 không?** Nếu có thì mới cần tạo Interview Result (để Draft là đủ, không cần Pass/Fail). Nếu không thì bỏ hẳn nhánh này. [Claude]
- **Mail Submit CV xem ở đâu trên STG?** STG có gửi mail ra ngoài không, hay chuyển hết về một hộp test? Hỏi Dev.

## 7. Hướng automation  [Claude] + [User] (đã thống nhất)
- **Đợt này:** test tay để đóng task (đã trễ hạn). Song song đó dựng auto cho phần lặp lại. [User]
- **Cách làm:** script tự sinh CV mẫu, tạo Application **qua giao diện**, chờ bản che, tải `_masked.pdf` qua API, dò chữ còn sót bằng PyMuPDF, xuất báo cáo Pass/Fail. Đã làm cho PDF có chữ (mục 10).
- **Không tạo data qua API** [Claude]: API bỏ qua trường bắt buộc khai báo trên view, onchange và kiểm tra bằng JS, nên record có thể khác record tạo qua giao diện. Trigger che cũng có thể chỉ chạy khi thao tác trên form. API chỉ dùng để **đọc và kiểm tra**.
- **Token** [Claude]: dò giao diện qua trình duyệt tốn nhiều token nhất. Đọc qua API và chạy script trên máy thì rẻ.
- Kế hoạch cũ "chạy codegen rồi gửi code" đã **bỏ**, thay bằng cách phối hợp ở mục 9. [User]

## 8. Ghi chú môi trường
- Claude in Chrome: profile công ty đã đăng nhập Redmine. Có 2 Chrome kết nối, người dùng chọn browser tên **"work area"** (04/11). [User]
- **URL STG:** https://vms-ta.stg.vti.com.vn/ (Odoo 12, đăng nhập tại `/web/login`, DB `vms_rec_stg`). [STG-API]
- Máy: Python 3.14.8, Node v24.21.0, Windows.
- **Session cookie:** người dùng từng gửi session của `hoai.nguyenthithu` ở phiên tạo RR. Session đó **không được lưu** ở đâu. Không cần dùng lại, vì tài khoản này đăng nhập được bằng mật khẩu chung trong `.env` (`BOD_USER`). [User] + [STG-chạy]

## 9. Project automation `D:\Auto-test\recruitment` (Python + Playwright + pytest)
Project mới, tách khỏi project cũ `D:\Auto-test\vms-ta-auto` (Selenium Java). Locator đăng nhập lấy theo project cũ: `#login`, `#password`, `.oe_login_buttons button[type='submit']`.

### Cấu trúc
```
recruitment/
├─ core/config.py        # đọc .env (BASE_URL, DEFAULT_PASSWORD, TA_USER, DL_USER, BOD_USER, HEADLESS, TIMEOUT_SECONDS)
├─ core/login.py         # login(page, username)
├─ core/odoo_api.py      # gọi XML-RPC (chỉ đọc/kiểm tra)
├─ core/probe.py         # dump_page(): ghi màn hình ra file text khi lỗi
├─ core/cv_maker.py      # sinh CV PDF mẫu + kiểm tra bản che
├─ core/mask_check.py    # chờ bản che, tải về, kiểm tra BR1–BR3, BR5, BR6
├─ pages/                # resource_request_page.py, application_page.py
├─ tests/                # test_create_rr, test_approve_rr, test_application_masking, conftest
├─ scripts/inspect_model.py  # đọc ô/nút/popup của form qua API
├─ scripts/check_mask.py     # kiểm tra lại bản che của 1 Application
├─ data/rr/, data/application/  # data mẫu (sửa ở đây, không sửa code)
├─ output/               # kết quả, file tải về (không commit)
```
- Mật khẩu chỉ nằm trong `.env`, không có trong code.
- Trạng thái [STG-chạy]: thư viện đã cài, `.env` đã có, đăng nhập, tạo RR, Approve và tạo Application đều chạy được.

### Cách phối hợp đã thống nhất  [User] 04/11/2026
Người dùng **không phải tự điền, không lấy locator, không chụp màn hình**.
1. Claude đọc form qua API: `scripts/inspect_model.py <model> <user> [form_view_id]`. Kết quả gồm ô, dropdown, các nút (hiện ở trạng thái nào), hộp xác nhận, popup wizard, nút trong bảng con. Claude viết sẵn data và script.
2. Người dùng chạy lệnh test (hoặc Claude tự chạy ở chế độ ẩn trình duyệt).
3. Gặp chỗ lạ hoặc lỗi, test tự ghi `output/probe_fail_<test>.txt` cùng ảnh .png.
4. Claude đọc file .txt rồi sửa script. Lặp lại đến khi qua hết luồng.

API **không** biết trước: lỗi do code Python kiểm tra lúc bấm nút và popup do method Python trả về. Những chỗ này lộ ra khi chạy.

### Thông tin form trên STG  [STG-API 04/11]
- Applications: model `hr.applicant`, form view **4899** (action 739, menu All Applications 569).
- Nút **Recreate masked CV** (`action_cv_mask_regenerate`), hộp xác nhận "The masked CV will be recreated from the original CV and will replace the current file. Continue?".
- Review CV là bảng con `applicant_line_ids` (`hr.applicant.lines`). Nút **Submit CV** (`submit_cv`), hộp xác nhận "Submit this CV and send an email to reviewer.".
- Các ô Masking: `cv_attachment_ids`, `cv_masked_attachment_ids`, `cv_mask_state` (Pending/Done/Failed), `cv_mask_error`, `cv_original_visible`, `cv_mask_can_replace`.
- Tác vụ nền: server action "Recruitment: Generate masked CVs" (id 5254), "Retry masked CV" (5255). TA và `hoai.nguyenthithu` đều **không** có quyền đọc ir.cron.

### Lộ trình từng bước
1. ✅ Đăng nhập.
2. ✅ Tạo RR, Approve → RR01413 Open.
3. ✅ Tạo Application, upload CV PDF có chữ, Save (id 32721).
4. ⏳ Chờ bản che, tải và kiểm tra (script có rồi, chờ job nền STG). [User]: người dùng tự chạy job sau.
5. ✅ Review CV → Submit CV → Accept (dòng 20260, bằng `truong.dangvan`). [STG-chạy]
6. 🟡 View CV: BR7 đạt ở form CV Review. BR9 chưa kiểm tra (cần tài khoản thuần). Xem mục 13.

## 10. Kết quả tự động tạo Application + kiểm tra CV Masked  [STG-chạy] 04/11/2026
- Test: `tests/test_application_masking.py`. TA (`chau.phamminh`) tạo Application Source **TA** (VTI) qua giao diện, upload CV PDF tự sinh, Save. Sau đó đợi bản che qua API và kiểm tra BR1–BR3, BR5, BR6. Kết quả ghi ở `output/mask_check_<id>.txt`.
- Kiểm tra lại, không tạo hồ sơ mới: `python scripts/check_mask.py [id]`.
- **Code hiện tại chỉ kiểm tra được PDF có chữ.** PDF scan, PNG, JPG, Word, file hỏng, nhiều file đều chưa làm.
- Popup phát hiện khi chạy: chọn Current Company → "Do you want to add this company to the Working History list?" → bấm **Cancel** (`KNOWN_POPUPS`).
- **Đã tạo trên STG:** Application **id 32721 (CV30118)**, "Nguyễn Văn Kiểm". CV của hồ sơ này sinh bằng font Arial, nên khi trích chữ dấu cách thành `\xa0`. Nếu bản che sót SĐT thì thử lại bằng CV mới trước khi báo bug.
- Bản che **Pending > 5 phút**, bấm Recreate cũng chỉ vào hàng chờ. [STG-API]: hồ sơ 32719 upload 04:29, chatter báo tạo bản che lúc 06:50 (khoảng 2 giờ 20 phút).
- [STG-API]: STG đã bật masking (16 hồ sơ Done). Source VTI = source của công ty VTI Corporation (TA id 6, TopCV 12, ITViec 9…). Source VJP = id 23, 115–124, 168 (công ty VJP).
- CV mẫu [STG-chạy]: dùng font Segoe UI, không dùng `-` và `( )` trong nội dung, vì font Windows trích sai các ký tự này. `make_text_cv` tự kiểm tra lại chữ sau khi tạo.

## 11. Upload mấy kiểu CV, ở mấy chỗ

### Kiểu CV
| # | Kiểu | Kỳ vọng | Nguồn | Code hiện tại |
|---|---|---|---|---|
| 1 | PDF có chữ | Che, chữ bị xóa hẳn | BR4, BR5 | ✅ |
| 2 | PDF scan | Che, tô đen (OCR) | BR4, BR5 | 🟡 có file mẫu CV02 |
| 3 | PNG | Che, tô đen | BR4, BR5 | 🟡 có file mẫu CV03 |
| 4 | JPG | Che, tô đen | BR4, BR5 | 🟡 có file mẫu CV04 |
| 5 | Word (.doc/.docx) | Ô nhận được [SRS ô S46], nhưng E_004 [SRS ô C255]. **Cần hỏi BA** | SRS | 🟡 có file mẫu CV05 |
| 6 | File hỏng (đổi đuôi, nội dung lỗi) | E_005 | [SRS ô C256] | 🟡 có file mẫu CV06A, CV06B |
| + | Một ứng viên nhiều file CV | Mỗi file một `_masked.pdf` | BR5 | 🟡 có file mẫu CV07 (PDF + PNG) |

### Bộ CV mẫu  [STG-chạy] 04/11/2026
- Sinh bằng `core/cv_maker.py` → `make_cv(kind, out_dir, candidate, stem)`. Xem trước cả bộ: `python scripts/make_cv_samples.py` → `data/cv_samples/` + `DANH_SACH.md`.
- **Mỗi CV có băng màu đầu trang** ghi "MẪU CVxx · định dạng" và dòng kỳ vọng, chân trang ghi lại. Tên file bắt đầu bằng mã mẫu. Người dùng yêu cầu để show cho khách nhận biết ngay. [User]
- Mã: CV01 PDF có chữ, CV02 PDF scan (ảnh xám 200dpi, không có lớp chữ), CV03 PNG, CV04 JPG, CV05 Word .docx (có link ẩn), CV06A file hỏng nội dung lỗi, CV06B file chữ đổi đuôi .pdf, CV07 nhiều file, CV08 PDF có chữ dùng cho Source VJP, CV09 upload lại lần 2. Tất cả < 800KB.
- PDF chỉ bị cắt ngắn thì MuPDF **tự sửa và vẫn mở được**, nên CV06A giữ đầu `%PDF` và thay thân file bằng byte rác.
- Khi chạy test, CV sinh mới mỗi lần (SĐT/email khác nhau, tránh báo trùng ứng viên).
- Kiểm tra bản che: người dùng **kiểm tra bằng mắt**. [User]. Lưu ý: PDF có chữ phải Ctrl+A, copy ra Notepad; link ẩn phải click thử.

[Claude]: mỗi định dạng nên chứa SĐT VN và quốc tế, email, link mạng xã hội, link ẩn, địa chỉ có nhãn và không nhãn, website/portfolio (không được che). Có thể dồn nhiều loại vào một CV.

### Chỗ upload: 4 nguồn riêng biệt  [RM-70538 mục 3.1] [SRS ô B204]
1. **Form Applications**: tạo mới và upload, rồi **đổi CV** trên hồ sơ đã có (phải tạo lại bản che, theo [SRS ô S227]).
2. **Get CV Info**: chưa rõ là gì (xem mục 6).
3. **Website (API upload CV)**: có thật trên STG, chưa rõ cách test (xem mục 6).
4. **Copy từ hồ sơ cũ**: chưa rõ là gì (xem mục 6).

> **Đính chính:** có phiên trước ghi "Get CV Info tính vào form Applications" và "Copy từ hồ sơ cũ = Duplicate". Cả 2 đều là **[Claude] suy đoán**, không có trong Redmine hay SRS. Redmine và SRS liệt kê 4 nguồn riêng.

Menu liên quan [SRS sheet Duplicate CV ô C9]: Draft Applications, All Applications, My Applications, My Referrals, All Referrals.

[Claude] **Với mỗi nguồn, thử cả** Source VTI (phải tạo bản che) và Source VJP (không được tạo bản che). Test đủ các kiểu file ở form Applications. Các nguồn còn lại, mỗi nguồn 1–2 file để xác nhận nguồn đó có kích hoạt tạo bản che.

### Phân biệt Source VTI và VJP
- [STG-API]: mỗi **Source** là một bản ghi `utm.source`, có trường **Company**. "Source thuộc VTI" nghĩa là Company là VTI Corporation.
- [STG-API]: trên form Applications, 4 ô Business Domain, Recruitment Type, Working Type, Main Market bị ẩn khi Source thuộc nhóm VJP (id 23, 115–124, 168). Đây là mẹo nhận biết trên giao diện.
- [STG-API 04/11] Source VJP: 23 VJP, 115 Facebook, 116 Linkedin, 117 Hellowork, 118 Fanpage, 119 説明会, 120 Mail, 121 Jobfair, 122 Webinar, 123 Others, 124 ERP, 167 VJP Recruitment: Mail Offer, 168 Web_Active_VJP.
- **Bẫy trùng tên** [STG-API]: "ERP" có ở cả VTI (10) và VJP (124); "Facebook", "Others" có ở VJP và ở source không công ty; "VTI - VJP" (24) thuộc **VTI**. Khi test VJP dùng Source **"VJP"** (id 23, tên duy nhất).

## 12. Checklist phân quyền  [Claude] dựa trên BR9 + [SRS mục 3.5]
Mỗi role đăng nhập vào cùng một Application của ứng viên VTI, rồi kiểm tra:

| Role | Ô CV Attachment / tải CV gốc | Mở link CV gốc trực tiếp | CV gốc trong chatter | Xem/tải CV Masked | Thay CV Masked, nút Recreate |
|---|---|---|---|---|---|
| REC User, Rec Manager | Có | Mở được | Có | Có | Có |
| Partner (HRI), HRI Manager | Chỉ file mình upload | File người khác: E_007 | Chỉ file mình upload | Có | Không |
| Admin System (không thuộc REC) | Không | E_007 | Không | Có | Không |
| BOD, DL, Reviewer, Interviewer | Không | E_007 | Không | Có | Không |
| Nhân viên giới thiệu (Referrals) | Chỉ file mình upload | E_007 với file khác | | **Không** | Không |
| VTI Website User | | | | Không | Không (chỉ upload qua API) |

[Claude] **Cách test "mở link CV gốc trực tiếp":** đăng nhập REC User, copy link tải CV gốc (dạng `/web/content/<id>`). Đăng nhập role khác, dán link vào trình duyệt. Kỳ vọng bị chặn, báo E_007.

**Tài khoản hiện có** (`.env`, [User]): REC User `chau.phamminh`, DL/Reviewer/Interviewer `truong.dangvan` (một người giữ cả 3 vai), `BOD_USER` = `hoai.nguyenthithu`. [STG-API]: tài khoản này thuộc **VTI.TA** (đã tạo Review CV), **không phải BOD thuần**. Approver của RR01413 là `hoai.nguyenthithu`.
### Tài khoản theo role  [STG-API] 04/11/2026
- Cách quét [User]: dùng `hoai.nguyenthithu` đọc `secure.module.user` (action 2358 "User Recruitment Permission", domain `view_rec_permission = 1`), group theo `group_id`. Kết quả đầy đủ: `output/accounts_by_group.txt`, role thuần: `output/accounts_pure_roles.txt`.
- Group có trên STG: BOD, Content Admin, DL, Interviewer, Module Admin, Partner, Partner Manager, REC User, Rec Manager, Reviewer, SM, VJP Viewer.
- Nhóm của tài khoản đang dùng: `chau.phamminh` = chỉ REC User. `truong.dangvan` = DL, Interviewer, Rec Manager, Reviewer, SM (**có Rec Manager nên thấy được CV gốc, không dùng để test "người ngoài TA"**). `hoai.nguyenthithu` = BOD, DL, Interviewer, Module Admin, REC User, Rec Manager.
- **Role thuần** (chỉ 1 group), đăng nhập được bằng mật khẩu chung trong `.env` (đã thử qua API):

| Role | Tài khoản đề xuất | Ghi chú |
|---|---|---|
| REC User | `chau.phamminh` | đang dùng |
| Rec Manager | `trung.phambao` | công ty VJP |
| BOD | `giang.trinh` | VTI, login cuối 2023 |
| DL | `dang.nguyenhuu` | VTI, người duy nhất chỉ là DL |
| Reviewer | `tinh.giangthi`, `tuan.maivan` | VTI |
| Interviewer | `minh.hoangkim`, `viet.hoangquoc` | VTI |
| Partner (HRI) | `thanh.hoang1`, `linh.dophuong` | công ty HRI |
| Partner Manager | `thuy.nghiemthanh`, `hong` | HRI, login API được. Nhóm khác của 2 người này chưa đọc được |
| VTI Website User | `recvtiwebsite` | group Partner, **không** đăng nhập được bằng mật khẩu chung |

- **Còn thiếu:** Admin System không thuộc REC, nhân viên thường (Referrals). Không có trong danh sách vì danh sách chỉ gồm user có quyền Recruitment.
- Lưu ý: DL/Interviewer chỉ thấy hồ sơ gắn với RR/Meeting của họ, nên hồ sơ test phải gắn đúng các tài khoản này.

## 13. Nghiệp vụ và các công đoạn kiểm tra thủ công  [Claude] tổng hợp từ SRS + kết quả STG, phiên 04/11/2026
Người dùng **tự kiểm tra bằng mắt** ở các công đoạn này [User]. Script hoặc TA chỉ lo tạo data.

### 13.1 Nghiệp vụ cần hiểu
- **RR:** bộ phận cần người, DL tạo phiếu tuyển dụng, BOD duyệt thì sang Open.
- **Application:** hồ sơ ứng viên do TA nhập. Lúc mới tạo chưa gắn vị trí nào (New).
- **Review CV:** TA "nộp" hồ sơ vào một RR, mỗi lần nộp là **một dòng** (`hr.applicant.lines`). Một hồ sơ nộp được nhiều RR. Trạng thái dòng: Draft → Submit CV (TA) → Submitted → Accept/Reject (DL/Reviewer).
- **Hai lối vào cùng một dòng:** bảng Review CV trên form Application (lối của TA), và menu **Recruitment > Applications > Review CV** (form "CV Review", lối của DL/Reviewer/Interviewer). Form CV Review dài vì phục vụ DL ra quyết định. TA chỉ cần chọn RR. [STG-chạy]
- **Ai thấy dòng Review CV** [SRS sheet Phân quyền, bảng Review CV]: REC User chỉ thấy hồ sơ mình tạo. DL/Reviewer chỉ thấy dòng nộp vào RR của bộ phận mình hoặc RR mình là reviewer. **Interviewer chỉ thấy dòng đã Accept**, thuộc RR mình là interviewer. Đây là phân quyền có sẵn, **không phải BR của task masking** (Redmine không có). Chỉ dùng làm điều kiện để chọn đúng tài khoản.
- **View CV xảy ra 2 lần:** ① DL/Reviewer xem CV **trước** khi Accept (review), ② Interviewer xem CV **sau** Accept (phỏng vấn).
- **Accept, Add a Meeting, tạo Interview Result không phải đối tượng test.** Đây chỉ là bước đi đường để tới màn View CV. Task #70538 tên "…trong CV **và lịch phỏng vấn**", nên View CV lúc phỏng vấn mới thuộc phạm vi (BR7).
- **BR7 và BR9 khác nhau:** BR7 hỏi *màn này hiện file nào* (không phụ thuộc người xem). BR9 hỏi *người này có được đụng vào CV gốc không* (phụ thuộc role). Tài khoản có Rec Manager (`truong.dangvan`, `hoai.nguyenthithu`) kiểm tra được BR7 nhưng **không** kiểm tra được BR9.
- **Interview Result** [SRS sheet Phân quyền, Interviews; Applications 3.3.1]: DL, Reviewer, Interviewer tạo được. REC User chỉ xem (trạng thái khác Draft). Tạo từ khối Interview result trên form Application ([Claude] đoán, chưa chứng thực trên STG). List view Interview Result có nút View CV. Nếu BA xác nhận thuộc BR7 thì chỉ cần tạo và Save ở Draft, **không cần Pass/Fail/Submit**, trừ khi nút View CV bị ẩn lúc Draft.

### 13.2 Link file CV gốc là gì (test BR9 / E_007)
Ẩn ô CV Attachment trên form chỉ là giấu nút. Mỗi file đính kèm còn có link riêng dạng `https://vms-ta.stg.vti.com.vn/web/content/<id file>?download=true`. Id là số tăng dần, đoán được. Ví dụ file Masked của dòng 20260 là id 326249 [STG-chạy].
1. Đăng nhập **REC User** → Application → ô **CV Attachment** → chuột phải tên file → **Copy link address**. Nếu không có link thì tải về rồi lấy URL trong Ctrl+J.
2. Mở **cửa sổ ẩn danh**, đăng nhập DL/Reviewer/Interviewer **thuần**.
3. Dán link. **Kỳ vọng:** bị chặn, báo E_007. Tải được file gốc thì là **bug BR9**.
4. Đối chứng: cùng tài khoản dán link file Masked thì phải mở được.

### 13.3 Các công đoạn kiểm tra
**Công đoạn 1. Sau khi TA upload CV** (tài khoản REC User)
| Kiểm tra | Kỳ vọng | BR |
|---|---|---|
| Ô CV Masked | Sau 1–2 phút có `<tên gốc>_masked.pdf` (STG thực tế lâu hơn, xem mục 10) | BR5, BR6 |
| Chatter | "Đã tạo CV che: N vùng được che" (STG ghi tiếng Anh) | BR6 |
| Mở file Masked | SĐT, email, địa chỉ, link MXH bị che. Họ tên, ngày sinh, ảnh, học vấn, kinh nghiệm, portfolio còn nguyên | BR1–BR3 |
| Ctrl+A, copy, dán ra Notepad | Không còn SĐT/email | BR5 |

**Công đoạn 2. Sau khi TA Submit CV.** Phải Submit rồi mới kiểm tra, vì lúc Draft dòng vẫn hiện CV gốc [STG-chạy].
| Kiểm tra | Tài khoản / cách xem | Kỳ vọng | BR |
|---|---|---|---|
| File trên dòng Review CV | REC User: mở dòng trên form Application, hoặc menu CV Review | `_masked.pdf` | BR7 |
| File đính kèm mail "Applicant: Submit CV" | Mail gửi DL/Reviewer, không gửi TA. Xem theo thứ tự: (1) chatter của Application/CV Review; (2) `?debug=1` → Settings → Technical → Email → Emails (cần quyền quản trị, thử `hoai.nguyenthithu`); (3) hộp mail thật nếu STG có gửi mail ra ngoài | `_masked.pdf`, To/CC như cũ | BR7, 3.7 |
Không xem được mail bằng cả 3 cách thì ghi "Blocked: không có quyền xem mail trên STG".

**Công đoạn 3. DL/Reviewer review CV** (lần ①, trước Accept, tài khoản **thuần**)
| Kiểm tra | Kỳ vọng | BR |
|---|---|---|
| Menu Review CV / link trong mail → mở dòng → mục "CV (s)" | Bản Masked | BR7 |
| Mở form Application (nếu vào được) | Không thấy ô CV Attachment | BR9 |
| Chatter | Không có file CV gốc | BR9 |
| Dán link file CV gốc (13.2) | Bị chặn, E_007 | BR9 |
Xong bấm **Accept** (2 hộp thoại: xác nhận → popup Accept CV, xem `du-lieu-quet-api-form-va-dropdown.md` mục 6).

**Công đoạn 4. Interviewer xem CV phỏng vấn** (lần ②, sau Accept, tài khoản **thuần**). Kiểm tra giống công đoạn 3. Mở ở menu Review CV (dòng Accepted). Add a Meeting không bắt buộc để Interviewer thấy CV.

**Công đoạn 5 (chờ BA). View CV ở list view Applications / Interview Result:** nếu có nút View CV thì bấm, phải ra bản Masked. Không có thì ghi "STG không có nút View CV ở list view".

[STG-chạy 04/11]: dòng 20260 (hồ sơ 32721, RR01413) đã Submit và Accept bằng `truong.dangvan`. Form CV Review hiện `CV_Kiểm_auto.mask.9f42a7_masked.pdf` → **BR7 đạt ở form CV Review**. BR9 chưa kiểm tra vì tài khoản có Rec Manager.

### 13.4 Trường hợp chạy qua các công đoạn
| Trường hợp | Công đoạn | Kỳ vọng |
|---|---|---|
| PDF có chữ | 1 → 4 | Luồng chính đầy đủ |
| PDF scan, PNG, JPG | 1 | Tô đen, file ra là PDF |
| Nhiều file | 1 | Mỗi file một bản Masked |
| Link ẩn, số quốc tế, địa chỉ có nhãn | 1 | Bị che |
| Website/portfolio | 1 | **Không** bị che |
| Địa chỉ không nhãn, TCVN3/VNI, ảnh chèn trong PDF | 1 | Có thể sót, ghi nhận, không tính bug (BR12) |
| Source VJP | 1 | Không có CV Masked, như cũ |
| File Word | 1, 2 | Chờ BA (E_004?). Ghi hành vi thực tế |
| File hỏng | 1, 2 | E_005. Submit CV bị chặn (E_002) |
| Submit ngay khi bản che chưa xong | 2 | Tạo bản che ngay rồi mới gửi (BR8) |
| TA upload lại CV khác | 1 | Bản Masked tạo lại theo file mới |
| REC User thay file Masked | 1 | Được. DL/Interviewer không được |
| Các role còn lại (Partner, HRI Manager, BOD, Admin System) | 3 | Theo bảng mục 12, làm sau cùng |

### 13.6 Lệnh tạo data theo công đoạn  [Claude] 04/11/2026
- Bổ sung: `test_create_rr.py` ghi `output/last_rr.txt`, đọc biến `RR_DATA`. Data mới `data/rr/rr_pure_roles.json` có Reviewer `tinh.giangthi`, Interviewer `minh.hoangkim`, còn DL/SM là `truong.dangvan`. **Chưa chạy thử** việc chọn 2 tài khoản này.
- `test_application_masking.py`: đặt `MASK_WAIT=0` thì chỉ tạo data, không chờ bản che.
- `scripts/links_for_check.py [id]` in link form, link file CV gốc/Masked, dòng Review CV → `output/links_<id>.txt`. [STG-chạy] với 32721.
- Thứ tự: RR (pure) → Approve → tạo Application → (check CĐ1) → Submit CV → (check CĐ2, CĐ3 bằng Reviewer thuần) → Accept (`truong.dangvan`) → (check CĐ4 bằng Interviewer thuần).

### 13.5 Việc tiếp theo  [Claude] đề xuất
1. Tạo RR mới có **Reviewer/Interviewer/DL là tài khoản thuần** (ví dụ Reviewer `tinh.giangthi`, Interviewer `minh.hoangkim`), cùng một hồ sơ mới gắn RR đó, rồi chạy luồng một lần để test được cả BR7 lẫn BR9.
2. Hỏi BA các điểm mới ở mục 6 (Draft hiện CV gốc, View CV là màn nào, Interview Result, mail trên STG) **trước khi** tạo Interview Result.

### 13.7 Data ứng viên và CV mẫu  [Claude] 04/11/2026
- **Data duyệt trước:** `data/application/candidates.json`, 10 ứng viên (CV01–CV09, riêng CV06A/CV06B), mỗi mã một người, một định dạng CV. Mục `lien_he` liệt kê SĐT, email, link MXH sẽ có trong CV. `{n3}`, `{n4}`, `{tag}` là phần tự sinh để không trùng ứng viên.
- `app_data(candidate="CV01")` đọc file này. Dropdown trên form (Main skill, Experience Years, University, Current Company) giữ như `app_default.json`.
- CV sinh theo bố cục hồ sơ thật (dải màu + ảnh đại diện chữ cái đầu, các mục liên hệ, học vấn, kinh nghiệm, kỹ năng). Mã mẫu chỉ còn ở chân trang nhỏ và tên file. Xem trước: `python scripts/make_cv_samples.py` → `data/cv_samples/`.
- `test_masking_batch.py` giờ lấy ứng viên theo mã CV. **CV09 (upload lại) chưa có test** vì `test_masking_reupload.py` chưa viết; batch hiện tạo 9 hồ sơ.
- Đã kiểm tra: CV PDF có chữ chứa đủ các mục "phải che" trước khi che (6/6, 4/4, 4/4).
