# Checklist viết auto test (dùng cho mọi project)

> Rút ra từ phiên tạo/duyệt RR trên VMS TA STG (Odoo 12, Playwright Python), 04/11/2026. Chi tiết phiên: `docs/session-tao-rr-tom-tat.md`.
> Bổ sung 08/11/2026 từ phiên tạo Application + kiểm tra CV Masked (task #73087). Chi tiết: `docs/task-73087-masking-test-tom-tat.md` mục 10. Các mục bổ sung ghi **(bổ sung 08/11)**.
> Nguồn: [STG-chạy] = bài học từ lần chạy thật bị lỗi; [User] = người dùng chỉ ra; [Claude] = lời khuyên chung của Claude, chưa kiểm chứng ở project khác.
> Bản dùng chung: `D:\Auto-test\CHECKLIST-auto-test.md`.

## 0. Quy trình tổng cho một flow (bổ sung 08/11)
> Thứ tự công việc, chi tiết từng việc ở các mục bên dưới. Đề xuất, **chưa chạy thử trọn vẹn trên flow nào**. [Claude]
> Người dùng chỉ có mặt ở bước 1, 6 và lúc cho phép xóa ở bước 14. Các bước còn lại Claude tự làm.
> **Mỗi flow một phiên chat**, bàn giao qua `docs/`, vì chat càng dài thì mỗi câu càng tốn token. [Claude]

**Giai đoạn 1: Chuẩn bị (làm một lần cho cả flow, làm gọn vì có những thứ chỉ chạy thật mới lộ ra)**
- [ ] **Bước 1. Người dùng giao việc:** flow nào, mục SRS nào, role nào, điều cấm làm trên môi trường. Chưa có danh sách điều cấm thì hỏi. [Claude]
- [ ] **Bước 2. Đọc mục lục `docs/README.md`, đọc trọn các file liên quan đến flow và SRS, rồi lập bảng flow:** bước, role, thao tác, **kết quả đúng** (kèm nguồn SRS), có gửi mail hoặc khó hoàn tác không. Viết **dễ hiểu như kể chuyện** (ai làm gì, để làm gì, xong chuyển cho ai) vì người dùng có thể đang học nghiệp vụ. Kết quả đúng lấy từ SRS, không lấy từ hành vi hiện tại của hệ thống, nếu không test sẽ luôn pass kể cả khi hệ thống sai. [Claude]
- [ ] **Bước 3. Đọc bản ghi mẫu do người tạo tay, rồi quét API/metadata mọi màn trong flow một lần**, ghi vào `docs/`. Quét bằng **tài khoản của role làm bước đó**, vì nút, ô, dropdown và bản ghi nhìn thấy có thể khác theo role. Không cần quét mọi màn với mọi role, trừ khi test phân quyền. Có source code hệ thống thì đọc phần liên quan, sẽ bớt được nhiều lần chạy thăm dò. [Claude]
- [ ] **Bước 4. Đánh dấu nút có thể mở popup mà API không báo trước** (Odoo: `type="object"`) để lần chạy đầu ghi lại. [STG-chạy: popup Add a Meeting, Accept CV chỉ lộ khi chạy]
- [ ] **Bước 5. Đối chiếu SRS với API, liệt kê chỗ lệch. Soạn data.** Có việc chạy nền thì hỏi người dùng (mục 1). [Claude]
- [ ] **Bước 6. Người dùng duyệt một file gộp:** bảng flow; từng chỗ lệch (bug, SRS cũ hay hỏi BA, **mặc định ghi "hỏi BA"** nếu người dùng chưa nắm nghiệp vụ); data kèm danh sách người sẽ nhận mail. Người dùng không phải xem field, XML, HTML, locator, code. Chưa duyệt thì chưa viết code. [Claude]

**Giai đoạn 2: Làm từng bước của flow**
- [ ] **Bước 7. Viết code một bước, đi đường thuận trước.** Tách tạo data, lưu kỳ vọng, kiểm tra (mục 3). Mỗi bước dùng record **do bước trước vừa tạo**. Lỗi ở bước nào thì sửa và chạy lại bước đó, không tạo lại từ đầu; nếu record đã bị đổi trạng thái giữa chừng thì báo người dùng quyết định. [Claude] + [User: chạy từ đầu flow, không dùng data cũ]
- [ ] **Bước 8. Chạy thử chưa Save** với form chưa từng lưu thành công (mục 4); form đã chạy được thì bỏ qua. Lần chạy đầu, **ghi màn hình ra file text sau mỗi bước** để không phải đi riêng một chuyến chỉ để thăm dò, nhưng **chỉ đọc file khi lỗi hoặc ở các nút đã đánh dấu** ở bước 4. Bật trace (`--tracing on`) để người dùng xem lại robot đã làm gì. [Claude]
- [ ] **Bước 9. Chạy thật, kiểm tra kết quả qua API/DB** (mục 3).
- [ ] **Bước 10. Nếu lỗi:** đọc file text. Chỉ lấy HTML thô của đúng khúc cần xem khi phần tử không có tên, bị trùng tên, hoặc file text không đủ. Vá mò quá 2 lần thì dừng lại điều tra (mục 4). [Claude]
- [ ] **Bước 11.** Bước này chạy được mới sang bước sau, quay lại bước 7. [STG-chạy]

**Giai đoạn 3: Chốt**
- [ ] **Bước 12. Chạy lại cả flow từ đầu với data mới**, vì từng bước pass riêng chưa chắc nối lại đã chạy được. [Claude]
- [ ] **Bước 13. Thêm trường hợp sai:** thiếu ô bắt buộc, sai quyền, Reject. [Claude]
- [ ] **Bước 14. Dọn data rác** (người dùng cho phép, mục 5) **và tóm tắt vào `docs/`**, gồm: flow theo thực tế đã chạy (mỗi bước ai làm, trạng thái đổi ra sao, mail gửi cho ai) để làm tài liệu học nghiệp vụ; **số lần chạy, số lần lỗi, nguyên nhân** để biết chỗ nào thật sự tốn; cập nhật `docs/README.md`. [STG-chạy] + [User] + [Claude]

## 1. Trước khi viết code: hiểu hệ thống bằng cách rẻ nhất
- [ ] Đọc **hết** tài liệu đã có trong project (`docs/`, file tóm tắt phiên trước) trước dòng code đầu tiên. [STG-chạy: `resource-request.md` có sẵn trường bắt buộc nhưng không được đọc hết]
- [ ] Ưu tiên nguồn có cấu trúc: API, schema, Swagger, SRS, code hệ thống. Trình duyệt và ảnh chụp là cách đắt nhất. [Claude]
- [ ] Liệt kê trước các luật của form: trường bắt buộc, giá trị mặc định, định dạng ngày và số, độ dài tối thiểu, hộp xác nhận, wizard, luồng trạng thái. [STG-chạy: 6 luật chỉ lộ ra khi chạy hỏng (DL mặc định sai, ngày dd/mm/yyyy, Currency, ≥150 từ, Confirm, Reject Reason)]
- [ ] **(bổ sung 08/11)** Đọc trước nút bấm từ metadata form: nút nào hiện ở trạng thái nào, nút nào có hộp xác nhận (kèm câu chữ), nút nào mở popup nhập liệu, nút trong bảng con. Odoo: `fields_view_get`, script `scripts/inspect_model.py`. Không biết trước được: lỗi do code kiểm tra lúc bấm, popup do code trả về, popup onchange. [STG-chạy: đọc ra đúng hộp Confirm của Submit/Approve RR, nút Submit CV; riêng popup "Working History" chỉ lộ khi chạy]
- [ ] **(bổ sung 08/11)** Đọc **một bản ghi mẫu do người tạo bằng tay** để biết cần điền ô nào và giá trị ra sao, trước khi đọc cả form. [STG-chạy: hồ sơ 32625 cho biết ngay các ô bắt buộc có điều kiện]
- [ ] **(bổ sung 08/11)** Tính năng có việc chạy nền (job, queue, mail, đồng bộ): **hỏi người dùng** job có đang chạy, bao lâu chạy một lần, ai chạy, **trước khi** chạy test phải chờ. [User: "bạn có thể hỏi trực tiếp tôi trước khi chạy"; STG-chạy: mất 1 lần chạy 6 phút mới biết job che CV chưa chạy]
- [ ] Biết trước thao tác nào **gửi mail hoặc không hoàn tác được** (Submit, Approve, Reject…). [STG-chạy]
- [ ] **(bổ sung 08/11)** **Dropdown phải áp domain của ô.** Lấy bằng `fields_get(<ô>, attributes=["domain"])` rồi `search_read` theo domain đó. Chỉ đọc cả bảng thì chọn phải giá trị không hiện trong dropdown. [STG-chạy: "Others" có trong bảng lý do nhưng ô Resignation Reason chỉ nhận `apply_for = 'resignation_reason'`, mất 1 lần chạy]
- [ ] **(bổ sung 08/11)** Ghi **giá trị mặc định** của ô (`default_get`), không chỉ danh sách lựa chọn, để người dùng biết ô nào hệ thống tự chọn sẵn. [STG-chạy + User: Number of Rounds mặc định `multi`, người dùng hỏi vì sao test "chọn" Multiple Rounds]
- [ ] **(bổ sung 08/11)** **Ai nhìn thấy bản ghi phụ thuộc quan hệ với bản ghi, không chỉ role.** Quét thêm "tài khoản nào đọc được bản ghi này" bằng `search_read` theo từng tài khoản. Tài khoản **nhiều role** làm hỏng phép thử phân quyền. [STG-API: dòng Review CV chỉ hiện với Reviewer/Interviewer/DL gắn với RR; 6 tài khoản thuần role không thấy hồ sơ; `truong.dangvan` có cả Rec Manager nên thấy CV gốc]
- [ ] **(bổ sung 08/11)** **Tìm thao tác nằm ở màn nào bằng cách tra từ khóa trong SRS/Redmine trước**, rồi mới dò giao diện. [STG-chạy: Create Result nằm ở màn RR, dò 5 bước trên màn Application mới biết; người dùng dán đoạn SRS là xong]
- [ ] **(bổ sung 08/11)** Lời đồn ("phải điền giờ quá khứ thì mới tạo được") thì **kiểm chứng bằng API**, không tin ngay và không bỏ qua. Điều đã biết về môi trường (STG có gửi mail thật không, ai được xóa data) **ghi vào file môi trường** để khỏi hỏi lại người dùng. [STG-chạy: đã hỏi người dùng về thư mời trong khi bộ nhớ đã ghi STG không gửi mail thật]

## 2. Data test
- [ ] Data để trong file riêng (JSON, YAML, Excel), **không hardcode** trong code. [User]
- [ ] Ngày tháng lưu dạng "+N ngày" để không hết hạn. [Claude]
- [ ] **Cho người dùng xem và duyệt data trước** khi viết code, nhất là trên môi trường khách nghiệm thu. [User]
- [ ] Nội dung giống thật, tiếng Việt có dấu, không nêu tên khách hàng. [User]
- [ ] Đánh dấu data do test tạo (tên riêng hoặc ngày giờ) để dễ tìm và dọn. [Claude]
- [ ] **(bổ sung 08/11)** Data có thể bị hệ thống báo trùng (email, SĐT…) thì **sinh mới mỗi lần chạy**. [STG-chạy: `app_data()` sinh email/SĐT theo thời gian]
- [ ] **(bổ sung 08/11)** File test tự sinh (PDF, ảnh, Excel…) phải **tự kiểm tra lại ngay sau khi tạo**: đọc lại nội dung xem đúng chưa, dung lượng có trong giới hạn không. [STG-chạy: font Arial trích dấu cách thành `\xa0`, Segoe UI trích `( )` thành `﴾ ﴿`, PDF nhúng nguyên font nặng 2MB; suýt báo bug oan cho tính năng che]

## 3. Viết test
- [ ] Chia theo bước nhỏ (tạo, gửi, duyệt…), mỗi bước một test, truyền kết quả qua file hoặc fixture (ví dụ `output/last_rr.txt`). [STG-chạy]
- [ ] Page object và hàm dùng chung cho thao tác lặp: dropdown, hộp thoại, chờ trang, tìm kiếm. [Claude]
- [ ] Locator theo nghĩa (nhãn, role, tên trường), tránh id sinh tự động. [Claude]
- [ ] **Chờ đúng thứ cần dùng**, không chờ "cả trang" hay trang mặc định sau đăng nhập. [User: "chỉ cần đợi menu Rec, Helpdesk kệ nó"]
- [ ] Hộp xác nhận chỉ bấm **một lần**, rồi chờ nó đóng. [STG-chạy: bấm Confirm 2 lần gây lỗi]
- [ ] **(bổ sung 08/11)** **Chuỗi hộp thoại liên tiếp** (xác nhận, rồi wizard; ví dụ Accept CV): xử lý theo vòng lặp, thấy nút đích (theo `name`) thì bấm, không thì bấm Confirm, và **chờ hộp thoại đóng hẳn rồi mới xét hộp tiếp**. Không bấm lặp lúc STG chậm, có thể gửi mail nhiều lần. [STG-chạy: Submit CV bấm Confirm 3 lần vì không chờ đóng; Accept CV có 2 hộp, lần đầu chỉ bấm hộp 1 nên dòng vẫn `submit`]
- [ ] **(bổ sung 08/11)** Tách 3 phần: **tạo data** (qua giao diện), **lưu kỳ vọng ngay lúc tạo** (file spec), **kiểm tra** bằng lệnh chạy lại được mà không tạo data mới. Không để test giao diện ngồi chờ việc chạy nền. [STG-chạy: `scripts/check_mask.py`, `MASK_WAIT=0`; quên lưu spec lúc tạo hồ sơ 32721 nên phải dựng lại 2 lần]
- [ ] **(bổ sung 08/11)** Kiểm tra kết quả **qua API/DB** (trạng thái, file đính kèm, chatter) thay vì đọc màn hình. Giao diện chỉ dùng cho phần cần kiểm tra giao diện. [STG-chạy]
- [ ] **(bổ sung 08/11)** Popup lạ phát hiện khi chạy thì gom vào **một danh sách dễ sửa** (chữ trong popup → nút bấm), gặp popup chưa biết thì dừng và báo rõ nội dung. [STG-chạy: `KNOWN_POPUPS` trong `pages/application_page.py`]
- [ ] **(bổ sung 08/11)** Dropdown/autocomplete: gõ lại và thử lại khi kết quả chậm (onchange của ô trước chưa xong). [STG-chạy: ô Experience Years lúc được lúc không]
- [ ] **(bổ sung 08/11)** **Điền xong thì đọc lại giá trị các ô, ô nào trống thì điền lại** (tối đa 3 lần) trước khi upload hoặc Save. Phản hồi onchange trễ có thể ghi đè lên ô đã điền. [STG-chạy: Main Skill, Gender trống và file CV biến mất, Save báo "CV Attachment is not Null"]
- [ ] **(bổ sung 08/11)** **Quy tắc popup form Odoo** (bổ sung cho `KNOWN_POPUPS`): [STG-chạy + User]
  - Save xong popup **vẫn mở** ở chế độ xem (hiện nút Edit, Create). Chờ nút `button.o_form_button_edit` hiện **trong popup** rồi bấm **×** (`.modal-header button.close`) để đóng. Nút Save nằm trong thân form, không phải `.modal-footer`.
  - Ô ngày giờ gõ xong phải **Enter** mới chốt, dropdown phải chọn một dòng.
  - Tên ô trong popup có thể trùng form chính (`current_company_id`, `business_domain_id`): phải khoanh vùng tìm ô trong popup.
  - Hàm bắt "popup lạ" phải bỏ qua popup do chính test mở.
- [ ] **(bổ sung 08/11)** **Đăng nhập chịu lỗi mạng:** `goto` dùng `wait_until="commit"`, chờ ô đăng nhập, thử lại 5 lần, nới thời gian chờ sau khi bấm đăng nhập. **Dùng phiên đăng nhập đã lưu** (`storage_state`, `scripts/save_auth.py`) để khỏi đăng nhập mỗi lần chạy. [STG-chạy: `ERR_NETWORK_CHANGED`, "interrupted by another navigation", timeout sau đăng nhập, khoảng 6 lần chạy hỏng; chưa dùng phiên đã lưu nên chưa kiểm chứng]
- [ ] **(bổ sung 08/11)** **Test phải kiểm tra trạng thái trước khi tạo** (đã có dòng Review CV chưa, đã có Working History chưa) để chạy lại không tạo trùng. Chạy trên bản ghi có sẵn qua biến môi trường (`APP_ID`, `RR_ID`). [STG-chạy]
- [ ] **(bổ sung 08/11)** **Kịch bản phụ thuộc trạng thái chỉ dùng được một lần.** Lên kế hoạch thứ tự trước, hoặc dùng bản ghi riêng cho từng kịch bản. [STG-chạy: bản che đang `pending` bị dùng hết khi Submit CV (hệ thống tạo ngay), nên BR8 và BR6 không còn làm lại được trên hồ sơ 32721]
- [ ] Ghi đặc điểm của framework thành code dùng chung ngay từ đầu. Với Odoo 12: [STG-chạy]
  - không dùng `networkidle` (luôn có kết nối nền): chờ **một ô hoặc nút cụ thể** thay vì chờ mạng yên. [STG-chạy; phiên 04/11 mình đã dùng `networkidle` trong `_settle()` và phải sửa lại, xem mục 4 bổ sung 08/11]
  - dropdown phải **click vào giá trị** thì mới tắt [User, nhắc 2 lần];
  - list có bộ lọc mặc định, phải xóa trước khi tìm;
  - sau đăng nhập có thể về trang mặc định khác, nên vào thẳng URL và chờ menu của màn cần dùng.

## 4. Gỡ lỗi tiết kiệm thời gian và token
- [ ] Gỡ lỗi phần điền form **chưa Save** (điền xong thì Discard). Form sạch lỗi rồi mới cho lưu. [STG-chạy: mỗi lần chạy lỗi sau Save để lại 1 RR rác]
- [ ] Khi lỗi, tự ghi trạng thái trang ra **file text** (URL, nút đang hiện, hộp thoại, thông báo lỗi), thay vì đọc ảnh. [Claude]
- [ ] Bật trace (`--tracing retain-on-failure`) để người dùng tự mở xem. [Claude]
- [ ] Tìm nguyên nhân trước khi vá. **Vá mò quá 2 lần thì dừng lại điều tra.** [STG-chạy: vá 5 kiểu cho lỗi điều hướng]
- [ ] Môi trường chậm hoặc trắng trang thì kiểm tra server trước, đừng chạy lại liên tục. [STG-chạy]
- [ ] Sửa code bằng công cụ Edit, không dùng script thay chuỗi. Sửa xong phải kiểm tra code import được. [STG-chạy: 3 lần lỗi cú pháp, 1 lần script hỏng lặng lẽ]
- [ ] **(bổ sung 08/11)** Kết quả lệnh **chỉ in phần cần thiết**: lỗi API chỉ in dòng cuối, không in cả traceback; danh sách dài thì cắt bớt. [STG-chạy: 3 traceback Odoo dài khi thử gọi đọc form theo view_id]
- [ ] **(bổ sung 08/11)** pytest chạy với `-q --tb=short`, ghi kết quả ra file rồi đọc một lần. **Không chạy lại chỉ để xem lỗi.** [STG-chạy: chạy lại thêm 90 giây chỉ để lọc dòng lỗi]
- [ ] **(bổ sung 08/11)** **Sửa hàm dùng chung (page object) thì chạy lại test cũ đang pass** trước khi coi là xong. Không để hàm sửa dở. [STG-chạy: sửa `fill_form`, `upload_cv` mà chưa chạy lại test tạo Application]
- [ ] **(bổ sung 08/11)** Báo cáo của test **không ghi "lỗi"** chỉ vì thấy popup còn mở. Quyết định đúng/sai bằng API (bản ghi đã tạo chưa, trạng thái gì). [STG-chạy: báo "Loi khi Save" trong khi cuộc họp đã được tạo]
- [ ] **(bổ sung 08/11)** Lệnh gọi API có kiểu tham số khác nhau theo model (Odoo: `fields_view_get` của `hr.applicant` cần `[]` đầu tiên, `applicant.working.history` thì cần tham số có tên). Bọc `call()` để lỗi chỉ in dòng cuối, và thử cả hai cách. [STG-chạy: 3 lần traceback dài]

## 5. An toàn trên môi trường chung (STG, UAT, nghiệm thu)
- [ ] Có bước **dọn rác** sau mỗi lần chạy thử, chỉ xóa data do chính test tạo. Liệt kê và kiểm tra trước khi xóa. [STG-chạy]
- [ ] Xin phép người dùng trước khi xóa hoặc đổi trạng thái data. [STG-chạy]
- [ ] Hiểu cách xóa của hệ thống. Ví dụ Odoo VMS chỉ xóa được bản ghi Draft, đã Submit thì phải Reject → Set to draft → Delete. [STG-chạy]
- [ ] Không lưu mật khẩu hay session vào code hoặc tài liệu. Đưa session cho AI xong thì đăng xuất. [Claude]

## 6. Làm việc với Claude
- [ ] Đầu project, cho Claude một file mô tả: URL, tài khoản theo role (không kèm mật khẩu), tài liệu nghiệp vụ, điều cấm làm trên môi trường. [Claude]
- [ ] Yêu cầu Claude cho xem data và kế hoạch **trước** khi viết code hoặc chạy trên server. [User]
- [ ] Gợi ý của người dùng (người thấy màn hình thật) phải được làm theo ngay. Claude không làm theo thì nhắc thẳng. [STG-chạy]
- [ ] Cuối phiên, yêu cầu tóm tắt vào file md trong `docs/` để phiên sau không phải tìm hiểu lại. [User]
- [ ] **(bổ sung 08/11)** Người dùng **không phải lấy locator hay chụp màn hình**. Claude đọc metadata, viết script, người dùng (hoặc Claude) chạy, lỗi thì tự ghi file text (probe), Claude đọc rồi sửa. [User]
- [ ] **(bổ sung 08/11)** Tài liệu ghi **nguồn cho từng thông tin** (Redmine, SRS kèm số ô, hệ thống thật, suy đoán của Claude, người dùng). Suy đoán phải ghi rõ "chưa chứng thực". [User: phiên trước ghi suy đoán như sự thật, gây loạn]
- [ ] **(bổ sung 08/11)** Sửa tài liệu theo từng mục, không viết lại cả file. [STG-chạy: viết lại file 300 dòng 2 lần]
- [ ] **(bổ sung 08/11)** Mỗi bước lớn mở **phiên mới**, dựa vào `docs/` để làm tiếp. Việc lặp lại (chạy lệnh, sửa tài liệu, code theo khuôn) dùng Sonnet; phân tích lỗi lạ, đối chiếu yêu cầu dùng Opus hoặc `opusplan`. [Claude]
