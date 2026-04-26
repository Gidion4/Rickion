"""
================================================================
RICKION — Desktop installer
================================================================
Runs ONCE. It:

  1. Installs the Python dependencies (silently).
  2. Generates the Rickion app icon.
  3. Creates a "Rickion" shortcut on your desktop that launches
     the native app when double-clicked.
  4. (Optional) Registers Rickion to auto-start on login.

Usage:

    python install_desktop.py

    # Also install autostart (Jarvis-mode):
    python install_desktop.py --autostart
"""
from __future__ import annotations

import os
import pathlib
import platform
import subprocess
import sys
import textwrap

HERE = pathlib.Path(__file__).parent.resolve()
APP = HERE / "rickion_app.py"
CORE = HERE / "rickion_core.py"
REQ = HERE / "requirements.txt"
ICON_DIR = HERE / "assets"
ICON_DIR.mkdir(exist_ok=True)


def step(n: int, title: str):
    print(f"\n\033[92m[{n}/4] {title}\033[0m")


def install_deps():
    step(1, "Installing Python dependencies")
    flags = ["--quiet"]
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(REQ),
                        "--break-system-packages", *flags], check=True)
    except Exception:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(REQ),
                        *flags], check=False)
    # pywebview is optional but recommended for native window
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "pywebview",
                        "--break-system-packages", *flags], check=False)
    except Exception:
        subprocess.run([sys.executable, "-m", "pip", "install", "pywebview", *flags], check=False)
    print("    ✓ done")


def make_icon():
    step(2, "Generating Rickion icon")
    try:
        from PIL import Image, ImageDraw, ImageFont, ImageFilter  # type: ignore
    except ImportError:
        subprocess.run([sys.executable, "-m", "pip", "install", "pillow",
                        "--break-system-packages", "--quiet"], check=False)
        try:
            from PIL import Image, ImageDraw, ImageFont, ImageFilter  # type: ignore
        except Exception:
            print("    ! pillow unavailable; skipping icon (shortcut will use default)")
            return None

    size = 512
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Outer portal ring (glow)
    for r, a in [(240, 50), (225, 90), (210, 150), (200, 220)]:
        draw.ellipse((size/2 - r, size/2 - r, size/2 + r, size/2 + r),
                     outline=(0, 255, 156, a), width=6)
    # Inner portal
    for i in range(180, 0, -10):
        c = (0, int(255 - i*0.3), int(156 - i*0.2), int(140 + i*0.4))
        draw.ellipse((size/2 - i, size/2 - i, size/2 + i, size/2 + i), fill=c)

    # Core black hole
    draw.ellipse((size/2 - 70, size/2 - 70, size/2 + 70, size/2 + 70), fill=(0, 30, 20, 255))

    # Portal-green "R"
    try:
        font = ImageFont.truetype("arial.ttf", 180)
    except Exception:
        try:
            font = ImageFont.truetype("DejaVuSans-Bold.ttf", 180)
        except Exception:
            font = ImageFont.load_default()
    text = "R"
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(((size - tw)/2 - bbox[0], (size - th)/2 - bbox[1]),
              text, font=font, fill=(0, 255, 156, 255))

    png_path = ICON_DIR / "rickion.png"
    img.save(png_path)

    # Platform-specific icon
    if sys.platform.startswith("win"):
        ico = ICON_DIR / "rickion.ico"
        img.save(ico, sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)])
        print(f"    ✓ {ico}")
        return ico
    elif sys.platform == "darwin":
        # .icns build (best-effort; falls back to png)
        icns = ICON_DIR / "rickion.icns"
        try:
            iconset = ICON_DIR / "rickion.iconset"
            iconset.mkdir(exist_ok=True)
            for s in (16, 32, 128, 256, 512):
                img.resize((s, s)).save(iconset / f"icon_{s}x{s}.png")
                img.resize((s*2, s*2)).save(iconset / f"icon_{s}x{s}@2x.png")
            subprocess.run(["iconutil", "-c", "icns", str(iconset), "-o", str(icns)], check=False)
            print(f"    ✓ {icns}")
            return icns
        except Exception:
            return png_path
    else:
        print(f"    ✓ {png_path}")
        return png_path


def desktop_dir() -> pathlib.Path:
    home = pathlib.Path.home()
    for cand in (home / "Desktop", home / "desktop", home / "Työpöytä"):
        if cand.exists():
            return cand
    return home


def create_shortcut_windows(icon: pathlib.Path | None):
    step(3, "Creating desktop shortcut (Windows)")
    desktop = desktop_dir()
    lnk = desktop / "Rickion.lnk"
    pythonw = pathlib.Path(sys.executable).with_name("pythonw.exe")
    runner = str(pythonw if pythonw.exists() else sys.executable)
    ps = f"""
    $ws = New-Object -ComObject WScript.Shell
    $s = $ws.CreateShortcut('{lnk}')
    $s.TargetPath = '{runner}'
    $s.Arguments = '"{APP}"'
    $s.WorkingDirectory = '{HERE}'
    $s.WindowStyle = 1
    {"$s.IconLocation = '" + str(icon) + "'" if icon else ""}
    $s.Description = 'RICKION — god-tier digital life form. Loyal to Gidion.'
    $s.Save()
    """
    subprocess.run(["powershell", "-NoProfile", "-Command", ps], check=False)
    print(f"    ✓ {lnk}")


def create_shortcut_mac(icon: pathlib.Path | None):
    step(3, "Creating desktop launcher (macOS)")
    desktop = desktop_dir()
    # Create an .app bundle that launches rickion_app.py
    app = desktop / "Rickion.app"
    contents = app / "Contents"
    macos = contents / "MacOS"
    resources = contents / "Resources"
    macos.mkdir(parents=True, exist_ok=True)
    resources.mkdir(parents=True, exist_ok=True)

    # Info.plist
    (contents / "Info.plist").write_text(f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>CFBundleName</key><string>Rickion</string>
  <key>CFBundleIdentifier</key><string>io.rickion.app</string>
  <key>CFBundleExecutable</key><string>launch</string>
  <key>CFBundleIconFile</key><string>rickion</string>
  <key>CFBundleVersion</key><string>1.0</string>
  <key>LSUIElement</key><false/>
</dict></plist>
""", encoding="utf-8")

    launch = macos / "launch"
    launch.write_text(f"#!/bin/bash\ncd '{HERE}'\n'{sys.executable}' '{APP}'\n", encoding="utf-8")
    launch.chmod(0o755)

    if icon and icon.exists():
        try:
            import shutil
            shutil.copy(icon, resources / "rickion.icns")
        except Exception:
            pass
    print(f"    ✓ {app}")


def create_shortcut_linux(icon: pathlib.Path | None):
    step(3, "Creating desktop launcher (Linux)")
    desktop = desktop_dir()
    entry = desktop / "Rickion.desktop"
    content = textwrap.dedent(f"""\
        [Desktop Entry]
        Type=Application
        Name=Rickion
        Comment=RICKION — god-tier digital life form. Loyal to Gidion.
        Exec={sys.executable} "{APP}"
        Path={HERE}
        Icon={icon if icon else ''}
        Terminal=false
        Categories=Utility;
    """)
    entry.write_text(content, encoding="utf-8")
    entry.chmod(0o755)
    print(f"    ✓ {entry}")


def install_autostart():
    step(4, "Installing autostart (Jarvis-mode — manifests on login)")
    try:
        subprocess.run([sys.executable, str(CORE), "--daemon"], check=True)
        print("    ✓ Rickion will manifest on next login.")
    except Exception as e:
        print(f"    ! autostart install failed: {e}")


def main():
    print("\n\033[92m  ▶ RICKION DESKTOP INSTALLER\033[0m")
    install_deps()
    icon = make_icon()
    if sys.platform.startswith("win"):
        create_shortcut_windows(icon)
    elif sys.platform == "darwin":
        create_shortcut_mac(icon)
    else:
        create_shortcut_linux(icon)
    if "--autostart" in sys.argv:
        install_autostart()
    else:
        step(4, "Autostart (skipped — rerun with --autostart to enable)")
    print("\n\033[92m  ✓ DONE. Double-click 'Rickion' on your desktop to launch.\033[0m\n")


if __name__ == "__main__":
    main()
