"""Игрок: позиция, направление взгляда и плоскость камеры."""

import math
from dataclasses import dataclass

from cub3d.scene import Scene

FOV = 66  # угол обзора в градусах
PLANE_LENGTH = math.tan(math.radians(FOV / 2))  # длина plane, около 0,65


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
