"""Tao CV mau cho test Masking (#73087) + danh sach chu PHAI bi che / PHAI giu (BR1-BR3).

CV co bo cuc nhu CV that (dai ten + anh dai dien, cac muc lien he, hoc van, kinh nghiem, ky nang).
Ma mau + dinh dang chi ghi nho o chan trang; ten file bat dau bang ma mau (CV01_...).
Noi dung ung vien lay tu data/application/candidates.json qua pages.application_page.app_data(candidate=...).

    cv = make_cv("png", out_dir, candidate, stem="CV_Kiem")
    cv["files"]      -> danh sach file can upload (multi = 2 file)
    cv["must_mask"]  -> SDT, email, dia chi, link mang xa hoi (ke ca link an)
    cv["must_keep"]  -> ho ten, nam sinh, hoc van, kinh nghiem, portfolio

Cac kieu (KINDS): pdf_text, pdf_scan, png, jpg, docx, broken_cut, broken_fake, multi, vjp, reupload.
"""
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape

import pymupdf

# Segoe UI: co dau tieng Viet VA trich chu ra dung dau cach. Arial/Tahoma/Times trich dau cach thanh \xa0
# -> cong cu che (va bo kiem tra) co the doc sai SDT -> bao bug oan.
# Khong dung '-' (trich thanh U+2010) va '( )' (trich thanh U+FD3E/FD3F) trong noi dung.
FONT = r"C:\Windows\Fonts\segoeui.ttf"
FONT_BOLD = r"C:\Windows\Fonts\segoeuib.ttf"
MAX_BYTES = 800 * 1024  # SRS o S46: CV <= 800KB

# kind -> (ma mau, dinh dang ghi tren bang, ky vong ghi tren bang, mau bang RGB 0..1, duoi file)
KINDS = {
    "pdf_text":    ("CV01", "PDF CÓ CHỮ", "Kỳ vọng: phải che, chữ bị xóa hẳn, copy không ra", (0.10, 0.35, 0.75), ".pdf"),
    "pdf_scan":    ("CV02", "PDF SCAN", "Kỳ vọng: phải che bằng OCR, vùng liên hệ bị tô đen", (0.45, 0.25, 0.65), ".pdf"),
    "png":         ("CV03", "ẢNH PNG", "Kỳ vọng: phải che bằng OCR, vùng liên hệ bị tô đen", (0.05, 0.50, 0.45), ".png"),
    "jpg":         ("CV04", "ẢNH JPG", "Kỳ vọng: phải che bằng OCR, vùng liên hệ bị tô đen", (0.15, 0.55, 0.20), ".jpg"),
    "docx":        ("CV05", "FILE WORD DOCX", "Kỳ vọng: CHƯA RÕ, che được hay báo E_004. Hỏi BA", (0.10, 0.30, 0.55), ".docx"),
    "broken_cut":  ("CV06A", "FILE HỎNG: NỘI DUNG LỖI", "Kỳ vọng: báo E_005, không tạo bản che", (0.70, 0.15, 0.15), ".pdf"),
    "broken_fake": ("CV06B", "FILE HỎNG: ĐỔI ĐUÔI", "Kỳ vọng: báo E_005, không tạo bản che", (0.70, 0.15, 0.15), ".pdf"),
    "multi":       ("CV07", "NHIỀU FILE", "Kỳ vọng: mỗi file có một bản _masked.pdf riêng", (0.80, 0.45, 0.05), ".pdf"),
    "vjp":         ("CV08", "PDF CÓ CHỮ · SOURCE VJP", "Kỳ vọng: KHÔNG tạo bản che vì Source thuộc VJP", (0.35, 0.35, 0.35), ".pdf"),
    "reupload":    ("CV09", "UPLOAD LẠI LẦN 2", "Kỳ vọng: tạo lại bản che theo file mới này", (0.60, 0.20, 0.50), ".pdf"),
    "pdf_limits":  ("CV10", "PDF GIỚI HẠN BR12", "Kỳ vọng: địa chỉ không nhãn và ảnh chèn có thể sót, chỉ ghi nhận", (0.45, 0.40, 0.10), ".pdf"),
    "replace_masked": ("CV11", "FILE THAY CV MASKED", "Dùng để REC User thay tay ô CV Masked", (0.30, 0.30, 0.55), ".pdf"),
}


def _norm(s: str) -> str:
    return " ".join(s.replace("\xa0", " ").split())


def label_of(kind: str, part: str = "") -> tuple[str, str]:
    code, fmt, expect, _, _ = KINDS[kind]
    return f"{code} · {fmt}{part}", expect


# ---------------------------------------------------------------- noi dung CV
# Thu tu in cac loai lien he trong CV. Khoa 'linkedin_an' = link AN gan tren chu (khong hien URL).
CONTACT_LABELS = {
    "phone": "Điện thoại", "phone_intl": "Phone international", "email": "Email", "facebook": "Facebook",
    "zalo": "Zalo", "github": "GitHub", "gitlab": "GitLab", "skype": "Skype", "instagram": "Instagram",
    "tiktok": "TikTok", "telegram": "Telegram", "twitter": "Twitter", "linkedin": "LinkedIn",
}
HIDDEN_KEY = "linkedin_an"
HIDDEN_LINK_TEXT = "LinkedIn profile, bấm để xem"
DEFAULT_EXPERIENCE = ["2020 đến nay: Kiểm thử phần mềm, Manual testing Web",
                      "• Viết test case, thực hiện kiểm thử chức năng và hồi quy",
                      "• Báo cáo lỗi trên Redmine, phối hợp với đội phát triển"]
DEFAULT_SKILLS = "Manual testing, SQL cơ bản, Postman, Playwright"


def _norm_cv(c: dict) -> dict:
    """Chap nhan 2 dang: moi (co 'contacts', tu data/application/candidates.json) va cu (phone, email, github, linkedin)."""
    if "contacts" in c:
        contacts = dict(c["contacts"])
    else:
        contacts = {k: c[k] for k in ("phone", "phone_intl", "email", "github") if c.get(k)}
        if c.get("linkedin"):
            contacts[HIDDEN_KEY] = c["linkedin"]
    return {**c, "contacts": contacts, "title": c.get("title") or "Tester / QA Engineer",
            "experience": c.get("experience") or DEFAULT_EXPERIENCE, "skills": c.get("skills") or DEFAULT_SKILLS}


def _blocks(c: dict) -> list[tuple]:
    """Noi dung CV dang khoi: (loai, ...). Dung chung cho PDF, anh, Word."""
    ct = c["contacts"]
    b = [("name", c["full_name"].upper()), ("title", c["title"]), ("section", "THÔNG TIN LIÊN HỆ"),
         ("kv", "Năm sinh", str(c["dob"]))]
    if c.get("address_lines"):  # nhieu dong dia chi (BR2): co label = dong co nhan, khong label = chi co tu khoa
        b += [("kv", a["label"], a["value"]) if a.get("label") else ("line", a["value"]) for a in c["address_lines"]]
    else:
        b.append(("kv", "Địa chỉ", c["address"]))
    b += [("kv", lab, ct[k]) for k, lab in CONTACT_LABELS.items() if k in ct]
    if HIDDEN_KEY in ct:
        b.append(("hidden", HIDDEN_LINK_TEXT, ct[HIDDEN_KEY]))
    b.append(("kv", "Portfolio", c["portfolio"]))
    y = int(c["dob"]) if str(c["dob"]).isdigit() else 2000
    b += [("section", "HỌC VẤN"), ("line", f"{y + 18} – {y + 22}: {c['university']}"),
          ("section", "KINH NGHIỆM LÀM VIỆC")]
    b += [("bullet" if s.startswith("•") else "job", s) for s in c["experience"]]
    b += [("section", "KỸ NĂNG"), ("line", c["skills"])]
    if c.get("image_lines"):  # BR12: thong tin lien he nam trong anh chen tren PDF co chu
        b.append(("image_text", c["image_lines"]))
    return b


def _spec(c: dict) -> dict:
    c = _norm_cv(c)
    must_mask = {("linkedin_hidden" if k == HIDDEN_KEY else k): v for k, v in c["contacts"].items()}
    if c.get("address_lines"):  # dong khong co 'key' (BR12) khong dua vao danh sach phai che
        must_mask.update({f"address_{i}": a["key"] for i, a in enumerate(c["address_lines"], 1) if a.get("key")})
    else:
        must_mask["address"] = c["address_key"]
    job = c["experience"][0]
    role = (job.split(":", 1)[-1]).split(",")[0].strip()
    return {
        "must_mask": must_mask,
        "must_keep": {"full_name": c["full_name"].upper(), "dob": str(c["dob"]), "university": c["university"],
                      "portfolio": c["portfolio"], "experience": role},
    }


def _portrait_png(color: tuple) -> bytes:
    """Anh chan dung gia lap (BR3: anh chan dung khong duoc che)."""
    doc = pymupdf.open()
    page = doc.new_page(width=160, height=160)
    page.draw_rect(page.rect, color=None, fill=(0.88, 0.91, 0.95))
    page.draw_oval(pymupdf.Rect(26, 104, 134, 210), color=None, fill=color)
    page.draw_circle((80, 62), 32, color=None, fill=(0.93, 0.76, 0.62))
    png = page.get_pixmap(dpi=144).tobytes("png")
    doc.close()
    return png


def _text_image_png(lines: list[str]) -> bytes:
    """Anh chua chu lien he, de chen vao PDF co chu (BR12)."""
    doc = pymupdf.open()
    page = doc.new_page(width=320, height=70)
    page.draw_rect(page.rect, color=(0.6, 0.6, 0.6), fill=(0.96, 0.96, 0.90))
    for i, s in enumerate(lines):
        page.insert_text((10, 26 + i * 24), s, fontsize=13, fontname="F0", fontfile=FONT)
    png = page.get_pixmap(dpi=200).tobytes("png")
    doc.close()
    return png


def _pdf_doc(c: dict, kind: str, part: str = "") -> tuple[pymupdf.Document, list[str]]:
    """Trang A4 giong CV that: dai mau co anh dai dien + ten + chuc danh, cac muc lien he, hoc van, kinh nghiem, ky nang.
    Ma mau + dinh dang chi ghi nho o chan trang."""
    c = _norm_cv(c)
    title, _ = label_of(kind, part)
    color = KINDS[kind][3]
    doc = pymupdf.open()
    page = doc.new_page()  # A4 595x842
    written = []
    fonts = {False: pymupdf.Font(fontfile=FONT), True: pymupdf.Font(fontfile=FONT_BOLD)}
    X, W = 50, 495

    def text(x, y, s, size=11, bold=False, col=(0, 0, 0), maxw=None, record=True):
        if any(ch in s for ch in "-()"):
            raise ValueError(f"CV mau khong dung '-' hay '( )' (font trich sai): {s}")
        while maxw and size > 8 and fonts[bold].text_length(s, fontsize=size) > maxw:
            size -= 0.5  # dong dai (dia chi) -> thu nho cho vua mot dong, khong ngat dong
        page.insert_text((x, y), s, fontsize=size, fontname="F1" if bold else "F0",
                         fontfile=FONT_BOLD if bold else FONT, color=col)
        if record:
            written.append(s)
        return fonts[bold].text_length(s, fontsize=size)

    # Dai dau trang: anh chan dung, ten, chuc danh
    page.draw_rect(pymupdf.Rect(0, 0, 595, 130), color=None, fill=color)
    page.insert_image(pymupdf.Rect(38, 25, 118, 105), stream=_portrait_png(color))
    blocks = _blocks(c)
    step = 19 if len(blocks) <= 26 else 15  # CV nhieu dong (bo A) van nam gon 1 trang
    text(140, 66, blocks[0][1], 22, True, (1, 1, 1), maxw=410)
    text(140, 94, blocks[1][1], 13, False, (1, 1, 1), maxw=410)

    y = 168
    for kind_, *rest in blocks[2:]:
        if kind_ == "section":
            if y > 170:
                y += 8
            text(X, y, rest[0], 12, True, color)
            page.draw_line((X, y + 5), (X + W, y + 5), color=color, width=0.8)
            y += 24
        elif kind_ == "kv":
            lab = rest[0] + ":"
            lw = text(X, y, lab, 11, True)
            text(X + lw + 6, y, rest[1], 11, False, maxw=W - lw - 6)
            y += step
        elif kind_ == "hidden":  # link an: chu hien thi khong chua URL, URL gan vao chu (BR1)
            text(X, y, rest[0])
            page.insert_link({"kind": pymupdf.LINK_URI, "uri": rest[1], "from": pymupdf.Rect(X, y - 12, X + 210, y + 4)})
            y += step
        elif kind_ == "job":
            text(X, y, rest[0], 11, True, maxw=W)
            y += step
        elif kind_ == "bullet":
            text(X + 8, y, rest[0], 11, maxw=W - 8)
            y += step
        elif kind_ == "image_text":
            page.insert_image(pymupdf.Rect(X, y, X + 320, y + 70), stream=_text_image_png(rest[0]))
            y += 76
        else:  # line
            text(X, y, rest[0], 11, maxw=W)
            y += step
    if y > 815:
        raise AssertionError(f"CV mau tran trang (y={y}): bot noi dung hoac giam gian dong")

    # Chan trang: ma mau (nho, de nhan biet khi show)
    text(X, 825, f"Mẫu kiểm thử Masking #73087 · {title}", 8, False, (0.55, 0.55, 0.55))
    return doc, written


def _save_pdf(doc: pymupdf.Document, path: Path, written: list[str] | None = None):
    path.parent.mkdir(parents=True, exist_ok=True)
    doc.subset_fonts()  # chi nhung ky tu dung -> file nho
    doc.save(str(path), garbage=4, deflate=True)
    doc.close()
    if written:  # Tu kiem tra: chu trich tu file phai khop dung tung dong da viet
        with pymupdf.open(str(path)) as check:
            got = check[0].get_text()
        bad = [t for t in written if _norm(t) not in _norm(got)]
        if bad or "\xa0" in got:
            raise AssertionError(f"CV mau trich chu sai (font?): {bad[:3] or repr(got[:120])}")


def _pixmap(c: dict, kind: str, part: str = "", dpi: int = 150, gray: bool = False) -> pymupdf.Pixmap:
    doc, _ = _pdf_doc(c, kind, part)
    pix = doc[0].get_pixmap(dpi=dpi, colorspace=pymupdf.csGRAY if gray else pymupdf.csRGB)
    doc.close()
    return pix


# ---------------------------------------------------------------- tung dinh dang
def _make_pdf_text(path: Path, c: dict, kind: str, part: str = ""):
    doc, written = _pdf_doc(c, kind, part)
    _save_pdf(doc, path, written)


def _make_pdf_scan(path: Path, c: dict, kind: str):
    """PDF chi chua anh (khong co lop chu) -> gia lap CV scan, he thong phai OCR moi che duoc."""
    img = _pixmap(c, kind, dpi=200, gray=True).tobytes("jpg", jpg_quality=70)
    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_image(page.rect, stream=img)
    _save_pdf(doc, path)
    with pymupdf.open(str(path)) as check:
        if check[0].get_text().strip():
            raise AssertionError("PDF scan van con lop chu")


def _make_image(path: Path, c: dict, kind: str, part: str = ""):
    pix = _pixmap(c, kind, part, dpi=150)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix == ".png":
        path.write_bytes(pix.tobytes("png"))
    else:
        path.write_bytes(pix.tobytes("jpg", jpg_quality=85))


def _make_docx(path: Path, c: dict, kind: str):
    """Word toi gian (khong can thu vien): dai ten to nen, cac muc nhu CV that, link an gan tren chu."""
    c = _norm_cv(c)
    title, _ = label_of(kind)
    hexcol = "".join(f"{int(v * 255):02X}" for v in KINDS[kind][3])

    def run(s, size=22, bold=False, color=None):
        props = f'<w:sz w:val="{size}"/>' + ("<w:b/>" if bold else "") + (f'<w:color w:val="{color}"/>' if color else "")
        return f'<w:r><w:rPr><w:rFonts w:ascii="Segoe UI" w:hAnsi="Segoe UI"/>{props}</w:rPr><w:t xml:space="preserve">{escape(s)}</w:t></w:r>'

    def para(inner, shade=False):
        ppr = f'<w:pPr><w:shd w:val="clear" w:color="auto" w:fill="{hexcol}"/></w:pPr>' if shade else ""
        return f"<w:p>{ppr}{inner}</w:p>"

    body = []
    for kind_, *rest in _blocks(c):
        if kind_ == "name":
            body.append(para(run(rest[0], 44, True, "FFFFFF"), True))
        elif kind_ == "title":
            body.append(para(run(rest[0], 26, False, "FFFFFF"), True))
        elif kind_ == "section":
            body.append(para(run(rest[0], 24, True, hexcol)))
        elif kind_ == "kv":
            body.append(para(run(rest[0] + ": ", 22, True) + run(rest[1])))
        elif kind_ == "hidden":
            body.append(para(f'<w:hyperlink r:id="rIdLink">{run(rest[0])}</w:hyperlink>'))
        elif kind_ == "job":
            body.append(para(run(rest[0], 22, True)))
        else:
            body.append(para(run(rest[0])))
    body.append(para(run(f"Mẫu kiểm thử Masking #73087 · {title}", 16, False, "888888")))
    link = c["contacts"].get(HIDDEN_KEY, "https://example.com")

    ns = ('xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
          'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"')
    document = f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:document {ns}><w:body>{"".join(body)}</w:body></w:document>'
    rel_t = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
    files = {
        "[Content_Types].xml": '<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
            '<Default Extension="xml" ContentType="application/xml"/>'
            '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/></Types>',
        "_rels/.rels": f'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            f'<Relationship Id="rId1" Type="{rel_t}/officeDocument" Target="word/document.xml"/></Relationships>',
        "word/_rels/document.xml.rels": f'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            f'<Relationship Id="rIdLink" Type="{rel_t}/hyperlink" Target="{escape(link)}" TargetMode="External"/></Relationships>',
        "word/document.xml": document,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for name, data in files.items():
            z.writestr(name, data)


def _make_broken_cut(path: Path, c: dict):
    """PDF hong: giu phan dau '%PDF' cua file that, phan than thay bang byte rac.
    (Chi cat file thi MuPDF tu sua va van mo duoc -> khong ra E_005.)"""
    import random
    tmp = path.with_suffix(".tmp.pdf")
    _make_pdf_text(tmp, c, "broken_cut")
    data = tmp.read_bytes()
    tmp.unlink()
    rnd = random.Random(73087)
    path.write_bytes(data[:15] + bytes(rnd.randrange(256) for _ in range(len(data) // 3)))
    try:
        with pymupdf.open(str(path)) as d:
            if d.page_count and d[0].get_text().strip():
                raise AssertionError("File hong van doc duoc chu")
    except AssertionError:
        raise
    except Exception:
        pass  # mo khong duoc = dung y do


def _make_broken_fake(path: Path, c: dict):
    """File chu thuong bi doi duoi thanh .pdf. Mo bang Notepad se thay nhan mau."""
    title, expect = label_of("broken_fake")
    path.write_text(f"MẪU {title}\n{expect}\n\nĐây là file văn bản thường bị đổi đuôi thành .pdf, "
                    f"không phải PDF thật.\nĐiện thoại: {_norm_cv(c)['contacts'].get('phone', '')}\nEmail: {_norm_cv(c)['contacts'].get('email', '')}\n", encoding="utf-8")


# ---------------------------------------------------------------- ham chinh
def make_cv(kind: str, out_dir: Path, c: dict, stem: str = "CV") -> dict:
    """Sinh CV kieu `kind` vao out_dir. Ten file: <ma mau>_<stem><duoi>.
    Tra ve {kind, code, files: [Path], must_mask, must_keep, expect}."""
    if kind not in KINDS:
        raise ValueError(f"Kieu CV khong co: {kind}. Chon 1 trong {list(KINDS)}")
    code, _, expect, _, ext = KINDS[kind]
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{code}_{stem}{ext}"
    files = [path]

    if kind in ("pdf_text", "vjp", "reupload", "pdf_limits", "replace_masked"):
        _make_pdf_text(path, c, kind)
    elif kind == "pdf_scan":
        _make_pdf_scan(path, c, kind)
    elif kind in ("png", "jpg"):
        _make_image(path, c, kind)
    elif kind == "docx":
        _make_docx(path, c, kind)
    elif kind == "broken_cut":
        _make_broken_cut(path, c)
    elif kind == "broken_fake":
        _make_broken_fake(path, c)
    elif kind == "multi":  # file 1 PDF co chu, file 2 anh PNG
        files = [out_dir / f"{code}_{stem}_file1.pdf", out_dir / f"{code}_{stem}_file2.png"]
        _make_pdf_text(files[0], c, kind, " · FILE 1 / 2")
        _make_image(files[1], c, kind, " · FILE 2 / 2")

    for f in files:
        size = f.stat().st_size
        if size > MAX_BYTES:
            raise AssertionError(f"{f.name} nang {size // 1024}KB > 800KB (SRS o S46)")
    return {"kind": kind, "code": code, "files": files, "path": files[0], "expect": expect, **_spec(c)}


def make_text_cv(path: Path, c: dict) -> dict:
    """Giu cho code cu: CV01 PDF co chu, luu dung `path`."""
    _make_pdf_text(path, c, "pdf_text")
    return {"kind": "pdf_text", "code": "CV01", "files": [path], "path": path, **_spec(c)}


def check_masked(pdf_bytes: bytes, cv: dict) -> dict:
    """Doc chu + link con lai trong ban che. Tra ve {'leaked': {...}, 'lost': {...}, 'text': ...}.
    'leaked' = chu phai che ma van copy duoc (vi pham BR5); 'lost' = chu phai giu ma bi che (BR3).
    Chi dung cho CV PDF co chu. Anh/scan: kiem tra bang mat."""
    doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
    text = "\n".join(p.get_text() for p in doc)
    links = [l.get("uri", "") for p in doc for l in p.get_links()]
    doc.close()
    flat = _norm(text)
    digits = "".join(ch for ch in flat if ch.isdigit())

    def present(v: str) -> bool:
        if v in flat or v in links:
            return True
        d = "".join(ch for ch in v if ch.isdigit())
        return len(d) >= 9 and d in digits  # SDT co the bi tach dau cach

    leaked = {k: v for k, v in cv["must_mask"].items() if present(v)}
    lost = {k: v for k, v in cv["must_keep"].items() if v not in flat}
    return {"leaked": leaked, "lost": lost, "text": text, "links": links}
