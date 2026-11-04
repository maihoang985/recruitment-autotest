# recruitment

Auto test module Recruitment (TA) trên https://vms-ta.stg.vti.com.vn/. Viết bằng Python, Playwright và pytest.
Mục tiêu đầu tiên: task **#73087**, test tính năng Masking che contact ứng viên trong CV.

## Cấu trúc
```
recruitment/
├─ core/            # config, login (dùng chung)
├─ tests/           # test pytest
├─ codegen/         # code ghi bằng Playwright codegen (nguyên liệu để viết test)
├─ data/cv_samples/ # bộ CV mẫu để upload
├─ output/          # file tải về, báo cáo (không commit)
└─ scripts/         # setup.ps1, codegen.ps1
```

## Cài lần đầu
```powershell
cd D:\Auto-test\recruitment
powershell -ExecutionPolicy Bypass -File scripts\setup.ps1
```
Sau đó mở file `.env` và điền `DEFAULT_PASSWORD`, `TA_USER`. File `.env` không được commit.

## Ghi thao tác bằng codegen
```powershell
powershell -ExecutionPolicy Bypass -File scripts\codegen.ps1 tao_application
```
Code được lưu vào `codegen\tao_application.py`. Mỗi luồng nên ghi một file riêng, ví dụ:
`dang_nhap`, `tao_application`, `xem_cv_masked`, `submit_cv`, `view_cv`.
Trước khi chia sẻ, **xóa mật khẩu** trong file codegen.

## Chạy test
```powershell
.\.venv\Scripts\python.exe -m pytest
```
`tests/test_login.py` là smoke test kiểm tra đăng nhập bằng `TA_USER`.
