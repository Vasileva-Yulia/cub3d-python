from pathlib import Path

import pytest

from cub3d.errors import CubError, RaycastError
from cub3d.parser import parse_scene
from cub3d.raycast import cast_ray, wall_facing
from cub3d.scene import Scene

MAPS = Path(__file__).resolve().parent.parent / "maps"


def make_scene(grid: list[str]) -> Scene:
    """Сцена из строк карты без файла: текстуры и цвета не нужны."""
    return Scene({}, (0, 0, 0), (0, 0, 0), grid, 1, 1, "N")


@pytest.mark.parametrize(
    ("side", "ray_x", "ray_y", "expected"),
    [
        (0, 1.0, 0.3, "EA"),
        (0, -1.0, 0.3, "WE"),
        (1, 0.2, 1.0, "SO"),
        (1, 0.2, -1.0, "NO"),
    ],
)
def test_wall_facing(side: int, ray_x: float, ray_y: float, expected: str) -> None:
    assert wall_facing(side, ray_x, ray_y) == expected


def test_ray_from_the_assignment() -> None:
    # рис. 4: луч (1, -0,5) из точки (0,7; 2,6) попадает в клетку (4, 0)
    scene = make_scene(["000010", "000000", "000000", "000000"])
    hit = cast_ray(scene, 0.7, 2.6, 1.0, -0.5)
    assert (hit.map_x, hit.map_y) == (4, 0)
    assert hit.side == 0
    assert hit.distance == pytest.approx(3.3)
    assert hit.wall_x == pytest.approx(0.95)
    assert hit.facing == "EA"


@pytest.mark.parametrize(
    ("ray_x", "ray_y", "cell", "side", "distance", "facing"),
    [
        (0, -1, (4, 0), 1, 2.5, "NO"),
        (1, 0, (7, 3), 0, 2.5, "EA"),
        (-1, 0, (0, 3), 0, 3.5, "WE"),
        (0, 1, (4, 7), 1, 3.5, "SO"),
    ],
)
def test_rays_along_axes(
    ray_x: int, ray_y: int, cell: tuple[int, int], side: int, distance: float, facing: str
) -> None:
    scene = parse_scene(MAPS / "simple.cub")  # игрок в клетке (4, 3), то есть в точке (4,5; 3,5)
    hit = cast_ray(scene, 4.5, 3.5, ray_x, ray_y)
    assert (hit.map_x, hit.map_y) == cell
    assert hit.side == side
    assert hit.distance == pytest.approx(distance)
    assert hit.wall_x == pytest.approx(0.5)
    assert hit.facing == facing


def test_zero_ray() -> None:
    scene = make_scene(["111", "101", "111"])
    with pytest.raises(ValueError):
        cast_ray(scene, 1.5, 1.5, 0, 0)


def test_outside_of_map_is_wall() -> None:
    scene = make_scene(["000", "000", "000"])  # стен нет, но за картой стена есть
    hit = cast_ray(scene, 1.5, 1.5, 1.0, 0.0)
    assert (hit.map_x, hit.map_y) == (3, 1)
    assert hit.distance == pytest.approx(1.5)


def test_ray_without_walls_does_not_hang(monkeypatch: pytest.MonkeyPatch) -> None:
    scene = make_scene(["000", "000", "000"])
    monkeypatch.setattr(scene, "is_wall", lambda x, y: False)  # стен нет совсем
    with pytest.raises(RaycastError):
        cast_ray(scene, 1.5, 1.5, 1.0, 0.3)


def test_raycast_error_is_cub_error() -> None:
    assert issubclass(RaycastError, CubError)
