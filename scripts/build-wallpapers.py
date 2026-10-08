#!/usr/bin/env python3
"""Prepare reproducible wallpaper exports from verified source files."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
SIZES = {"16:9": "3840x2160", "16:10": "3840x2400", "21:9": "3440x1440"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--download", action="store_true", help="Download missing source files")
    parser.add_argument("--aspect", choices=SIZES, default="16:9")
    parser.add_argument("--srgb-profile", type=Path, default=Path("/usr/share/ghostscript/iccprofiles/srgb.icc"))
    args = parser.parse_args()
    if not shutil.which("magick"):
        parser.error("ImageMagick is required")
    if not args.srgb_profile.is_file():
        parser.error("Supply an sRGB ICC profile with --srgb-profile")
    size = SIZES[args.aspect]
    output = ROOT / ("backgrounds" if args.aspect == "16:9" else f".exports/{size}")
    output.mkdir(parents=True, exist_ok=True)
    masters = ROOT / ".masters"
    masters.mkdir(exist_ok=True)
    for item in json.loads((ROOT / "wallpapers.json").read_text()):
        source = masters / item["source_file"]
        if not source.exists():
            if not args.download:
                parser.error(f"Missing {source.name}; use --download to fetch it")
            request = urllib.request.Request(item["url"], headers={"User-Agent": "Luna-XP-wallpapers/1.0"})
            with urllib.request.urlopen(request, timeout=60) as response:
                data = response.read()
            if hashlib.sha256(data).hexdigest() != item["sha256"]:
                raise SystemExit(f"Source checksum mismatch: {source.name}")
            source.write_bytes(data)
        if hashlib.sha256(source.read_bytes()).hexdigest() != item["sha256"]:
            raise SystemExit(f"Source checksum mismatch: {source.name}")
        destination = output / (item["slug"] + ".webp")
        temporary = destination.with_suffix(".tmp.webp")
        try:
            subprocess.run([
                "magick", str(source), "-auto-orient", "-profile", str(args.srgb_profile),
                "-filter", "Lanczos", "-resize", size + "^", "-gravity", item["gravity"],
                "-extent", size, "-strip", "-quality", "92", "-define", "webp:method=6",
                "-define", "webp:use-sharp-yuv=true", str(temporary),
            ], check=True)
            temporary.replace(destination)
        finally:
            temporary.unlink(missing_ok=True)
        print(f"{destination.relative_to(ROOT)}: {item['quality']}")


if __name__ == "__main__":
    main()
