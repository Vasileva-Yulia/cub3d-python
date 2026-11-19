"""Модель сцены: текстуры, цвета, карта и стартовая позиция игрока."""

from dataclasses import dataclass
from pathlib import Path

Color = tuple[int, int, int]

WALL = "1"
FLOOR = "0"
EMPTY = " "


@dataclass
class Scene:
    textures: dict[str, Path]  # "NO", "SO", "WE", "EA" -> путь к PNG
    floor: Color
    ceiling: Color
    grid: list[str]  # строки карты одной длины: короткие дополнены пробелами
    start_x: int
    start_y: int
    start_dir: str  # "N", "S", "E" или "W"

    @property
    def width(self) -> int:
        return len(self.grid[0])

    @property
    def height(self) -> int:
        return len(self.grid)

    def is_wall(self, x: int, y: int) -> bool:
        """Непроходима ли клетка. Всё, что за пределами карты, тоже считаем стеной."""
        if not (0 <= x < self.width and 0 <= y < self.height):
            return True
        return self.grid[y][x] != FLOOR
