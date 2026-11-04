"""Tao 1 loat Application, MOI MAU CV MOT HO SO (CV01...CV09) de nguoi dung check ket qua bang tay.

Test CHI TAO DATA (khong kiem tra ban che). Moi ho so ghi vao output/batch_masking.md:
ma mau, id, ten ho so, link -> mo link tren STG, doi ban che xong roi check bang mat.
Ten ho so co ma mau (vd "Nguyễn Văn Kiểm CV03") de nhan ra trong danh sach.

Chay tat ca:   .\\.venv\\Scripts\\python.exe -m pytest tests/test_masking_batch.py
Chay 1 mau:    .\\.venv\\Scripts\\python.exe -m pytest tests/test_masking_batch.py -k png
"""
import os
from datetime import datetime

import pytest

from core import config, mask_check
from core.cv_maker import KINDS, make_cv
from pages.application_page import ApplicationPage, app_data

RESULT_FILE = config.OUTPUT_DIR / "batch_masking.md"
# Source VJP: dung "VJP" (id 23, ten duy nhat). Cac o nay bi an khi Source thuoc VJP -> khong dien.
VJP_SOURCE = "VJP"
VJP_USER = "trung.phambao"  # Rec Manager cong ty VJP (xem docs muc 12)
VJP_HIDDEN_FIELDS = ("business_domain_id", "recruitment_type", "working_type", "market_id")
# reupload tao rieng o test_masking_reupload.py
KINDS_BATCH = [k for k in KINDS if k != "reupload"]


def note_result(kind: str, app_id: int, name: str, source: str, files, extra: str = ""):
    code = KINDS[kind][0]
    if not RESULT_FILE.exists():
        RESULT_FILE.write_text(
            "# Kết quả tạo hồ sơ test Masking (#73087)\n\n"
            "| Giờ | Mã mẫu | Định dạng | Source | Hồ sơ | Link | File upload | Kỳ vọng | Ghi chú |\n"
            "|---|---|---|---|---|---|---|---|---|\n", encoding="utf-8")
    link = f"{config.BASE_URL}/web#id={app_id}&action=739&model=hr.applicant&view_type=form&menu_id=569" if app_id else "(không tạo được)"
    row = (f"| {datetime.now():%H:%M} | {code} | {KINDS[kind][1]} | {source} | {name} (id {app_id or '-'}) | {link} | "
           f"{', '.join(f.name for f in files)} | {KINDS[kind][2].replace('Kỳ vọng: ', '')} | {extra} |\n")
    with RESULT_FILE.open("a", encoding="utf-8") as f:
        f.write(row)


@pytest.mark.parametrize("kind", KINDS_BATCH)
def test_create_application_per_cv_sample(login_as, kind):
    code = KINDS[kind][0]
    is_vjp = kind == "vjp"
    d = app_data(candidate=code)  # ung vien trong data/application/candidates.json
    if is_vjp:
        for k in VJP_HIDDEN_FIELDS:
            d.pop(k, None)
    cv = make_cv(kind, config.OUTPUT_DIR / "cv", d["cv"], stem=d["email"].split("@")[0])

    # Source VJP: TA thuoc cong ty VTI/GITS nen dropdown KHONG co nguon VJP -> dung tai khoan cong ty VJP
    page = login_as(VJP_USER if is_vjp else config.TA_USER)
    app = ApplicationPage(page)
    app.open_create()
    app.fill_form(d)
    app.upload_cv(cv["files"])
    try:
        app_id = app.save()
    except AssertionError as e:
        if kind != "docx":
            raise
        # Word: STG chan ngay luc Save (khong phai loi script). Ghi lai thong bao that de bao BA.
        msg = " ".join(str(e).split())
        note_result(kind, 0, f"{d['last_name']} {d['first_name']}", d["source_id"], cv["files"], f"STG chặn khi Save: {msg}")
        print(f"[{code}] STG chan file Word: {msg}")
        page.screenshot(path=str(config.OUTPUT_DIR / "word_bi_chan.png"))  # anh popup loi, xem lai bat cu luc nao
        if not config.HEADLESS:  # cho nguoi xem popup truoc khi trinh duyet dong (doi so giay: $env:PAUSE_SEC="60")
            page.wait_for_timeout(int(os.getenv("PAUSE_SEC", "30")) * 1000)
        return
    mask_check.save_spec(app_id, cv)
    name = f"{d['last_name']} {d['first_name']}"
    # Working History (Submit CV bat buoc phai co). Loi o buoc nay khong lam mat ho so da tao -> chi ghi chu.
    wh_note = ""
    try:
        app.add_working_history(d["working_history"])
    except Exception as e:
        wh_note = "Chưa thêm được Working History: " + " ".join(str(e).split())[:150]
        print(f"[{code}] {wh_note}")
    note_result(kind, app_id, name, d["source_id"], cv["files"], wh_note)
    print(f"\n[{code}] id={app_id} {name} source={d['source_id']} files={[f.name for f in cv['files']]}")
