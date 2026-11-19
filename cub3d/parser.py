"""Чтение файлов сцены .cub."""

import re
from pathlib import Path

from cub3d.errors import SceneFormatError
from cub3d.scene import EMPTY, FLOOR, Color, Scene

TEXTURE_IDS = ("NO", "SO", "WE", "EA")
COLOR_IDS = ("F", "C")
ALL_IDS = TEXTURE_IDS + COLOR_IDS
PLAYER_CHARS = "NSEW"
MAP_CHARS = "01NSEW "  # стена, пол, игрок, пустота
NUMBER_RE = re.compile(r"[0-9]+")


def parse_color(text: str) -> Color:
    """'60,60,70' -> (60, 60, 70). Пробелы вокруг чисел допускаются."""
    parts = text.split(",")
    if len(parts) != 3:
        raise ValueError(f"цвет '{text}': нужно три числа через запятую")
    values = []
    for part in parts:
        number = part.strip()
        if not NUMBER_RE.fullmatch(number):
            raise ValueError(f"цвет '{text}': '{number}' — не целое число")
        if int(number) > 255:
            raise ValueError(f"цвет '{text}': {number} больше 255")
        values.append(int(number))
    return values[0], values[1], values[2]


def find_texture(value: str, base_dir: Path) -> Path:
    """Найти файл текстуры: сначала от текущего каталога, потом от каталога сцены."""
    if not value.lower().endswith(".png"):
        raise ValueError(f"текстура '{value}' должна быть файлом PNG")
    for candidate in (Path(value), base_dir / value):
        if candidate.is_file():
            return candidate.resolve()
    raise ValueError(f"файл текстуры '{value}' не найден")


def is_map_line(line: str) -> bool:
    return line.strip() != "" and all(char in MAP_CHARS for char in line)


def missing_ids(found: list[str]) -> str:
    return ", ".join(key for key in ALL_IDS if key not in found)


def parse_scene_text(text: str, base_dir: Path) -> Scene:
    lines = text.splitlines()
    if not any(line.strip() for line in lines):
        raise SceneFormatError("файл пуст")

    textures: dict[str, Path] = {}
    colors: dict[str, Color] = {}
    index = 0
    # сначала шесть элементов в любом порядке, между ними могут быть пустые строки
    while index < len(lines) and len(textures) + len(colors) < len(ALL_IDS):
        line_no = index + 1
        line = lines[index]
        index += 1
        if not line.strip():
            continue
        found = list(textures) + list(colors)
        parts = line.split(maxsplit=1)
        key = parts[0]
        if key not in ALL_IDS:
            if is_map_line(line):
                raise SceneFormatError(
                    f"карта начинается раньше всех элементов, не хватает: {missing_ids(found)}",
                    line_no,
                )
            raise SceneFormatError(f"неизвестный элемент '{key}'", line_no)
        if key in found:
            raise SceneFormatError(f"элемент {key} задан повторно", line_no)
        if len(parts) < 2:
            raise SceneFormatError(f"у элемента {key} нет значения", line_no)
        try:
            if key in TEXTURE_IDS:
                textures[key] = find_texture(parts[1].strip(), base_dir)
            else:
                colors[key] = parse_color(parts[1])
        except ValueError as e:
            raise SceneFormatError(str(e), line_no) from e

    if len(textures) + len(colors) < len(ALL_IDS):
        raise SceneFormatError(f"не заданы элементы: {missing_ids(list(textures) + list(colors))}")

    # потом карта: пропускаем пустые строки перед ней и в конце файла
    while index < len(lines) and not lines[index].strip():
        index += 1
    map_lines = lines[index:]
    while map_lines and not map_lines[-1].strip():
        map_lines.pop()
    if not map_lines:
        raise SceneFormatError("в файле нет карты")
    first_word = map_lines[0].split()[0]
    if first_word in ALL_IDS:
        raise SceneFormatError(f"элемент {first_word} задан повторно", index + 1)

    grid, x, y, direction = parse_map(map_lines, index + 1)
    return Scene(textures, colors["F"], colors["C"], grid, x, y, direction)


def parse_map(lines: list[str], first_line: int) -> tuple[list[str], int, int, str]:
    """Разобрать карту. Возвращает сетку и стартовую клетку игрока с направлением."""
    width = max(len(line) for line in lines)
    grid = []
    player = None
    for y, line in enumerate(lines):
        line_no = first_line + y
        if not line.strip():
            raise SceneFormatError("пустая строка внутри карты", line_no)
        for x, char in enumerate(line):
            if char not in MAP_CHARS:
                raise SceneFormatError(f"недопустимый символ '{char}' в карте", line_no, x + 1)
            if char in PLAYER_CHARS:
                if player is not None:
                    raise SceneFormatError("игрок задан второй раз", line_no, x + 1)
                player = (x, y, char)
        grid.append(line.ljust(width))

    if player is None:
        raise SceneFormatError("на карте нет игрока")
    x, y, direction = player
    grid[y] = grid[y][:x] + FLOOR + grid[y][x + 1 :]  # клетка игрока — обычный пол
    check_closed(grid, first_line)
    return grid, x, y, direction


def check_closed(grid: list[str], first_line: int) -> None:
    """Клетка пола не должна стоять на краю карты и касаться пустоты, даже по диагонали."""
    height, width = len(grid), len(grid[0])
    for y in range(height):
        for x in range(width):
            if grid[y][x] != FLOOR:
                continue
            if x in (0, width - 1) or y in (0, height - 1):
                raise SceneFormatError(
                    "карта не замкнута: клетка пола на краю карты", first_line + y, x + 1
                )
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    if grid[y + dy][x + dx] == EMPTY:
                        raise SceneFormatError(
                            "карта не замкнута: клетка граничит с пустотой", first_line + y, x + 1
                        )


def parse_scene(path: str | Path) -> Scene:
    """Прочитать сцену из файла. OSError (нет файла и т.п.) не перехватывается."""
    scene_path = Path(path)
    if scene_path.suffix != ".cub":
        raise SceneFormatError(f"файл сцены должен иметь расширение .cub: {scene_path.name}")
    try:
        text = scene_path.read_text(encoding="utf-8-sig")  # -sig: пропускает BOM от Блокнота
    except UnicodeDecodeError as e:
        raise SceneFormatError("файл не в кодировке UTF-8") from e
    return parse_scene_text(text, scene_path.parent)
