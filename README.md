# Luna XP

A light Omarchy theme inspired by Windows XP Luna. Blue borders, warm gray surfaces, green accents, and seven classic wallpapers.

![Luna XP desktop](assets/preview.png)

## Install

Requires Omarchy with `colors.toml` theme templates and Omarchy Shell support. Tested with the installed Omarchy 4 development templates.

```sh
omarchy theme install https://github.com/kyryl-bogach/omarchy-luna-xp-theme
```

Select **Luna XP** in the theme menu. Use the background menu to choose another wallpaper.

This theme supplies colors, a blue bar, and the standard Yaru-blue icon selection. Omarchy generates application configurations from its templates.

## Terminal contrast

After a dark-to-light theme change, some terminal applications retain their previous colors.
Omarchy already refreshes supported applications when any theme changes, but some applications still need a restart.
If text becomes pale or input panels remain dark, restart the affected application in a new terminal window.

For Codex, use `codex resume` in the new terminal to reopen the conversation.
For OpenCode, select `system` with `/theme`; use `omarchy restart opencode` to request a configuration reload without terminating the process.
This theme does not force application restarts.

The Foot template supplied with Omarchy 4.0.4 places every palette in `[colors-dark]`.
Foot therefore reports dark mode even when Luna XP displays a light background.
The override below corrects that report. It does not refresh colors that an application retains internally.

The override in `templates/foot.ini.tpl` sets Foot's initial mode and palette section from the theme's `mode` value.
It requires Foot 1.28 or newer and applies to all Omarchy themes.
If a custom Foot template already exists, back it up before you replace it.
From this repository, run:

```sh
mkdir -p ~/.config/omarchy/themed
cp templates/foot.ini.tpl ~/.config/omarchy/themed/foot.ini.tpl
omarchy theme set luna-xp
```

Open a new Foot window after you apply the override. Existing Foot windows do not reload this configuration.

## Wallpaper selector

Open the wallpaper selector with `omarchy theme bg-switcher`.

![Luna XP wallpaper selector with seven wallpapers](assets/wallpaper-selector.webp)

The selector uses an overlapping carousel. The gallery below shows each complete wallpaper.

## Wallpapers

| Wallpaper | Preview |
| --- | --- |
| Bliss | [![Bliss](assets/wallpapers/01-bliss.webp)](backgrounds/01-bliss.webp) |
| Home | [![Home](assets/wallpapers/02-home.webp)](backgrounds/02-home.webp) |
| Red Moon Desert | [![Red Moon Desert](assets/wallpapers/03-red-moon-desert.webp)](backgrounds/03-red-moon-desert.webp) |
| Stonehenge | [![Stonehenge](assets/wallpapers/04-stonehenge.webp)](backgrounds/04-stonehenge.webp) |
| Follow | [![Follow](assets/wallpapers/05-follow.webp)](backgrounds/05-follow.webp) |
| Autumn | [![Autumn](assets/wallpapers/06-autumn.webp)](backgrounds/06-autumn.webp) |
| Azul | [![Azul](assets/wallpapers/07-azul.webp)](backgrounds/07-azul.webp) |

All seven exports are 3840 × 2160 WebP images. Export resolution does not imply native 4K detail.

| Wallpaper | Source pixels | Quality |
| --- | --- | --- |
| Bliss | 4510 × 3627 | High-resolution archive source |
| Home | 3840 × 2160 | Community AI upscale |
| Red Moon Desert | 1920 × 1200 | Enlarged |
| Stonehenge | 1920 × 1200 | Enlarged rescan derivative |
| Follow | 1920 × 1200 | Enlarged |
| Autumn | 4200 × 2800 | High-resolution archive source |
| Azul | 4341 × 2841 | High-resolution archive source |

The exports use an sRGB conversion and a centered crop. Portrait displays and wider displays can crop more of each photograph.

See [SOURCES.md](SOURCES.md) for download links, credits, and asset rights. Source checksums are in [wallpapers.json](wallpapers.json).

## Rebuild

Requires Python 3.11+, ImageMagick, and an sRGB ICC profile. The default profile comes from Ghostscript on Arch Linux.

```sh
python scripts/build-wallpapers.py --download
python scripts/validate.py
```

Source files stay in the ignored `.masters/` directory. The validator requires an installed Omarchy tree.

For other display ratios, export from the source files to avoid a second crop:

```sh
python scripts/build-wallpapers.py --download --aspect 16:10
python scripts/build-wallpapers.py --download --aspect 21:9
```

These exports go into `.exports/`. Copy the desired files into your Omarchy background directory.

## License

The MIT license covers original theme configurations, scripts, and documentation. It excludes wallpaper photographs and their depictions in screenshots.

The photographs remain third-party works. The source archives do not establish a redistribution license. This project has no Microsoft affiliation.
