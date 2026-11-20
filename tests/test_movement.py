import math

import pytest

from cub3d.movement import MARGIN, MOVE_SPEED, move_player, walk_player
from cub3d.player import PLANE_LENGTH, Player, rotate_player
from cub3d.scene import Scene

ROOM = [
    "1111111",
    "1000001",
    "1000001",
    "1000001",
    "1000001",
    "1000001",
    "1111111",
]


def make_scene() -> Scene:
    return Scene({}, (0, 0, 0), (0, 0, 0), ROOM, 3, 3, "N")


def make_player_at(x: float, y: float) -> Player:
    return Player(x, y, 0, -1, PLANE_LENGTH, 0)  # смотрит на север, справа - восток


def test_walk_forward_and_back() -> None:
    scene = make_scene()
    player = make_player_at(3.5, 3.5)
    walk_player(player, scene, 1, 0, 0.1)
    assert (player.x, player.y) == pytest.approx((3.5, 3.5 - MOVE_SPEED * 0.1))
    walk_player(player, scene, -1, 0, 0.2)
    assert (player.x, player.y) == pytest.approx((3.5, 3.5 + MOVE_SPEED * 0.1))


def test_walk_sideways() -> None:
    scene = make_scene()
    player = make_player_at(3.5, 3.5)
    walk_player(player, scene, 0, 1, 0.1)  # вправо - на восток
    assert (player.x, player.y) == pytest.approx((3.5 + MOVE_SPEED * 0.1, 3.5))
    walk_player(player, scene, 0, -1, 0.2)  # влево - на запад
    assert (player.x, player.y) == pytest.approx((3.5 - MOVE_SPEED * 0.1, 3.5))


def test_walk_follows_direction_of_view() -> None:
    scene = make_scene()
    player = make_player_at(3.5, 3.5)
    rotate_player(player, math.pi / 2)  # теперь смотрит на восток
    walk_player(player, scene, 1, 0, 0.1)
    assert (player.x, player.y) == pytest.approx((3.5 + MOVE_SPEED * 0.1, 3.5))


def test_standing_still() -> None:
    scene = make_scene()
    player = make_player_at(3.5, 3.5)
    walk_player(player, scene, 0, 0, 0.1)
    assert (player.x, player.y) == (3.5, 3.5)


def test_speed_does_not_depend_on_fps() -> None:
    scene = make_scene()
    slow = make_player_at(3.5, 5.5)
    fast = make_player_at(3.5, 5.5)
    for _ in range(30):  # одна секунда при 30 FPS
        walk_player(slow, scene, 1, 0, 1 / 30)
    for _ in range(144):  # одна секунда при 144 FPS
        walk_player(fast, scene, 1, 0, 1 / 144)
    assert slow.y == pytest.approx(5.5 - MOVE_SPEED)
    assert fast.y == pytest.approx(slow.y)


def test_wall_blocks_movement() -> None:
    scene = make_scene()
    player = make_player_at(1.5, 3.5)
    move_player(player, scene, -1.0, 0)  # шаг прямо в стену
    assert (player.x, player.y) == (1.5, 3.5)


def test_player_stops_at_margin_from_wall() -> None:
    scene = make_scene()
    player = make_player_at(3.5, 3.5)
    for _ in range(100):  # идём на запад к стене x = 1 маленькими шагами
        move_player(player, scene, -0.05, 0)
    assert 1.0 + MARGIN - 1e-9 <= player.x <= 1.0 + MARGIN + 0.05 + 1e-9


def test_slide_along_horizontal_wall() -> None:
    scene = make_scene()
    player = make_player_at(3.5, 1.5)
    move_player(player, scene, 0.3, -0.6)  # вправо и вверх, в северную стену
    assert (player.x, player.y) == pytest.approx((3.8, 1.5))  # по x скользим, по y стоим


def test_slide_along_vertical_wall() -> None:
    scene = make_scene()
    player = make_player_at(5.5, 3.5)
    move_player(player, scene, 0.6, 0.3)  # вправо и вниз, в восточную стену
    assert (player.x, player.y) == pytest.approx((5.5, 3.8))  # по y скользим, по x стоим


def test_corner_blocks_both_axes() -> None:
    scene = make_scene()
    player = make_player_at(5.5, 1.5)
    move_player(player, scene, 0.6, -0.6)
    assert (player.x, player.y) == (5.5, 1.5)
