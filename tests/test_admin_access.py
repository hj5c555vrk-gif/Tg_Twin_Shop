import importlib
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def test_admin_ids_accept_username_and_numeric_values(monkeypatch):
    monkeypatch.setenv("ADMIN_ID", "6593118456")
    monkeypatch.setenv("ADMIN_IDS", "@Twinstore_Manager,12345")

    sys.modules.pop("bot.database.admin", None)
    admin_module = importlib.import_module("bot.database.admin")
    importlib.reload(admin_module)

    assert admin_module.is_admin_user(12345)
    assert admin_module.is_admin_user(6593118456)
    assert admin_module.is_admin_user(999, username="Twinstore_Manager")
    assert not admin_module.is_admin_user(777, username="someone_else")
