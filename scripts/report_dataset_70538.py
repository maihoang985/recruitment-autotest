"""In bang ket qua data #70538 cho nguoi dung check tay (chi doc, khong tao gi). Chay lai bao nhieu lan cung duoc.
    python scripts/report_dataset_70538.py
Ket qua: output/dataset_70538.md
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from core import config  # noqa: E402
from core.odoo_api import OdooApi  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
DATA = json.loads((config.DATA_DIR / "application" / "dataset_70538.json").read_text(encoding="utf-8"))
STATE = config.OUTPUT_DIR / "dataset_70538_state.json"
APP_URL = config.BASE_URL + "/web#id={id}&action=739&model=hr.applicant&view_type=form&menu_id=569"
OLD_CV_DOMAIN = [["cv_mask_state", "=", False], ["cv_attachment_ids", "!=", False], ["source_id.company_id.name", "=", "VTI Corporation"]]


def row_info(api: OdooApi, app_id: int) -> tuple[str, str, str]:
    a = api.read_one("hr.applicant", app_id, ["cv_mask_state", "cv_mask_error", "cv_masked_attachment_ids", "applicant_line_ids", "meet_ids", "is_duplicate"])
    masked = ""
    if a["cv_masked_attachment_ids"]:
        masked = ", ".join(x["name"] for x in api.call("ir.attachment", "read", a["cv_masked_attachment_ids"], fields=["name"]))
    state = str(a["cv_mask_state"] or "không có") + (f" ({a['cv_mask_error']})" if a["cv_mask_error"] else "")
    line = "chưa có"
    if a["applicant_line_ids"]:
        line = api.call("hr.applicant.lines", "read", a["applicant_line_ids"][:1], fields=["state"])[0]["state"]
    if a["meet_ids"]:
        line += " + đã có Meeting"
    if a["is_duplicate"]:
        line += " (DÍNH CỜ TRÙNG CV)"
    return state, masked or "không có", line


def main():
    state = json.loads(STATE.read_text(encoding="utf-8")) if STATE.exists() else {}
    rr = (config.OUTPUT_DIR / "last_rr.txt").read_text(encoding="utf-8").strip()
    out = [f"# Data test Masking #70538 · RR {rr}", "",
           "| ID | Nội dung | Source | Hồ sơ | Người tạo | Trạng thái che | CV Masked | Dòng Review CV | Bạn check | Link |",
           "|---|---|---|---|---|---|---|---|---|---|"]
    for row in DATA["rows"]:
        cur = state.get(row["id"])
        if not cur or not cur.get("app_id"):
            out.append(f"| {row['id']} | {row['mo_ta']} | {row['source_id']} | CHƯA TẠO | | | | | {row['check']} | |")
            continue
        try:
            mask, masked, line = row_info(OdooApi(cur["user"]), cur["app_id"])
        except Exception as e:
            mask, masked, line = "lỗi đọc: " + str(e)[-80:], "", ""
        done = "" if cur.get("done") else " (CHƯA XONG)"
        out.append(f"| {row['id']} | {row['mo_ta']} | {row['source_id']} | {cur['name']} ({cur['app_id']}){done} | {cur['user']} | {mask} | {masked} | {line} | {row['check']} | {APP_URL.format(id=cur['app_id'])} |")
    extras = [f"- {rid}: `{c['extra_file']}`" for rid, c in state.items() if c.get("extra_file")]
    if extras:
        out += ["", "## File để bạn tự upload", *extras]
    old = OdooApi(config.TA_USER).call("hr.applicant", "search_read", OLD_CV_DOMAIN, fields=["id", "name"], limit=3, order="id desc")
    out += ["", "## D17: hồ sơ có CV từ trước khi bật tính năng (`chau.phamminh` mở được)"]
    out += [f"- {o['name']} ({o['id']}): {APP_URL.format(id=o['id'])}" for o in old] or ["- Không còn hồ sơ phù hợp"]
    text = "\n".join(out) + "\n"
    (config.OUTPUT_DIR / "dataset_70538.md").write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
