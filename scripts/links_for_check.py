"""In ra link de nguoi dung tu dang nhap va check bang tay (khong mo trinh duyet, khong tao data).
    python scripts/links_for_check.py          -> ho so trong output/last_application.txt
    python scripts/links_for_check.py 32721
Ghi them vao output/links_<id>.txt
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from core import config  # noqa: E402
from core.odoo_api import OdooApi  # noqa: E402

B = config.BASE_URL


def main(app_id: int):
    api = OdooApi(config.TA_USER)
    a = api.read_one("hr.applicant", app_id, ["name", "cv_mask_state", "cv_mask_error", "cv_attachment_ids",
                                              "cv_masked_attachment_ids", "applicant_line_ids"])
    att = lambda ids: api.call("ir.attachment", "read", ids, fields=["name"]) if ids else []
    out = [f"Ho so {app_id}: {a['name']}   cv_mask_state={a['cv_mask_state']}  loi={a['cv_mask_error'] or ''}", "",
           "Form Application (TA / Rec Manager / role khac thu mo):",
           f"  {B}/web#id={app_id}&action=739&model=hr.applicant&view_type=form&menu_id=569", "",
           "Link file CV GOC (role ngoai TA dan vao -> phai bi chan E_007):"]
    out += [f"  {x['name']}: {B}/web/content/{x['id']}?download=true" for x in att(a["cv_attachment_ids"])] or ["  (chua co)"]
    out += ["", "Link file CV MASKED (role xem duoc ho so -> phai mo duoc):"]
    out += [f"  {x['name']}: {B}/web/content/{x['id']}?download=true" for x in att(a["cv_masked_attachment_ids"])] \
        or ["  (chua co - ban che chua xong)"]
    out += ["", "Dong Review CV (form CV Review, muc 'CV (s)'):"]
    lines = api.call("hr.applicant.lines", "read", a["applicant_line_ids"],
                     fields=["state", "resource_request_id", "cv_attachment_ids"]) if a["applicant_line_ids"] else []
    for ln in lines:
        out.append(f"  dong {ln['id']} state={ln['state']} RR={ln['resource_request_id'] and ln['resource_request_id'][1]} "
                   f"file={[x['name'] for x in att(ln['cv_attachment_ids'])]}")
        out.append(f"  {B}/web#id={ln['id']}&action=758&model=hr.applicant.lines&view_type=form&menu_id=585")
    if not lines:
        out.append("  (chua co dong)")
    text = "\n".join(out)
    (config.OUTPUT_DIR / f"links_{app_id}.txt").write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else int((config.OUTPUT_DIR / "last_application.txt").read_text().strip()))
