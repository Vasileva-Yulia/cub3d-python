from pathlib import Path

import pytest

import main
from cub3d.scene import Scene

MAPS = Path(__file__).resolve().parent.parent / "maps"


def test_no_arguments() -> None:
    with pytest.raises(SystemExit) as info:
        main.main([])
    assert info.value.code == 2


def test_bad_window_size() -> None:
    with pytest.raises(SystemExit) as info:
        main.main([str(MAPS / "simple.cub"), "--width", "0"])
    assert info.value.code == 2


@pytest.mark.parametrize("name", ["bad/open_space.cub", "bad/missing_texture.cub", "nope.cub"])
def test_errors(name: str, capsys: pytest.CaptureFixture[str]) -> None:
    assert main.main([str(MAPS / name)]) == 1
    err = capsys.readouterr().err
    assert err.startswith("Error\n")
    assert "Traceback" not in err


def test_good_map(monkeypatch: pytest.MonkeyPatch) -> None:
    sizes: list[tuple[int, int]] = []

    def fake_window(scene: Scene, width: int, height: int) -> None:
        sizes.append((width, height))

    monkeypatch.setattr(main, "run_window", fake_window)  # окно в тестах не открываем
    assert main.main([str(MAPS / "simple.cub")]) == 0
    assert sizes == [(960, 600)]


def test_window_size_from_arguments(monkeypatch: pytest.MonkeyPatch) -> None:
    sizes: list[tuple[int, int]] = []

    def fake_window(scene: Scene, width: int, height: int) -> None:
        sizes.append((width, height))

    monkeypatch.setattr(main, "run_window", fake_window)
    assert main.main([str(MAPS / "simple.cub"), "--width", "640", "--height", "400"]) == 0
    assert sizes == [(640, 400)]
