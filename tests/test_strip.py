import pytest

from cub3d.raycast import strip_height


@pytest.mark.parametrize(
    ("distance", "expected"),
    [
        (1, 600),  # на расстоянии 1 стена занимает весь экран
        (2, 300),  # на расстоянии 2 - половину
        (4, 150),
        (2.5, 240),
        (0.5, 1200),  # ближе одной клетки полоса выше экрана
    ],
)
def test_strip_height(distance: float, expected: int) -> None:
    assert strip_height(distance, 600) == expected


def test_strip_height_at_zero_distance() -> None:
    assert strip_height(0, 600) > 600  # деления на ноль нет


def test_strip_height_is_at_least_one() -> None:
    assert strip_height(100000, 600) == 1
