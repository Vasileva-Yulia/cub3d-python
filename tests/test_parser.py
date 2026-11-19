import shutil
from pathlib import Path

import pytest

from cub3d.errors import CubError, SceneFormatError
from cub3d.parser import parse_color, parse_scene, parse_scene_text

ROOT = Path(__file__).resolve().parent.parent
MAPS = ROOT / "maps"
TEXTURES = ROOT / "textures"


def test_simple_map() -> None:
    scene = parse_scene(MAPS / "simple.cub")
    assert (scene.width, scene.height) == (10, 8)
    assert (scene.start_x, scene.start_y, scene.start_dir) == (4, 3, "N")
    assert scene.floor == (60, 60, 70)
    assert scene.ceiling == (150, 190, 230)
    assert scene.textures["NO"] == TEXTURES / "north.png"
    assert scene.textures["EA"] == TEXTURES / "east.png"


def test_player_cell_becomes_floor() -> None:
    scene = parse_scene(MAPS / "simple.cub")
    assert scene.grid[3] == "1000000101"
    assert not scene.is_wall(4, 3)


def test_is_wall() -> None:
    scene = parse_scene(MAPS / "simple.cub")
    assert scene.is_wall(0, 0)
    assert scene.is_wall(3, 2)  # колонна внутри комнаты
    assert not scene.is_wall(1, 1)
    assert scene.is_wall(-1, 1)  # за пределами карты
    assert scene.is_wall(10, 1)


def test_elements_in_any_order_with_blank_lines() -> None:
    text = (
        "\nC 1,2,3\n\n\nEA textures/east.png\nF 4, 5 ,6\nWE textures/west.png\n"
        "SO textures/south.png\n\nNO textures/north.png\n\n111\n1S1\n111\n\n\n"
    )
    scene = parse_scene_text(text, ROOT)
    assert scene.ceiling == (1, 2, 3)
    assert scene.floor == (4, 5, 6)
    assert scene.grid == ["111", "101", "111"]
    assert scene.start_dir == "S"


def test_irregular_map() -> None:
    scene = parse_scene(MAPS / "irregular.cub")
    assert (scene.width, scene.height) == (23, 8)
    assert all(len(row) == scene.width for row in scene.grid)
    assert scene.start_dir == "W"


def test_texture_next_to_scene_file(tmp_path: Path) -> None:
    # относительный путь, которого нет от текущего каталога, ищется рядом с файлом сцены
    for name in ("north", "south", "west", "east"):
        shutil.copy(TEXTURES / f"{name}.png", tmp_path / f"my_{name}.png")
    text = (MAPS / "simple.cub").read_text(encoding="utf-8").replace("textures/", "my_")
    (tmp_path / "room.cub").write_text(text, encoding="utf-8")
    scene = parse_scene(tmp_path / "room.cub")
    assert scene.textures["SO"] == (tmp_path / "my_south.png").resolve()


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("60,60,70", (60, 60, 70)),
        ("0,0,0", (0, 0, 0)),
        (" 255 , 0,10 ", (255, 0, 10)),
    ],
)
def test_parse_color(text: str, expected: tuple[int, int, int]) -> None:
    assert parse_color(text) == expected


@pytest.mark.parametrize("text", ["60,60", "1,2,3,4", "256,0,0", "-1,0,0", "a,0,0", "1.5,0,0", ""])
def test_parse_color_invalid(text: str) -> None:
    with pytest.raises(ValueError):
        parse_color(text)


@pytest.mark.parametrize(
    ("name", "message"),
    [
        ("empty.cub", "файл пуст"),
        ("missing_element.cub", "не заданы элементы: C"),
        ("duplicate_element.cub", "строка 7: элемент F задан повторно"),
        ("unknown_element.cub", "строка 6: неизвестный элемент 'R'"),
        ("bad_color.cub", "строка 6: цвет '60,300,70': 300 больше 255"),
        ("missing_texture.cub", "строка 1: файл текстуры 'textures/nope.png' не найден"),
        ("map_too_early.cub", "строка 8: карта начинается раньше всех элементов, не хватает: C"),
        ("invalid_char.cub", "строка 11, колонка 4: недопустимый символ '2' в карте"),
        ("no_player.cub", "на карте нет игрока"),
        ("two_players.cub", "строка 13, колонка 8: игрок задан второй раз"),
        ("open_edge.cub", "строка 16, колонка 6: карта не замкнута: клетка пола на краю карты"),
        ("open_space.cub", "строка 10, колонка 4: карта не замкнута: клетка граничит с пустотой"),
        ("empty_line_in_map.cub", "строка 14: пустая строка внутри карты"),
        ("no_map.cub", "в файле нет карты"),
    ],
)
def test_bad_maps(name: str, message: str) -> None:
    with pytest.raises(SceneFormatError) as info:
        parse_scene(MAPS / "bad" / name)
    assert str(info.value) == message


def test_element_without_value() -> None:
    # «WE» состоит из символов карты, но это идентификатор элемента, а не строка карты
    with pytest.raises(SceneFormatError) as info:
        parse_scene_text("NO textures/north.png\nWE\n", ROOT)
    assert str(info.value) == "строка 2: у элемента WE нет значения"


def test_wrong_extension(tmp_path: Path) -> None:
    path = tmp_path / "room.txt"
    path.write_text("", encoding="utf-8")
    with pytest.raises(SceneFormatError, match=r"\.cub"):
        parse_scene(path)


def test_missing_file() -> None:
    with pytest.raises(FileNotFoundError):
        parse_scene(MAPS / "nope.cub")


def test_scene_format_error_is_cub_error() -> None:
    assert issubclass(SceneFormatError, CubError)
