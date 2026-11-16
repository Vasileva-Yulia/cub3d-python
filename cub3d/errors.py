"""Исключения программы."""


class CubError(Exception):
    """Базовая ошибка cub3D."""


class SceneFormatError(CubError):
    """Ошибка в файле сцены .cub."""

    def __init__(self, message: str, line: int | None = None, column: int | None = None) -> None:
        if line is not None and column is not None:
            text = f"строка {line}, колонка {column}: {message}"
        elif line is not None:
            text = f"строка {line}: {message}"
        else:
            text = message
        super().__init__(text)
        self.line = line
        self.column = column
