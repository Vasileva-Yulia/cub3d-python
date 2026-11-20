import math
from pathlib import Path

import pygame
import pytest

from cub3d.errors import CubError
from cub3d.parser import parse_scene
from cub3d.player import PLANE_LENGTH, Player, make_player, rotate_player
from cub3d.scene import Scene
from cub3d.texture import TEXTURE_SIZE
from cub3d.window import Textures, draw_frame, load_textures, save_frame

MAPS = Path(__file__).resolve().parent.parent / "maps"
WIDTH = 960
HEIGHT = 600
CEILING = (150, 190, 230)
FLOOR = (60, 60, 70)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
MAGENTA = (255, 0, 255)


def make_columns(
    top_color: tuple[int, int, int], bottom_color: tuple[int, int, int]
) -> list[pygame.Surface]:
    """64 столбца текстуры: верхняя половина одного цвета, нижняя другого."""
    columns = []
    for _ in range(TEXTURE_SIZE):
        column = pygame.Surface((1, TEXTURE_SIZE))
        column.fill(top_color, (0, 0, 1, TEXTURE_SIZE // 2))
        column.fill(bottom_color, (0, TEXTURE_SIZE // 2, 1, TEXTURE_SIZE // 2))
        columns.append(column)
    return columns


def make_textures() -> Textures:
    """По одному цвету на сторону света: сразу видно, какая текстура выбрана."""
    return {
        "NO": make_columns(RED, BLUE),
        "SO": make_columns(GREEN, BLUE),
        "WE": make_columns(YELLOW, BLUE),
        "EA": make_columns(MAGENTA, GREEN),
    }


def color_at(screen: pygame.Surface, x: int, y: int) -> tuple[int, int, int]:
    color = screen.get_at((x, y))
    return color.r, color.g, color.b


def make_frame(player: Player | None = None) -> pygame.Surface:
    """Кадр maps/simple.cub без окна: рисуем на обычной поверхности в памяти."""
    scene = parse_scene(MAPS / "simple.cub")
    if player is None:
        player = make_player(scene)
    screen = pygame.Surface((WIDTH, HEIGHT))
    draw_frame(screen, scene, player, make_textures())
    return screen


def test_ceiling_and_floor_colors() -> None:
    screen = make_frame()
    # в центре кадра стена на расстоянии 2,5 занимает строки 180..419
    assert color_at(screen, 480, 0) == CEILING
    assert color_at(screen, 480, 179) == CEILING
    assert color_at(screen, 480, 420) == FLOOR
    assert color_at(screen, 480, 599) == FLOOR


def test_wall_in_center_has_known_height() -> None:
    screen = make_frame()
    wall_rows = []
    for y in range(HEIGHT):
        if color_at(screen, 480, y) not in (CEILING, FLOOR):
            wall_rows.append(y)
    assert len(wall_rows) == 240  # 600 / 2,5
    assert wall_rows[0] == 180
    assert wall_rows[-1] == 419


def test_wall_uses_texture_of_its_side() -> None:
    screen = make_frame()  # игрок смотрит на север: в центре стена NO
    assert color_at(screen, 480, 200) == RED  # верхняя половина текстуры NO
    assert color_at(screen, 480, 400) == BLUE  # нижняя половина


def test_texture_is_stretched_over_the_strip() -> None:
    screen = make_frame()  # полоса 180..419: верхняя половина 180..299, нижняя 300..419
    assert color_at(screen, 480, 180) == RED
    assert color_at(screen, 480, 299) == RED
    assert color_at(screen, 480, 300) == BLUE
    assert color_at(screen, 480, 419) == BLUE


@pytest.mark.parametrize(
    ("quarter_turns", "top_color"),
    [
        (0, RED),  # север: текстура NO
        (1, MAGENTA),  # восток: текстура EA
        (2, GREEN),  # юг: текстура SO
        (3, YELLOW),  # запад: текстура WE
    ],
)
def test_each_side_uses_its_texture(quarter_turns: int, top_color: tuple[int, int, int]) -> None:
    scene = parse_scene(MAPS / "simple.cub")
    player = make_player(scene)
    rotate_player(player, quarter_turns * math.pi / 2)  # поворот вправо на 90° за раз
    screen = make_frame(player)
    # все четыре стены видны в центре кадра выше середины, там верхняя половина текстуры
    assert color_at(screen, 480, HEIGHT // 2 - 20) == top_color


def test_close_wall_shows_middle_of_texture() -> None:
    # стена на расстоянии 0,3 в 3 раза выше экрана: видна только середина столбца текстуры
    player = Player(4.5, 1.3, 0, -1, PLANE_LENGTH, 0)
    screen = make_frame(player)
    assert color_at(screen, 480, 0) == RED
    assert color_at(screen, 480, 250) == RED  # граница верхней и нижней половин - в центре кадра
    assert color_at(screen, 480, 350) == BLUE
    assert color_at(screen, 480, HEIGHT - 1) == BLUE


def test_other_screen_size() -> None:
    scene = parse_scene(MAPS / "simple.cub")
    screen = pygame.Surface((320, 200))
    draw_frame(screen, scene, make_player(scene), make_textures())
    assert color_at(screen, 160, 0) == CEILING
    assert color_at(screen, 160, 199) == FLOOR
    assert color_at(screen, 160, 70) == RED


def test_load_textures() -> None:
    scene = parse_scene(MAPS / "simple.cub")
    textures = load_textures(scene)
    assert sorted(textures) == ["EA", "NO", "SO", "WE"]
    for columns in textures.values():
        assert len(columns) == TEXTURE_SIZE
        assert columns[0].get_size() == (1, TEXTURE_SIZE)


def test_texture_with_wrong_size(tmp_path: Path) -> None:
    small = tmp_path / "small.png"
    pygame.image.save(pygame.Surface((32, 32)), str(small))
    scene = Scene({"NO": small}, (0, 0, 0), (0, 0, 0), ["111", "101", "111"], 1, 1, "N")
    with pytest.raises(CubError) as info:
        load_textures(scene)
    assert "64x64" in str(info.value)


def test_texture_is_not_an_image(tmp_path: Path) -> None:
    fake = tmp_path / "fake.png"
    fake.write_text("это не картинка", encoding="utf-8")
    scene = Scene({"NO": fake}, (0, 0, 0), (0, 0, 0), ["111", "101", "111"], 1, 1, "N")
    with pytest.raises(CubError):
        load_textures(scene)


def test_save_frame(tmp_path: Path) -> None:
    scene = parse_scene(MAPS / "simple.cub")
    save_frame(scene, tmp_path / "frame.png", 320, 200)
    image = pygame.image.load(str(tmp_path / "frame.png"))
    assert image.get_size() == (320, 200)
