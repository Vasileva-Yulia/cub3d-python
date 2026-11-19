"""Нарисовать один кадр сцены в PNG без окна: python tools/render_png.py <файл.cub> <out.png>"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # чтобы работал import cub3d

from cub3d.errors import CubError  # noqa: E402
from cub3d.parser import parse_scene  # noqa: E402
from cub3d.window import save_frame  # noqa: E402


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("Использование: python tools/render_png.py <файл.cub> <out.png>", file=sys.stderr)
        return 2
    try:
        scene = parse_scene(argv[0])
        save_frame(scene, argv[1], 960, 600)
    except (CubError, OSError) as e:
        print("Error", file=sys.stderr)
        print(e, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
