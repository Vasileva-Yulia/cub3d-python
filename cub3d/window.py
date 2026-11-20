"""Окно: отрисовка кадра и главный цикл. Единственный модуль, который импортирует pygame."""

from pathlib import Path

import pygame

from cub3d.camera import camera_x, ray_direction
from cub3d.errors import CubError
from cub3d.movement import walk_player
from cub3d.player import TURN_SPEED, Player, make_player, rotate_player
from cub3d.raycast import cast_ray, strip_height
from cub3d.scene import Scene
from cub3d.texture import TEXTURE_SIZE, texture_column, texture_rows

Textures = dict[str, list[pygame.Surface]]  # "NO", "SO", "WE", "EA" -> 64 столбца текстуры

FPS_LIMIT = 60
MAX_DT = 0.1  # самый длинный шаг по времени: при лаге игрок не «перепрыгнет» стену


def load_textures(scene: Scene) -> Textures:
    """Загрузить текстуры и нарезать каждую на 64 столбца шириной в 1 пиксель."""
    textures: Textures = {}
    for key, path in scene.textures.items():
        try:
            image = pygame.image.load(str(path))
        except pygame.error as e:
            raise CubError(f"не удалось загрузить текстуру {path}: {e}") from e
        if image.get_size() != (TEXTURE_SIZE, TEXTURE_SIZE):
            raise CubError(f"текстура {path} должна быть размером {TEXTURE_SIZE}x{TEXTURE_SIZE}")
        if pygame.display.get_surface() is not None:
            image = image.convert()  # формат как у окна: так быстрее копировать на экран
        columns = []
        for x in range(TEXTURE_SIZE):
            columns.append(image.subsurface((x, 0, 1, TEXTURE_SIZE)))
        textures[key] = columns
    return textures


def draw_wall_column(screen: pygame.Surface, column: pygame.Surface, x: int, height: int) -> None:
    """Растянуть столбец текстуры на высоту полосы и скопировать на экран в столбец x."""
    top = (screen.get_height() - height) // 2
    # у близкой стены масштабируем только видимую часть столбца
    first, last = texture_rows(height, screen.get_height())
    part = column.subsurface((0, first, 1, last - first))
    part_top = top + first * height // TEXTURE_SIZE
    part_height = top + last * height // TEXTURE_SIZE - part_top
    screen.blit(pygame.transform.scale(part, (1, part_height)), (x, part_top))


def draw_frame(screen: pygame.Surface, scene: Scene, player: Player, textures: Textures) -> None:
    """Нарисовать кадр: потолок, пол и по одному столбцу текстуры на столбец экрана."""
    width, height = screen.get_size()
    half = height // 2
    screen.fill(scene.ceiling, (0, 0, width, half))
    screen.fill(scene.floor, (0, half, width, height - half))
    for column in range(width):
        ray_x, ray_y = ray_direction(player, camera_x(column, width))
        hit = cast_ray(scene, player.x, player.y, ray_x, ray_y)
        wall_height = strip_height(hit.distance, height)
        tex_x = texture_column(hit.wall_x, hit.facing)
        draw_wall_column(screen, textures[hit.facing][tex_x], column, wall_height)


def save_frame(scene: Scene, path: str | Path, width: int, height: int) -> None:
    """Нарисовать один кадр без окна и сохранить в PNG."""
    screen = pygame.Surface((width, height))
    draw_frame(screen, scene, make_player(scene), load_textures(scene))
    pygame.image.save(screen, str(path))


def handle_keys(player: Player, scene: Scene, dt: float) -> None:
    """Зажатые клавиши: W/S - вперёд и назад, A/D - боком, стрелки влево и вправо - поворот."""
    keys = pygame.key.get_pressed()
    forward = 0
    strafe = 0
    turn = 0
    if keys[pygame.K_w]:
        forward += 1
    if keys[pygame.K_s]:
        forward -= 1
    if keys[pygame.K_d]:
        strafe += 1
    if keys[pygame.K_a]:
        strafe -= 1
    if keys[pygame.K_RIGHT]:
        turn += 1
    if keys[pygame.K_LEFT]:
        turn -= 1
    rotate_player(player, turn * TURN_SPEED * dt)
    walk_player(player, scene, forward, strafe, dt)


def run_window(scene: Scene, width: int, height: int) -> None:
    """Открыть окно: игрок ходит по сцене, пока не нажат Esc или не закрыто окно."""
    player = make_player(scene)
    try:
        pygame.init()
        screen = pygame.display.set_mode((width, height))
        textures = load_textures(scene)
        clock = pygame.time.Clock()
        running = True
        dt = 0.0  # время предыдущего кадра в секундах
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    running = False
            handle_keys(player, scene, dt)
            draw_frame(screen, scene, player, textures)
            pygame.display.flip()
            dt = clock.tick(FPS_LIMIT) / 1000
            if dt > MAX_DT:
                dt = MAX_DT
            pygame.display.set_caption(f"cub3D - {clock.get_fps():.0f} FPS")
    except pygame.error as e:
        raise CubError(f"ошибка графической библиотеки: {e}") from e
    finally:
        pygame.quit()
