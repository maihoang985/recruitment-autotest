"""Review CV -> Submit CV khi ban che CHUA XONG (BR8), tren ho so da co san (khong tao ho so moi).

Ho so: output/last_application.txt (hoac bien moi truong APP_ID). RR: output/last_rr.txt (RR dang Open).
Test KHONG assert dung/sai cua BR8, chi GHI LAI hanh vi that vao output/submit_cv_<id>.txt de nguoi dung check:
  - Submit co bi chan khong, thong bao gi (E_002?)
  - Sau Submit: ban che da duoc tao ngay chua, file CV tren dong Review CV la goc hay masked (BR7)
Chay: .\\.venv\\Scripts\\python.exe -m pytest tests/test_submit_cv_pending.py
"""
import os

from core import config
from core.odoo_api import OdooApi
from pages.application_page import ApplicationPage, app_data


def _snapshot(api: OdooApi, app_id: int) -> list[str]:
    a = api.read_one("hr.applicant", app_id, ["cv_mask_state", "cv_mask_error", "cv_attachment_ids",
                                              "cv_masked_attachment_ids", "applicant_line_ids"])
    names = lambda ids: [x["name"] for x in api.call("ir.attachment", "read", ids, fields=["name"])] if ids else []
    out = [f"cv_mask_state = {a['cv_mask_state']}  error = {a['cv_mask_error']}",
           f"CV goc      = {names(a['cv_attachment_ids'])}",
           f"CV masked   = {names(a['cv_masked_attachment_ids'])}"]
    for ln in api.call("hr.applicant.lines", "read", a["applicant_line_ids"],
                       fields=["state", "resource_request_id", "cv_attachment_ids", "submit_date"]) if a["applicant_line_ids"] else []:
        out.append(f"Dong Review CV {ln['id']}: state={ln['state']} RR={ln['resource_request_id'] and ln['resource_request_id'][1]} "
                   f"submit_date={ln['submit_date']} file CV tren dong={names(ln['cv_attachment_ids'])}")
    return out


def test_submit_cv_while_mask_pending(login_as):
    app_id = int(os.getenv("APP_ID") or (config.OUTPUT_DIR / "last_application.txt").read_text().strip())
    rr = (config.OUTPUT_DIR / "last_rr.txt").read_text().strip()
    api = OdooApi(config.TA_USER)
    report = [f"Application {app_id}, RR {rr}", "", "== TRUOC khi Submit ==", *_snapshot(api, app_id)]

    page = login_as(config.TA_USER)
    app = ApplicationPage(page)
    app.open_existing(app_id)
    has_wh = api.call("applicant.working.history", "search_count", [["applicant_id", "=", app_id]])
    if not has_wh:  # Submit CV bat buoc co Working History (loi "Please kindly provide Working History...")
        app.add_working_history(app_data()["working_history"])
        report += ["", "== Da them Working History =="]
    if not api.read_one("hr.applicant", app_id, ["applicant_line_ids"])["applicant_line_ids"]:
        app.edit()
        app.add_review_line(rr)
        app.save()
        report += ["", "== Da them dong Review CV + Save =="]
    report += ["", "== Truoc khi bam Submit =="] + _snapshot(api, app_id)

    message = app.submit_cv_on_line()
    page.wait_for_timeout(5000)
    report += ["", "== Bam Submit CV ==", f"Hop thoai/thong bao: {message or '(khong co)'}", "", "== SAU khi Submit ==",
               *_snapshot(api, app_id), "", "== Chatter (5 tin cuoi) =="]
    report += [" ".join(m.replace("<", " <").split())[:200] for m in api.chatter("hr.applicant", app_id)[-5:]]

    (config.OUTPUT_DIR / f"submit_cv_{app_id}.txt").write_text("\n".join(report), encoding="utf-8")
    print("\n" + "\n".join(report))
