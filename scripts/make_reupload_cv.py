"""Sinh CV "cap nhat" de TU upload lan 2 len ho so da co (kiem tra: ban che tao lai theo file moi).
Cung ung vien, cung ho ten/nam sinh, nhung DOI dia chi, SDT, email, link, kinh nghiem
-> mo ban masked moi la biet ngay no duoc tao lai tu file moi hay con la ban cu.

    python scripts/make_reupload_cv.py            -> ung vien CV01 (Tran Minh Quan, ho so 32726)
    python scripts/make_reupload_cv.py CV02       -> ung vien khac

Ket qua trong data/cv_samples/: file CV09_cap_nhat_<ma>.pdf + CV09_cap_nhat_<ma>_PHAI_CHE.md (danh sach phai che / phai giu)
Khong tao ho so, khong upload, khong sua gi tren STG.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core import config  # noqa: E402
from core.cv_maker import make_cv  # noqa: E402
from pages.application_page import app_data  # noqa: E402

NEW_ADDRESS = ("Số 18 Ngõ 52 Phố Kim Mã, Phường Ngọc Khánh, Quận Ba Đình, Hà Nội", "Ngõ 52 Phố Kim Mã")


def main(code: str):
    d = app_data(candidate=code)  # SDT, email, link: tag/so ngau nhien moi -> khac CV lan 1
    cv_data = {**d["cv"], "address": NEW_ADDRESS[0], "address_key": NEW_ADDRESS[1]}
    cv_data["experience"] = ["2024 đến nay: Trưởng nhóm kiểm thử, Công ty Công nghệ Tương Lai",
                             "• Quản lý nhóm 5 kiểm thử viên và lập kế hoạch kiểm thử",
                             "• Xây dựng bộ kiểm thử tự động cho hệ thống bán hàng"] + cv_data["experience"]
    out = config.CV_SAMPLES_DIR
    out.mkdir(parents=True, exist_ok=True)
    cv = make_cv("reupload", out, cv_data, stem=f"cap_nhat_{code}")
    f = cv["path"]

    lines = [f"# CV cập nhật để upload lần 2 · {d['last_name']} {d['first_name']} ({code})", "",
             f"File: `{f.name}`", "",
             "Upload vào ô **CV Attachment** của hồ sơ đã có CV lần 1. Sau khi bản Masked mới tạo xong, kiểm tra:", "",
             "## PHẢI BỊ CHE (thông tin liên hệ mới, khác CV lần 1)"]
    lines += [f"- {k}: `{v}`" for k, v in cv["must_mask"].items()]
    lines += ["", "## PHẢI CÒN NGUYÊN"]
    lines += [f"- {k}: `{v}`" for k, v in cv["must_keep"].items()]
    lines += ["", "## Dấu hiệu bản Masked đã tạo lại theo file mới",
              f"- Địa chỉ mới `{NEW_ADDRESS[1]}` bị che, địa chỉ cũ không còn trong file.",
              "- Có dòng kinh nghiệm mới \"Trưởng nhóm kiểm thử\" (CV lần 1 không có).",
              "- Chatter có thêm một dòng \"Masked CV created\" mới."]
    md = f.with_name(f.stem + "_PHAI_CHE.md")
    md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"File CV : {f}  ({f.stat().st_size // 1024}KB)\nDanh sách: {md}\n")
    print("\n".join(lines[8:]))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "CV01")
