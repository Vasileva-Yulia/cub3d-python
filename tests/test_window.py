from pathlib import Path

import pygame

from cub3d.camera import camera_x, ray_direction
from cub3d.parser import parse_scene
from cub3d.player import make_player
from cub3d.raycast import cast_ray
from cub3d.window import WALL_COLORS, draw_frame, save_frame

MAPS = Path(__file__).resolve().parent.parent / "maps"
WIDTH = 960
HEIGHT = 600


def make_frame() -> pygame.Surface:
    """Кадр maps/simple.cub без окна: рисуем на обычной поверхности в памяти."""
    scene = parse_scene(MAPS / "simple.cub")
    screen = pygame.Surface((WIDTH, HEIGHT))
    draw_frame(screen, scene, make_player(scene))
    return screen


def color_at(screen: pygame.Surface, x: int, y: int) -> tuple[int, int, int]:
    color = screen.get_at((x, y))
    return color.r, color.g, color.b


def test_ceiling_and_floor_colors() -> None:
    screen = make_frame()
    # в центре кадра стена на расстоянии 2,5 занимает строки 180..419
    assert color_at(screen, 480, 0) == (150, 190, 230)  # потолок
    assert color_at(screen, 480, 179) == (150, 190, 230)
    assert color_at(screen, 480, 420) == (60, 60, 70)  # пол
    assert color_at(screen, 480, 599) == (60, 60, 70)


def test_wall_strip_in_center_has_known_height() -> None:
    screen = make_frame()
    wall_rows = []
    for y in range(HEIGHT):
        if color_at(screen, 480, y) == WALL_COLORS[1]:
            wall_rows.append(y)
    assert len(wall_rows) == 240  # 600 / 2,5
    assert wall_rows[0] == 180
    assert wall_rows[-1] == 419
    assert color_at(screen, 480, HEIGHT // 2) == WALL_COLORS[1]  # север: side = 1


def test_side_zero_is_darker_than_side_one() -> None:
    assert sum(WALL_COLORS[0]) < sum(WALL_COLORS[1])
    screen = make_frame()
    scene = parse_scene(MAPS / "simple.cub")
    player = make_player(scene)
    for column in range(WIDTH):
        ray_x, ray_y = ray_direction(player, camera_x(column, WIDTH))
        hit = cast_ray(scene, player.x, player.y, ray_x, ray_y)
        assert color_at(screen, column, HEIGHT // 2) == WALL_COLORS[hit.side]


def test_other_screen_size() -> None:
    scene = parse_scene(MAPS / "simple.cub")
    screen = pygame.Surface((320, 200))
    draw_frame(screen, scene, make_player(scene))
    assert color_at(screen, 160, 0) == (150, 190, 230)
    assert color_at(screen, 160, 199) == (60, 60, 70)
    assert color_at(screen, 160, 100) == WALL_COLORS[1]


def test_save_frame(tmp_path: Path) -> None:
    scene = parse_scene(MAPS / "simple.cub")
    save_frame(scene, tmp_path / "frame.png", 320, 200)
    image = pygame.image.load(str(tmp_path / "frame.png"))
    assert image.get_size() == (320, 200)
