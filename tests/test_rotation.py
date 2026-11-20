import math

import pytest

from cub3d.player import PLANE_LENGTH, Player, rotate_player


def make_north_player() -> Player:
    return Player(3.5, 3.5, 0, -1, PLANE_LENGTH, 0)  # смотрит на север


def test_rotate_90_degrees_right() -> None:
    player = make_north_player()
    rotate_player(player, math.pi / 2)  # положительный угол - вправо: север -> восток
    assert (player.dir_x, player.dir_y) == pytest.approx((1, 0))
    assert (player.plane_x, player.plane_y) == pytest.approx((0, PLANE_LENGTH))


def test_rotate_90_degrees_left() -> None:
    player = make_north_player()
    rotate_player(player, -math.pi / 2)  # север -> запад
    assert (player.dir_x, player.dir_y) == pytest.approx((-1, 0))
    assert (player.plane_x, player.plane_y) == pytest.approx((0, -PLANE_LENGTH))


def test_four_turns_by_90_degrees() -> None:
    player = make_north_player()
    expected = [(1, 0), (0, 1), (-1, 0), (0, -1)]  # восток, юг, запад, север
    for dir_x, dir_y in expected:
        rotate_player(player, math.pi / 2)
        assert (player.dir_x, player.dir_y) == pytest.approx((dir_x, dir_y))


def test_rotate_360_degrees() -> None:
    player = make_north_player()
    for _ in range(36):
        rotate_player(player, math.radians(10))
    assert (player.dir_x, player.dir_y) == pytest.approx((0, -1))
    assert (player.plane_x, player.plane_y) == pytest.approx((PLANE_LENGTH, 0))


def test_rotate_keeps_lengths_and_perpendicular() -> None:
    player = make_north_player()
    for _ in range(100):
        rotate_player(player, 0.37)
    assert math.hypot(player.dir_x, player.dir_y) == pytest.approx(1)
    assert math.hypot(player.plane_x, player.plane_y) == pytest.approx(PLANE_LENGTH)
    assert player.dir_x * player.plane_x + player.dir_y * player.plane_y == pytest.approx(0)


def test_rotate_does_not_move_player() -> None:
    player = make_north_player()
    rotate_player(player, 1.0)
    assert (player.x, player.y) == (3.5, 3.5)
