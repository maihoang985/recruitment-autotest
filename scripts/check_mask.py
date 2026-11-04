"""Kiem tra lai ban CV Masked cua Application da tao (khong mo trinh duyet, khong tao data).
    python scripts/check_mask.py            -> dung id trong output/last_application.txt
    python scripts/check_mask.py 32721
Ket qua: output/mask_check_<id>.txt
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from core import config, mask_check  # noqa: E402

if __name__ == "__main__":
    app_id = int(sys.argv[1]) if len(sys.argv) > 1 else \
        int((config.OUTPUT_DIR / "last_application.txt").read_text().strip())
    problems = mask_check.run(app_id)
    print("PASS" if not problems else "FAIL:\n  " + "\n  ".join(problems))
