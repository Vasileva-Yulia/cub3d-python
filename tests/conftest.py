from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def _project_root_cwd(monkeypatch: pytest.MonkeyPatch) -> None:
    """Пути текстур в картах заданы от корня проекта, поэтому тесты идут из него."""
    monkeypatch.chdir(Path(__file__).resolve().parent.parent)
