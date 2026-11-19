import math

import pytest

from cub3d.camera import camera_x, ray_direction
from cub3d.player import PLANE_LENGTH, Player


def test_camera_x() -> None:
    assert camera_x(0, 960) == -1
    assert camera_x(480, 960) == 0
    assert camera_x(959, 960) == pytest.approx(1 - 2 / 960)
    assert camera_x(2, 8) == -0.5
    assert camera_x(6, 8) == 0.5


def test_center_ray_is_direction() -> None:
    player = Player(4.5, 3.5, 0, -1, PLANE_LENGTH, 0)  # смотрит на север
    assert ray_direction(player, 0) == (0, -1)


def test_edge_rays_facing_north() -> None:
    player = Player(4.5, 3.5, 0, -1, PLANE_LENGTH, 0)
    assert ray_direction(player, -1) == pytest.approx((-PLANE_LENGTH, -1))  # слева - запад
    assert ray_direction(player, 1) == pytest.approx((PLANE_LENGTH, -1))  # справа - восток


def test_edge_rays_facing_east() -> None:
    player = Player(4.5, 3.5, 1, 0, 0, PLANE_LENGTH)
    assert ray_direction(player, -1) == pytest.approx((1, -PLANE_LENGTH))  # слева - север
    assert ray_direction(player, 1) == pytest.approx((1, PLANE_LENGTH))  # справа - юг


def test_edge_rays_make_fov() -> None:
    player = Player(4.5, 3.5, 0, 1, -PLANE_LENGTH, 0)  # смотрит на юг
    left_x, left_y = ray_direction(player, -1)
    right_x, right_y = ray_direction(player, 1)
    length = left_x**2 + left_y**2  # у крайних лучей длины одинаковые
    cosine = (left_x * right_x + left_y * right_y) / length
    assert math.degrees(math.acos(cosine)) == pytest.approx(66)
