import pytest

from cub3d.texture import TEXTURE_SIZE, texture_column, texture_rows


@pytest.mark.parametrize("facing", ["NO", "EA"])
def test_column_is_not_mirrored(facing: str) -> None:
    assert texture_column(0.0, facing) == 0
    assert texture_column(0.5, facing) == 32
    assert texture_column(0.999, facing) == 63


@pytest.mark.parametrize("facing", ["SO", "WE"])
def test_column_is_mirrored(facing: str) -> None:
    assert texture_column(0.0, facing) == 63
    assert texture_column(0.5, facing) == 31
    assert texture_column(0.999, facing) == 0


@pytest.mark.parametrize("facing", ["NO", "SO", "WE", "EA"])
def test_column_stays_inside_texture(facing: str) -> None:
    for step in range(1000):
        column = texture_column(step / 1000, facing)
        assert 0 <= column < TEXTURE_SIZE


def test_all_rows_are_visible_when_wall_is_far() -> None:
    assert texture_rows(300, 600) == (0, 64)
    assert texture_rows(600, 600) == (0, 64)  # стена на расстоянии 1: ровно во весь экран
    assert texture_rows(1, 600) == (0, 64)


def test_only_middle_rows_are_visible_when_wall_is_close() -> None:
    # полоса вдвое выше экрана: видна средняя половина текстуры
    assert texture_rows(1200, 600) == (16, 48)


def test_closer_wall_shows_fewer_rows() -> None:
    first_a, last_a = texture_rows(1200, 600)
    first_b, last_b = texture_rows(2400, 600)
    assert last_b - first_b < last_a - first_a
    assert first_b > first_a


def test_visible_rows_are_symmetric() -> None:
    first, last = texture_rows(1800, 600)
    assert first == TEXTURE_SIZE - last
