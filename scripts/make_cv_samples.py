"""Sinh tron bo CV mau (moi kieu 1 file) vao data/cv_samples/ de xem truoc / show cho khach.

Chay: .\\.venv\\Scripts\\python.exe scripts/make_cv_samples.py
Ket qua: data/cv_samples/CV01_... -> CV09_..., kem DANH_SACH.md (ma mau, dinh dang, ky vong).

Luu y: khi chay test, CV duoc sinh MOI moi lan (SDT/email khac nhau de khong bi bao trung ung vien).
Bo nay chi de xem; noi dung giong het ban test se upload, chi khac SDT/email.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core import config  # noqa: E402
from core.cv_maker import KINDS, make_cv  # noqa: E402
from pages.application_page import app_data  # noqa: E402


def main():
    out = config.CV_SAMPLES_DIR
    out.mkdir(parents=True, exist_ok=True)
    for old in out.glob("CV0*"):
        old.unlink()
    rows = ["| Mã | Định dạng | File | Kỳ vọng |", "|---|---|---|---|"]
    for kind, (code, fmt, expect, _, _) in KINDS.items():
        d = app_data(candidate=code)
        cv = make_cv(kind, out, d["cv"], stem="mau")
        names = ", ".join(f"{f.name} ({f.stat().st_size // 1024}KB)" for f in cv["files"])
        rows.append(f"| {code} | {fmt} | {names} | {expect.replace('Kỳ vọng: ', '')} |")
        print(f"{code:<6} {fmt:<26} {names}")
    (out / "DANH_SACH.md").write_text(
        "# Bộ CV mẫu test Masking #73087\n\n"
        f"SĐT/email trong bộ này: `{d['cv']['phone']}`, `{d['cv']['email']}` (khi chạy test sẽ sinh số mới).\n\n"
        + "\n".join(rows) + "\n", encoding="utf-8")
    print(f"\nDa sinh vao {out}")


if __name__ == "__main__":
    main()
