from pathlib import Path

import pytest

import main

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


def test_good_map() -> None:
    assert main.main([str(MAPS / "simple.cub")]) == 0
