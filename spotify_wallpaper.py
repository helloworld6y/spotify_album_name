"""
Spotify Album Wallpaper for Windows
===================================
Sets your desktop wallpaper to the album cover of the song playing on Spotify
(any device on your account) and updates it whenever the song changes.

SETUP
  1. pip install spotipy pillow requests
  2. Go to https://developer.spotify.com/dashboard -> Create app
       Redirect URI:  http://127.0.0.1:8888/callback
       APIs used:     Web API
  3. Paste your Client ID / Client Secret below (or set the environment
     variables SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET).
  4. python spotify_wallpaper.py   (a browser opens once to log in)

TIP: run silently in the background with  pythonw spotify_wallpaper.py
     Press Ctrl+C in the console to stop; your old wallpaper is restored.
"""
import ctypes
import io
import os
import sys
import time
from pathlib import Path

import requests
import spotipy
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
from spotipy.oauth2 import SpotifyOAuth

# ----------------------------- CONFIG ---------------------------------------
CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID", "PASTE_CLIENT_ID_HERE")
CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET", "PASTE_CLIENT_SECRET_HERE")
REDIRECT_URI = "http://127.0.0.1:8888/callback"

POLL_SECONDS = 3          # how often to check what's playing
STYLE = "blur"            # "blur" = cover centered on a blurred backdrop
                          # "fill" = cover enlarged/cropped to fill the screen
COVER_SCALE = 0.70        # (blur style) cover size as a fraction of screen height
RESTORE_ON_EXIT = True    # put your original wallpaper back when you quit
# -----------------------------------------------------------------------------

if sys.platform != "win32":
    sys.exit("This script only works on Windows.")

user32 = ctypes.windll.user32
try:  # get real pixel resolution on scaled displays
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    pass

WORK_DIR = Path(os.environ["APPDATA"]) / "SpotifyWallpaper"
WORK_DIR.mkdir(exist_ok=True)
SPI_SETDESKWALLPAPER, SPI_GETDESKWALLPAPER = 0x0014, 0x0073


def get_current_wallpaper() -> str:
    buf = ctypes.create_unicode_buffer(260)
    user32.SystemParametersInfoW(SPI_GETDESKWALLPAPER, 260, buf, 0)
    return buf.value


def set_wallpaper(path: str) -> None:
    # 3 = SPIF_UPDATEINIFILE | SPIF_SENDCHANGE
    user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, path, 3)


def build_wallpaper(cover: Image.Image, w: int, h: int) -> Image.Image:
    cover = cover.convert("RGB")
    if STYLE == "fill":
        return ImageOps.fit(cover, (w, h), Image.LANCZOS)

    # Blurred, dimmed backdrop (blur a small copy, then scale up: fast + smooth)
    small = ImageOps.fit(cover, (max(w // 8, 1), max(h // 8, 1)), Image.LANCZOS)
    small = small.filter(ImageFilter.GaussianBlur(6))
    bg = small.resize((w, h), Image.LANCZOS)
    bg = ImageEnhance.Brightness(bg).enhance(0.55)

    size = int(h * COVER_SCALE)
    art = cover.resize((size, size), Image.LANCZOS)
    bg.paste(art, ((w - size) // 2, (h - size) // 2))
    return bg


def pick_image_url(item: dict):
    """Largest image for a track (album art) or a podcast episode."""
    images = (item.get("album") or {}).get("images") or item.get("images") \
        or (item.get("show") or {}).get("images") or []
    return images[0]["url"] if images else None  # Spotify lists largest first


def main() -> None:
    if "PASTE_" in CLIENT_ID or "PASTE_" in CLIENT_SECRET:
        sys.exit("Add your Spotify Client ID and Client Secret at the top of the script.")

    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope="user-read-currently-playing user-read-playback-state",
        cache_path=str(WORK_DIR / ".spotify_token"),
    ))

    original = get_current_wallpaper()
    last_key, flip = None, 0
    print("Running. Play something on Spotify. Ctrl+C to stop.")

    try:
        while True:
            try:
                cur = sp.current_user_playing_track()
                item = cur.get("item") if cur else None
                key = (item.get("uri") or item.get("name")) if item else None

                if item and key != last_key:
                    last_key = key
                    url = pick_image_url(item)
                    if url:
                        w, h = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
                        raw = requests.get(url, timeout=10).content
                        img = build_wallpaper(Image.open(io.BytesIO(raw)), w, h)

                        # alternate filenames so Windows never serves a cached image
                        flip ^= 1
                        out = WORK_DIR / f"wallpaper_{flip}.jpg"
                        img.save(out, quality=95)
                        set_wallpaper(str(out))
                        print(f"Now playing: {item.get('name')}")
            except Exception as e:  # network hiccup, token refresh, etc.
                print(f"Warning: {e}")
            time.sleep(POLL_SECONDS)
    except KeyboardInterrupt:
        pass
    finally:
        if RESTORE_ON_EXIT and original:
            set_wallpaper(original)
            print("Original wallpaper restored.")


if __name__ == "__main__":
    main()
