import pytest

from cub3d.camera import camera_x, ray_direction
from cub3d.player import make_player
from cub3d.raycast import cast_ray
from cub3d.scene import Scene

WIDTH = 960


def test_straight_wall_stays_straight() -> None:
    """Все столбцы, смотрящие на одну стену, видят одно расстояние: нет «рыбьего глаза»."""
    grid = [
        "11111111111",
        "10000000001",
        "10000000001",
        "10000000001",
        "11111111111",
    ]
    scene = Scene({}, (0, 0, 0), (0, 0, 0), grid, 5, 3, "N")
    player = make_player(scene)
    for column in range(WIDTH):
        ray_x, ray_y = ray_direction(player, camera_x(column, WIDTH))
        hit = cast_ray(scene, player.x, player.y, ray_x, ray_y)
        assert hit.facing == "NO"
        assert hit.distance == pytest.approx(2.5)


def test_straight_wall_facing_east() -> None:
    grid = ["11111"] + ["10001"] * 11 + ["11111"]
    scene = Scene({}, (0, 0, 0), (0, 0, 0), grid, 1, 6, "E")
    player = make_player(scene)
    for column in range(WIDTH):
        ray_x, ray_y = ray_direction(player, camera_x(column, WIDTH))
        hit = cast_ray(scene, player.x, player.y, ray_x, ray_y)
        assert hit.facing == "EA"
        assert hit.distance == pytest.approx(2.5)
