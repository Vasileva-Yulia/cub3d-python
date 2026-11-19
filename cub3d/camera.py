"""Камера: луч для каждого столбца экрана."""

from cub3d.player import Player


def camera_x(column: int, width: int) -> float:
    """Столбец экрана -> точка на плоскости камеры: от -1 слева до +1 справа."""
    return 2 * column / width - 1


def ray_direction(player: Player, cam_x: float) -> tuple[float, float]:
    """Направление луча: dir + plane * camX."""
    ray_x = player.dir_x + player.plane_x * cam_x
    ray_y = player.dir_y + player.plane_y * cam_x
    return ray_x, ray_y
