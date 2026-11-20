"""Рейкастинг: поиск стены алгоритмом DDA."""

import math
from dataclasses import dataclass

from cub3d.errors import RaycastError
from cub3d.scene import Scene

BIG = 1e30  # «бесконечное» расстояние для луча, параллельного оси
MIN_DISTANCE = 0.01  # ближе стену не считаем, чтобы не делить на ноль


@dataclass
class RayHit:
    map_x: int  # клетка стены
    map_y: int
    side: int  # 0 - пересекли вертикальную границу, 1 - горизонтальную
    distance: float  # перпендикулярное расстояние до стены
    wall_x: float  # где по ширине стены попал луч, от 0 до 1
    facing: str  # NO, SO, WE или EA - какая текстура нужна


def wall_facing(side: int, ray_x: float, ray_y: float) -> str:
    """Сторона света для выбора текстуры."""
    if side == 0:
        if ray_x > 0:
            return "EA"
        return "WE"
    if ray_y > 0:
        return "SO"
    return "NO"


def cast_ray(scene: Scene, pos_x: float, pos_y: float, ray_x: float, ray_y: float) -> RayHit:
    """Пустить луч из точки (pos_x, pos_y) и найти первую стену на его пути."""
    if ray_x == 0 and ray_y == 0:
        raise ValueError("направление луча не может быть нулевым")

    map_x = int(pos_x)
    map_y = int(pos_y)
    # расстояние вдоль луча между соседними границами клеток
    if ray_x == 0:
        delta_x = BIG
    else:
        delta_x = abs(1 / ray_x)
    if ray_y == 0:
        delta_y = BIG
    else:
        delta_y = abs(1 / ray_y)
    # шаг по клеткам и расстояние до первой границы
    if ray_x < 0:
        step_x = -1
        side_x = (pos_x - map_x) * delta_x
    else:
        step_x = 1
        side_x = (map_x + 1 - pos_x) * delta_x
    if ray_y < 0:
        step_y = -1
        side_y = (pos_y - map_y) * delta_y
    else:
        step_y = 1
        side_y = (map_y + 1 - pos_y) * delta_y

    side = 0
    steps = 0
    max_steps = 2 * (scene.width + scene.height)  # защита от бесконечного цикла
    found_wall = False
    while not found_wall:
        if steps >= max_steps:
            raise RaycastError("луч не встретил стену: карта не замкнута")
        steps += 1
        if side_x < side_y:
            side_x += delta_x
            map_x += step_x
            side = 0
        else:
            side_y += delta_y
            map_y += step_y
            side = 1
        if scene.is_wall(map_x, map_y):
            found_wall = True

    # перпендикулярное расстояние и точка попадания вдоль стены
    if side == 0:
        distance = side_x - delta_x
        hit_pos = pos_y + distance * ray_y
    else:
        distance = side_y - delta_y
        hit_pos = pos_x + distance * ray_x
    wall_x = hit_pos - math.floor(hit_pos)
    return RayHit(map_x, map_y, side, distance, wall_x, wall_facing(side, ray_x, ray_y))


def strip_height(distance: float, screen_height: int) -> int:
    """Полная высота полосы стены в пикселях: на расстоянии 1 - весь экран, на 2 - половина."""
    if distance < MIN_DISTANCE:
        distance = MIN_DISTANCE
    height = int(screen_height / distance)
    if height < 1:
        height = 1  # у очень далёкой стены остаётся хотя бы одна строка
    return height
