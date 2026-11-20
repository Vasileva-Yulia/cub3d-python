"""Игрок: позиция, направление взгляда и плоскость камеры."""

import math
from dataclasses import dataclass

from cub3d.scene import Scene

FOV = 66  # угол обзора в градусах
PLANE_LENGTH = math.tan(math.radians(FOV / 2))  # длина plane, около 0,65
TURN_SPEED = 2.0  # скорость поворота, радиан в секунду


@dataclass
class Player:
    x: float
    y: float
    dir_x: float  # направление взгляда (единичный вектор)
    dir_y: float
    plane_x: float  # плоскость камеры, перпендикулярна взгляду
    plane_y: float


def make_player(scene: Scene) -> Player:
    """Игрок в центре стартовой клетки, взгляд в сторону scene.start_dir."""
    if scene.start_dir == "N":
        dir_x, dir_y = 0.0, -1.0
    elif scene.start_dir == "S":
        dir_x, dir_y = 0.0, 1.0
    elif scene.start_dir == "E":
        dir_x, dir_y = 1.0, 0.0
    else:
        dir_x, dir_y = -1.0, 0.0
    # plane - это dir, повёрнутый на 90° вправо, длиной tan(FOV / 2)
    plane_x = -dir_y * PLANE_LENGTH
    plane_y = dir_x * PLANE_LENGTH
    return Player(scene.start_x + 0.5, scene.start_y + 0.5, dir_x, dir_y, plane_x, plane_y)


def rotate_player(player: Player, angle: float) -> None:
    """Повернуть взгляд и плоскость камеры на angle радиан (положительный угол - вправо)."""
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    old_dir_x = player.dir_x
    player.dir_x = player.dir_x * cos_a - player.dir_y * sin_a
    player.dir_y = old_dir_x * sin_a + player.dir_y * cos_a
    old_plane_x = player.plane_x
    player.plane_x = player.plane_x * cos_a - player.plane_y * sin_a
    player.plane_y = old_plane_x * sin_a + player.plane_y * cos_a
