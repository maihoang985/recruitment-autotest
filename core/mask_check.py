"""Kiem tra ban CV Masked cua 1 Application qua API (BR1-BR3, BR5, BR6).
Spec CV (chu phai che / phai giu) luu o output/cv/spec_<app_id>.json luc tao Application,
nen co the kiem tra lai sau (khi ban che chay nen xong): python scripts/check_mask.py <app_id>
"""
import json
import time

from core import config
from core.cv_maker import check_masked
from core.odoo_api import OdooApi

FIELDS = ["cv_mask_state", "cv_mask_error", "cv_masked_attachment_ids", "cv_attachment_ids"]


def spec_path(app_id: int):
    return config.OUTPUT_DIR / "cv" / f"spec_{app_id}.json"


def save_spec(app_id: int, cv: dict):
    spec_path(app_id).write_text(json.dumps(
        {"cv_file": str(cv["path"]), "must_mask": cv["must_mask"], "must_keep": cv["must_keep"]},
        ensure_ascii=False, indent=1), encoding="utf-8")


def wait_mask(api: OdooApi, app_id: int, seconds: int) -> tuple[dict, int]:
    t0 = time.time()
    while True:
        r = api.read_one("hr.applicant", app_id, FIELDS)
        if r["cv_mask_state"] in ("done", "failed") or time.time() - t0 > seconds:
            return r, int(time.time() - t0)
        time.sleep(10)


def verify(api: OdooApi, app_id: int, r: dict) -> list[str]:
    """Tra ve danh sach loi (rong = PASS). Ghi output/mask_check_<id>.txt + luu ban che .pdf."""
    spec = json.loads(spec_path(app_id).read_text(encoding="utf-8"))
    cv_stem = spec["cv_file"].replace("\\", "/").rsplit("/", 1)[-1].rsplit(".", 1)[0]
    problems, report = [], [f"Application id {app_id}", f"CV goc: {cv_stem}.pdf",
                            f"Masked CV Status: {r['cv_mask_state']}  error: {r['cv_mask_error']}"]
    res = {"text": "", "links": []}
    if r["cv_mask_state"] != "done":
        problems.append(f"Ban che chua xong: state={r['cv_mask_state']}, error={r['cv_mask_error']} (BR6)")
    elif len(r["cv_masked_attachment_ids"]) != 1:
        problems.append(f"So file CV Masked = {len(r['cv_masked_attachment_ids'])}, mong doi 1 (BR5)")
    if r["cv_masked_attachment_ids"] and r["cv_mask_state"] == "done":
        name, pdf = api.download(r["cv_masked_attachment_ids"][0])
        (config.OUTPUT_DIR / "cv" / name).write_bytes(pdf)
        report.append(f"CV Masked: {name}  (da luu output/cv/{name})")
        if name != f"{cv_stem}_masked.pdf":
            problems.append(f"Ten file che '{name}', mong doi '{cv_stem}_masked.pdf' (BR5)")
        res = check_masked(pdf, spec)
        problems += [f"CON SOT (copy/doc duoc) {k}: {v}  (BR1/BR5)" for k, v in res["leaked"].items()]
        problems += [f"BI CHE NHAM {k}: {v}  (BR3)" for k, v in res["lost"].items()]
        chat = " ".join(api.chatter("hr.applicant", app_id))
        if "Masked CV created" not in chat and "Đã tạo CV che" not in chat:
            problems.append("Chatter khong co dong 'Masked CV created / Đã tạo CV che' (BR6)")

    report += ["", "KET QUA: " + ("PASS" if not problems else "FAIL")] + problems
    report += ["", "== Chu con lai trong ban che ==", res["text"], "== Link con lai ==", *res["links"]]
    out = config.OUTPUT_DIR / f"mask_check_{app_id}.txt"
    out.write_text("\n".join(report), encoding="utf-8")
    print(f"[MASK] bao cao: {out}")
    return problems


def run(app_id: int, wait_seconds: int = 0) -> list[str]:
    api = OdooApi(config.TA_USER)
    r, waited = wait_mask(api, app_id, wait_seconds)
    print(f"[MASK] app {app_id}: state={r['cv_mask_state']} (cho ~{waited}s)")
    return verify(api, app_id, r)
