"""Запуск: python main.py <файл.cub> [--width W] [--height H]"""

import argparse
import sys

from cub3d.errors import CubError
from cub3d.parser import parse_scene


def make_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="main.py", description="cub3D: лабиринт от первого лица")
    parser.add_argument("scene", help="файл сцены .cub")
    parser.add_argument("--width", type=int, default=960, help="ширина окна, по умолчанию 960")
    parser.add_argument("--height", type=int, default=600, help="высота окна, по умолчанию 600")
    return parser


def print_error(reason: str) -> None:
    print("Error", file=sys.stderr)
    print(reason, file=sys.stderr)


def main(argv: list[str]) -> int:
    arg_parser = make_arg_parser()
    args = arg_parser.parse_args(argv)  # при неверных аргументах argparse сам выходит с кодом 2
    if args.width <= 0 or args.height <= 0:
        arg_parser.error("размер окна должен быть положительным")

    try:
        scene = parse_scene(args.scene)
    except CubError as e:
        print_error(str(e))
        return 1
    except OSError as e:
        print_error(f"не удалось открыть {args.scene}: {e.strerror or e}")
        return 1

    # TODO: окно в feature/raycast
    print(
        f"{args.scene}: карта {scene.width}x{scene.height}, "
        f"игрок в клетке ({scene.start_x}, {scene.start_y}), взгляд {scene.start_dir}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
