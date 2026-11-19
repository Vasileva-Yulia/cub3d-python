from pathlib import Path

import pytest

from cub3d.parser import parse_scene
from cub3d.player import FOV, PLANE_LENGTH, make_player
from cub3d.scene import Scene

MAPS = Path(__file__).resolve().parent.parent / "maps"


def test_fov() -> None:
    assert FOV == 66
    assert PLANE_LENGTH == pytest.approx(0.65, abs=0.01)


def test_player_in_cell_center() -> None:
    scene = parse_scene(MAPS / "simple.cub")  # игрок в клетке (4, 3)
    player = make_player(scene)
    assert (player.x, player.y) == (4.5, 3.5)


@pytest.mark.parametrize(
    ("direction", "dir_x", "dir_y", "plane_x", "plane_y"),
    [
        ("N", 0, -1, 1, 0),
        ("E", 1, 0, 0, 1),
        ("S", 0, 1, -1, 0),
        ("W", -1, 0, 0, -1),
    ],
)
def test_direction_and_plane(
    direction: str, dir_x: int, dir_y: int, plane_x: int, plane_y: int
) -> None:
    scene = Scene({}, (0, 0, 0), (0, 0, 0), ["111", "101", "111"], 1, 1, direction)
    player = make_player(scene)
    assert (player.dir_x, player.dir_y) == (dir_x, dir_y)
    # plane - это dir, повёрнутый на 90° вправо
    assert player.plane_x == pytest.approx(plane_x * PLANE_LENGTH)
    assert player.plane_y == pytest.approx(plane_y * PLANE_LENGTH)
