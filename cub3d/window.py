"""Окно: отрисовка кадра и главный цикл. Единственный модуль, который импортирует pygame."""

from pathlib import Path

import pygame

from cub3d.camera import camera_x, ray_direction
from cub3d.errors import CubError
from cub3d.player import Player, make_player
from cub3d.raycast import cast_ray, wall_strip
from cub3d.scene import Scene

WALL_COLORS = ((140, 140, 140), (200, 200, 200))  # side 0 темнее, side 1 светлее
FPS_LIMIT = 60


def draw_frame(screen: pygame.Surface, scene: Scene, player: Player) -> None:
    """Нарисовать кадр: потолок, пол и по одной вертикальной полосе стены на столбец."""
    width, height = screen.get_size()
    half = height // 2
    screen.fill(scene.ceiling, (0, 0, width, half))
    screen.fill(scene.floor, (0, half, width, height - half))
    for column in range(width):
        ray_x, ray_y = ray_direction(player, camera_x(column, width))
        hit = cast_ray(scene, player.x, player.y, ray_x, ray_y)
        top, bottom = wall_strip(hit.distance, height)
        # bottom не входит в полосу, а draw.line рисует обе крайние точки
        pygame.draw.line(screen, WALL_COLORS[hit.side], (column, top), (column, bottom - 1))


def save_frame(scene: Scene, path: str | Path, width: int, height: int) -> None:
    """Нарисовать один кадр без окна и сохранить в PNG."""
    screen = pygame.Surface((width, height))
    draw_frame(screen, scene, make_player(scene))
    pygame.image.save(screen, str(path))


def run_window(scene: Scene, width: int, height: int) -> None:
    """Открыть окно и показывать сцену, пока не нажат Esc или не закрыто окно."""
    player = make_player(scene)
    try:
        pygame.init()
        screen = pygame.display.set_mode((width, height))
        clock = pygame.time.Clock()
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    running = False
            draw_frame(screen, scene, player)
            pygame.display.flip()
            clock.tick(FPS_LIMIT)
            pygame.display.set_caption(f"cub3D - {clock.get_fps():.0f} FPS")
    except pygame.error as e:
        raise CubError(f"ошибка графической библиотеки: {e}") from e
    finally:
        pygame.quit()
