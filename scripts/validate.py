#!/usr/bin/env python3
"""Check the theme and render installed Omarchy templates in a temporary home."""
import configparser
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import tomllib

ROOT = Path(__file__).resolve().parents[1]


def luminance(color):
    channels = [int(color[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    linear = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
    return sum(c * weight for c, weight in zip(linear, (0.2126, 0.7152, 0.0722)))


def contrast(a, b):
    high, low = sorted((luminance(a), luminance(b)), reverse=True)
    return (high + 0.05) / (low + 0.05)


def main():
    colors = tomllib.loads((ROOT / "colors.toml").read_text())
    assert colors["mode"] == "light"
    for key, value in colors.items():
        if key not in ("mode", "hyprland_active_border", "hyprland_inactive_border"):
            assert re.fullmatch(r"#[0-9a-fA-F]{6}", value), key
    text_keys = ["foreground", "bright_foreground", "muted", "accent", "red", "yellow", "orange",
                 "green", "cyan", "blue", "magenta", "brown"]
    for bg in ("background", "lighter_background"):
        for fg in text_keys:
            ratio = contrast(colors[fg], colors[bg])
            assert ratio >= 4.5, f"{fg} on {bg}: {ratio:.2f}:1"
    assert contrast(colors["bright_foreground"], colors["selection"]) >= 4.5
    bar = tomllib.loads((ROOT / "shell.bar.toml").read_text())
    assert contrast(bar["text"], bar["background"]) >= 4.5
    rows = json.loads((ROOT / "wallpapers.json").read_text())
    assert len(rows) == 7
    expected = {item["slug"] + ".webp" for item in rows}
    assert {p.name for p in (ROOT / "backgrounds").iterdir()} == expected
    for name in sorted(expected):
        path = ROOT / "backgrounds" / name
        dimensions = subprocess.check_output(["magick", "identify", "-format", "%wx%h", str(path)], text=True)
        assert dimensions == "3840x2160", (name, dimensions)
        subprocess.run(["magick", str(path), "null:"], check=True)
    omarchy = Path(os.environ.get("OMARCHY_PATH", "/usr/share/omarchy"))
    assert (omarchy / "default/themed").is_dir(), "Installed Omarchy templates are required"
    with tempfile.TemporaryDirectory(prefix="luna-xp-check-") as temporary:
        home = Path(temporary)
        staging = home / ".local/state/omarchy/current/next-theme"
        staging.mkdir(parents=True)
        for name in ("colors.toml", "shell.bar.toml", "icons.theme"):
            shutil.copy2(ROOT / name, staging / name)
        env = os.environ | {"HOME": str(home), "OMARCHY_PATH": str(omarchy)}
        overrides = home / ".config/omarchy/themed"
        overrides.mkdir(parents=True)
        shutil.copy2(ROOT / "templates/foot.ini.tpl", overrides / "foot.ini.tpl")
        subprocess.run(["bash", str(omarchy / "bin/omarchy-theme-set-templates")], env=env, check=True)
        for template in (omarchy / "default/themed").glob("*.tpl"):
            rendered = staging / template.name.removesuffix(".tpl")
            text = rendered.read_text()
            assert "{{" not in text, f"Unresolved placeholder: {rendered.name}"
            if rendered.suffix == ".toml":
                tomllib.loads(text)
            elif rendered.suffix == ".json":
                json.loads(text)
        shell = tomllib.loads((staging / "shell.toml").read_text())
        assert shell["bar"]["background"] == bar["background"]
        assert "menu" in shell and "lock" in shell
        print(f"Rendered {len(list((omarchy / 'default/themed').glob('*.tpl')))} Omarchy templates successfully")
        foot = configparser.ConfigParser()
        foot.read(staging / "foot.ini")
        assert foot["main"]["initial-color-theme"] == "light"
        assert foot["colors-light"]["background"] == colors["background"].lstrip("#")
        assert foot["colors-light"]["foreground"] == colors["foreground"].lstrip("#")
        assert "colors-dark" not in foot
        if shutil.which("foot"):
            subprocess.run(["foot", "--check-config", "--config", str(staging / "foot.ini")], check=True)
        # The user template also applies when the user selects a dark theme.
        palette = staging / "colors.toml"
        palette.write_text(palette.read_text().replace('mode = "light"', 'mode = "dark"'))
        (staging / "foot.ini").unlink()
        subprocess.run(["bash", str(omarchy / "bin/omarchy-theme-set-templates")], env=env, check=True)
        dark_foot = configparser.ConfigParser()
        dark_foot.read(staging / "foot.ini")
        assert dark_foot["main"]["initial-color-theme"] == "dark"
        assert "colors-dark" in dark_foot and "colors-light" not in dark_foot
        if shutil.which("foot"):
            subprocess.run(["foot", "--check-config", "--config", str(staging / "foot.ini")], check=True)
        print("Foot light and dark mode configurations passed")
    print("Palette contrast, shell override, and all seven 4K wallpapers passed")


if __name__ == "__main__":
    main()
