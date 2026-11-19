import pytest

from cub3d.raycast import strip_height, wall_strip


@pytest.mark.parametrize(
    ("distance", "expected"),
    [
        (1, 600),  # на расстоянии 1 стена занимает весь экран
        (2, 300),  # на расстоянии 2 - половину
        (4, 150),
        (2.5, 240),
    ],
)
def test_strip_height(distance: float, expected: int) -> None:
    assert strip_height(distance, 600) == expected


def test_wall_strip_is_centered() -> None:
    assert wall_strip(2, 600) == (150, 450)
    assert wall_strip(4, 600) == (225, 375)


def test_wall_strip_is_cut_by_screen() -> None:
    assert wall_strip(0.5, 600) == (0, 600)  # стена ближе одной клетки выше экрана


def test_wall_strip_at_zero_distance() -> None:
    assert wall_strip(0, 600) == (0, 600)  # деления на ноль нет
