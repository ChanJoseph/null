#!/usr/bin/env python3
"""Inspect a photo, or apply a light grade when the picture must not be redrawn."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ASPECTS = {
    "1:1": 1.0,
    "4:3": 4 / 3,
    "3:4": 3 / 4,
    "16:9": 16 / 9,
    "9:16": 9 / 16,
}


def nearest_aspect(width: int, height: int) -> str:
    ratio = width / height
    return min(ASPECTS, key=lambda name: abs(ratio - ASPECTS[name]))


def require_pillow():
    try:
        from PIL import Image, ImageEnhance, ImageOps
    except ImportError:
        print("缺少 Pillow。先运行: python3 -m pip install pillow", file=sys.stderr)
        raise SystemExit(1)
    return Image, ImageEnhance, ImageOps


def open_image(path: Path):
    Image, _, ImageOps = require_pillow()
    with Image.open(path) as image:
        image = ImageOps.exif_transpose(image)
        image.load()
        return image


def output_path(source: Path) -> Path:
    stem = source.stem
    suffix = ".jpg" if source.suffix.lower() in {".jpg", ".jpeg"} else ".png"
    candidate = source.with_name(f"{stem}-beauty{suffix}")
    index = 2
    while candidate.exists():
        candidate = source.with_name(f"{stem}-beauty-{index}{suffix}")
        index += 1
    return candidate


def channel_mean(histogram: list[int]) -> float:
    total = sum(histogram)
    if total == 0:
        return 0.0
    return sum(index * count for index, count in enumerate(histogram)) / total


def gray_world(image, strength: float):
    Image, _, _ = require_pillow()
    rgb = image.convert("RGB")
    histogram = rgb.histogram()
    means = [channel_mean(histogram[band * 256 : (band + 1) * 256]) for band in range(3)]
    gray = sum(means) / 3
    scales = [1 + strength * ((gray / value) - 1) if value else 1 for value in means]
    channels = [
        channel.point(lambda value, scale=scale: max(0, min(255, int(value * scale))))
        for channel, scale in zip(rgb.split(), scales)
    ]
    balanced = Image.merge("RGB", channels)
    if image.mode == "RGBA":
        balanced.putalpha(image.getchannel("A"))
    return balanced


def warm(image):
    Image, _, _ = require_pillow()
    rgb = image.convert("RGB")
    red, green, blue = rgb.split()
    red = red.point(lambda value: min(255, int(value * 1.04)))
    blue = blue.point(lambda value: min(255, int(value * 0.97)))
    warmed = Image.merge("RGB", (red, green, blue))
    if image.mode == "RGBA":
        warmed.putalpha(image.getchannel("A"))
    return warmed


def command_info(path: Path) -> None:
    image = open_image(path)
    width, height = image.size
    print(
        json.dumps(
            {
                "width": width,
                "height": height,
                "aspect_ratio": nearest_aspect(width, height),
            },
            ensure_ascii=False,
        )
    )


def command_grade(path: Path) -> None:
    _, ImageEnhance, ImageOps = require_pillow()
    image = open_image(path)
    image = ImageOps.autocontrast(image, cutoff=0.4)
    image = gray_world(image, strength=0.4)
    image = warm(image)
    image = ImageEnhance.Brightness(image).enhance(1.03)
    image = ImageEnhance.Contrast(image).enhance(1.06)
    image = ImageEnhance.Color(image).enhance(1.08)
    image = ImageEnhance.Sharpness(image).enhance(1.15)
    destination = output_path(path)
    if destination.suffix == ".jpg":
        image.convert("RGB").save(destination, quality=92, optimize=True)
    else:
        image.save(destination)
    print(destination)


def main() -> None:
    parser = argparse.ArgumentParser(description="查看照片比例，或做不重画的轻度调色。")
    subcommands = parser.add_subparsers(dest="command", required=True)
    for name in ("info", "grade"):
        command = subcommands.add_parser(name)
        command.add_argument("image", type=Path)
    args = parser.parse_args()
    if not args.image.is_file():
        print(f"找不到图片: {args.image}", file=sys.stderr)
        raise SystemExit(1)
    if args.command == "info":
        command_info(args.image)
    else:
        command_grade(args.image)


if __name__ == "__main__":
    main()
