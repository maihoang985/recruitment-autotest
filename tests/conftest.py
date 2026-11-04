import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core import config  # noqa: E402
from core.login import login  # noqa: E402


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    return {**browser_type_launch_args, "headless": config.HEADLESS}


@pytest.fixture
def login_as(page):
    """Dung trong test: login_as("ten.tai.khoan")"""
    page.set_default_timeout(config.TIMEOUT_MS)

    def _login(username: str = config.TA_USER, password: str | None = None):
        return login(page, username, password)

    return _login


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Test loi -> ghi man hinh ra output/probe_fail_<ten test>.txt (+ .png).
    Gui file .txt cho Claude doc (re hon anh)."""
    outcome = yield
    rep = outcome.get_result()
    if rep.when == "call" and rep.failed and "page" in item.funcargs:
        try:
            from core.probe import dump_page
            dump_page(item.funcargs["page"], f"fail_{item.name.split('[')[0]}")
        except Exception:
            pass
