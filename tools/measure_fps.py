"""Замер скорости: python tools/measure_fps.py <файл.cub> [--width W] [--height H] [--frames N]"""

import argparse
import platform
import sys
import time
from pathlib import Path

import pygame

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # чтобы работал import cub3d

from cub3d.camera import camera_x, ray_direction  # noqa: E402
from cub3d.errors import CubError  # noqa: E402
from cub3d.parser import parse_scene  # noqa: E402
from cub3d.player import Player, make_player, rotate_player  # noqa: E402
from cub3d.raycast import cast_ray  # noqa: E402
from cub3d.scene import Scene  # noqa: E402
from cub3d.window import Textures, draw_frame, load_textures  # noqa: E402

RAY_TRIES = 20  # сколько раз повторяем замер лучей, берём лучший
TURN_STEP = 0.05  # на сколько радиан поворачиваем игрока между кадрами


def make_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="measure_fps.py", description="Замер времени кадра")
    parser.add_argument("scene", help="файл сцены .cub")
    parser.add_argument("--width", type=int, default=960, help="ширина кадра, по умолчанию 960")
    parser.add_argument("--height", type=int, default=600, help="высота кадра, по умолчанию 600")
    parser.add_argument("--frames", type=int, default=300, help="сколько кадров, по умолчанию 300")
    return parser


def print_error(reason: str) -> None:
    print("Error", file=sys.stderr)
    print(reason, file=sys.stderr)


def measure_rays(scene: Scene, player: Player, width: int) -> float:
    """Время в секундах на width лучей без отрисовки: лучшее из нескольких попыток."""
    best = 1e9
    for _ in range(RAY_TRIES):
        start = time.perf_counter()
        for column in range(width):
            ray_x, ray_y = ray_direction(player, camera_x(column, width))
            cast_ray(scene, player.x, player.y, ray_x, ray_y)
        elapsed = time.perf_counter() - start
        if elapsed < best:
            best = elapsed
    return best


def measure_frames(
    screen: pygame.Surface, scene: Scene, player: Player, textures: Textures, frames: int
) -> list[float]:
    """Время каждого кадра в секундах: отрисовка и flip. Игрок по кругу поворачивается."""
    times = []
    for _ in range(frames):
        rotate_player(player, TURN_STEP)
        start = time.perf_counter()
        draw_frame(screen, scene, player, textures)
        pygame.display.flip()
        times.append(time.perf_counter() - start)
    return times


def print_report(args: argparse.Namespace, rays: float, times: list[float]) -> None:
    """Напечатать результаты и готовую строку таблицы для README."""
    best = min(times)
    worst = max(times)
    average = sum(times) / len(times)
    cpu = platform.processor() or platform.machine()
    machine = f"{cpu}, {platform.system()} {platform.release()}"
    python = f"Python {platform.python_version()}, pygame-ce {pygame.version.ver}"
    size = f"{args.width}x{args.height}"
    print(f"Сцена {args.scene}, {size}, кадров: {args.frames}")
    print(f"Машина: {machine}; {python}")
    print(f"{args.width} лучей без отрисовки: {rays * 1000:.1f} мс")
    print(f"Кадр (отрисовка и flip): лучший {best * 1000:.1f} мс, средний {average * 1000:.1f} мс,")
    print(f"  худший {worst * 1000:.1f} мс")
    print(f"FPS: средний {1 / average:.0f}, худший кадр {1 / worst:.0f}")
    print()
    print("| Сцена | Разрешение | Время кадра | FPS | Машина | Интерпретатор |")
    print("| --- | --- | --- | --- | --- | --- |")
    row = f"| {args.scene} | {size} | {average * 1000:.1f} мс | {1 / average:.0f} "
    print(row + f"| {machine} | {python} |")


def main(argv: list[str]) -> int:
    arg_parser = make_arg_parser()
    args = arg_parser.parse_args(argv)  # при неверных аргументах argparse сам выходит с кодом 2
    if args.width <= 0 or args.height <= 0 or args.frames <= 0:
        arg_parser.error("размер кадра и число кадров должны быть положительными")

    try:
        scene = parse_scene(args.scene)
        pygame.display.init()
        screen = pygame.display.set_mode((args.width, args.height))
        textures = load_textures(scene)
        player = make_player(scene)
        rays = measure_rays(scene, player, args.width)
        times = measure_frames(screen, scene, player, textures, args.frames)
    except (CubError, pygame.error) as e:
        print_error(str(e))
        return 1
    except OSError as e:
        print_error(f"не удалось открыть {args.scene}: {e.strerror or e}")
        return 1
    finally:
        pygame.quit()
    print_report(args, rays, times)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
