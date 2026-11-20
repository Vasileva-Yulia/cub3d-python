"""Движение игрока: сдвиг по осям отдельно, отступ от стен, скорость не зависит от FPS."""

from cub3d.player import Player
from cub3d.scene import Scene

MOVE_SPEED = 3.0  # клеток в секунду
MARGIN = 0.2  # на таком расстоянии от стены игрок останавливается


def move_player(player: Player, scene: Scene, dx: float, dy: float) -> None:
    """Сдвинуть игрока на (dx, dy). Оси проверяются по отдельности, поэтому у стены он скользит."""
    if dx != 0:
        new_x = player.x + dx
        # проверяем точку с отступом в сторону движения
        if dx > 0:
            edge_x = new_x + MARGIN
        else:
            edge_x = new_x - MARGIN
        if not scene.is_wall(int(edge_x), int(player.y)):
            player.x = new_x
    if dy != 0:
        new_y = player.y + dy
        if dy > 0:
            edge_y = new_y + MARGIN
        else:
            edge_y = new_y - MARGIN
        if not scene.is_wall(int(player.x), int(edge_y)):
            player.y = new_y


def walk_player(player: Player, scene: Scene, forward: int, strafe: int, dt: float) -> None:
    """Шаг за время dt. forward: 1 - вперёд, -1 - назад; strafe: 1 - вправо, -1 - влево."""
    # right = (-dir_y, dir_x) - перпендикуляр к взгляду
    dx = (player.dir_x * forward - player.dir_y * strafe) * MOVE_SPEED * dt
    dy = (player.dir_y * forward + player.dir_x * strafe) * MOVE_SPEED * dt
    move_player(player, scene, dx, dy)
