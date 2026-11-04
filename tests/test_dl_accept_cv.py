"""DL mo dong Review CV (menu Recruitment > Applications > Review CV, action 758) -> Accept CV,
roi mo View CV tren Application de xem CV hien ra la ban nao (BR7, BR9).

Dung tai khoan DL cua RR. Luu y: `truong.dangvan` con la Rec Manager nen thay ca CV goc
-> test nay chi chay thong luong + kiem tra BR7, KHONG chung minh BR9 (can tai khoan thuan, xem docs).
Test ghi lai hanh vi that (khong assert dung/sai BR) vao output/accept_cv_<app>.txt va probe_dl_*.txt.

Chay: .\\.venv\\Scripts\\python.exe -m pytest tests/test_dl_accept_cv.py
Doi tai khoan: DL_ACCOUNT=ten.tai.khoan   Doi ho so: APP_ID=...
"""
import os

from core import config
from core.odoo_api import OdooApi
from core.probe import dump_page

LINE_URL = config.BASE_URL + "/web#id={id}&action=758&model=hr.applicant.lines&view_type=form&menu_id=585"
APP_URL = config.BASE_URL + "/web#id={id}&action=739&model=hr.applicant&view_type=form&menu_id=569"


def _line_state(api, line_id):
    ln = api.call("hr.applicant.lines", "read", [line_id], fields=["state", "cv_attachment_ids"])[0]
    names = [x["name"] for x in api.call("ir.attachment", "read", ln["cv_attachment_ids"], fields=["name"])] if ln["cv_attachment_ids"] else []
    return ln["state"], names


def test_dl_accept_cv_and_view_cv(login_as):
    app_id = int(os.getenv("APP_ID") or (config.OUTPUT_DIR / "last_application.txt").read_text().strip())
    user = os.getenv("DL_ACCOUNT") or config.DL_USER
    api = OdooApi(user)
    lines = api.call("hr.applicant.lines", "search_read", [["applicant_id", "=", app_id]], fields=["state"], order="id desc")
    assert lines, f"{user} khong thay dong Review CV nao cua ho so {app_id} (RR khong gan tai khoan nay?)"
    line_id = lines[0]["id"]
    report = [f"Tai khoan: {user}  Ho so: {app_id}  Dong Review CV: {line_id}", ""]
    state, files = _line_state(api, line_id)
    report.append(f"TRUOC: state={state}  file CV tren dong={files}")

    page = login_as(user)
    p = page
    # 1. Mo dong Review CV
    p.goto(LINE_URL.format(id=line_id), wait_until="domcontentloaded", timeout=config.TIMEOUT_MS * 3)
    p.locator(".o_form_view").first.wait_for(timeout=config.TIMEOUT_MS * 3)
    p.wait_for_timeout(3000)
    dump_page(p, "dl_form_review_line")
    report.append(f"Nut Accept CV hien: {p.locator('button[name=accept_cv_form]:visible').count() > 0}")

    # 2. Accept CV (chi khi dong dang Submitted)
    if state == "submit":
        p.locator("button[name=accept_cv_form]:visible").first.click()
        # Co the co 2 hop thoai: xac nhan -> popup "Accept CV" (Interviewer + Message, nut Accept name=accept_cv)
        dlg = p.locator(".modal-dialog:visible")
        for _ in range(4):
            try:
                dlg.first.wait_for(timeout=6000)
            except Exception:
                break
            report.append("Hop thoai: " + " | ".join(dlg.first.inner_text().splitlines()))
            final = dlg.first.locator("button[name=accept_cv]")
            if final.count():
                final.first.click()
            else:
                dlg.first.locator(".modal-footer button.btn-primary").first.click()
            try:
                dlg.first.wait_for(state="hidden", timeout=config.TIMEOUT_MS * 3)
            except Exception:
                pass
        p.wait_for_timeout(5000)
        dump_page(p, "dl_after_accept")
        state, files = _line_state(api, line_id)
        report.append(f"SAU Accept: state={state}  file CV tren dong={files}")
    else:
        report.append(f"Bo qua Accept vi dong dang o trang thai {state}")

    # 3. View CV tren Application
    p.goto(APP_URL.format(id=app_id), wait_until="domcontentloaded", timeout=config.TIMEOUT_MS * 3)
    p.locator(".o_form_view").first.wait_for(timeout=config.TIMEOUT_MS * 3)
    p.wait_for_timeout(3000)
    report.append(f"O CV Attachment hien tren Application: {p.locator('.o_form_view [name=cv_attachment_ids]:visible').count() > 0}")
    report.append(f"O CV Masked hien tren Application: {p.locator('.o_form_view [name=cv_masked_attachment_ids]:visible').count() > 0}")
    btn = p.locator(".o_form_view button[name='view_cv']:visible")
    if btn.count():
        btn.first.click()
        p.wait_for_timeout(5000)
        dump_page(p, "dl_view_cv")
        links = p.evaluate("""() => [...document.querySelectorAll('.modal a[href], .modal iframe[src], .modal embed[src], .modal object[data]')]
                              .map(e => (e.tagName + ' ' + (e.getAttribute('href') || e.getAttribute('src') || e.getAttribute('data'))).slice(0, 200))""")
        report.append("View CV: cac link/khung trong popup = " + str(links))
    else:
        report.append("Khong thay nut View CV tren Application")

    (config.OUTPUT_DIR / f"accept_cv_{app_id}.txt").write_text("\n".join(report), encoding="utf-8")
    print("\n" + "\n".join(report))
