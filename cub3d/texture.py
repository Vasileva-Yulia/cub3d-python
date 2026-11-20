"""Текстуры стен: какой столбец текстуры нужен и какие строки видны на экране."""

TEXTURE_SIZE = 64  # текстура - квадрат 64x64


def texture_column(wall_x: float, facing: str) -> int:
    """Номер столбца текстуры от 0 до 63 для точки попадания wall_x (от 0 до 1)."""
    tex_x = int(wall_x * TEXTURE_SIZE)
    # у сторон WE и SO экранная ось x идёт против оси карты, поэтому столбец отражаем
    if facing in ("WE", "SO"):
        tex_x = TEXTURE_SIZE - 1 - tex_x
    return tex_x


def texture_rows(height: int, screen_height: int) -> tuple[int, int]:
    """Строки текстуры с первой по последнюю (не включая), которые видны на экране."""
    if height <= screen_height:
        return 0, TEXTURE_SIZE  # полоса целиком на экране
    # стена ближе одной клетки: сверху и снизу за экраном скрыто по несколько пикселей полосы
    hidden = (height - screen_height) // 2
    first = hidden * TEXTURE_SIZE // height
    return first, TEXTURE_SIZE - first
