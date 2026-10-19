# Spotify Album Wallpaper

Sets your Windows desktop wallpaper to the album cover of the song you are playing on Spotify, and updates it automatically when the track changes.

> Personal, non-commercial project. Not affiliated with or endorsed by Spotify.

## Features
- Updates within a few seconds of a song change
- Works with Spotify on desktop, phone or web player (any device on your account)
- Uses the full-resolution (640x640) cover art
- Two styles: `blur` (cover centred on a blurred, dimmed backdrop) and `fill` (cover cropped to fill the screen)
- Restores your original wallpaper when you quit
- Read-only access: it cannot control playback or change your library

## Requirements
- Windows 10 or 11
- Python 3.9 or newer
- A Spotify developer app. Spotify's Development Mode rules changed in 2026 (the app owner needs Premium), so check the current rules at https://developer.spotify.com

## Setup
1. Install the dependencies:
   ```
   pip install -r requirements.txt
   ```
2. Create an app at https://developer.spotify.com/dashboard
   - Redirect URI: `http://127.0.0.1:8888/callback` (use `127.0.0.1`, not `localhost`)
   - API used: Web API
3. Give the script your credentials **without editing the file**, so you never commit a secret:
   ```
   setx SPOTIPY_CLIENT_ID "your-client-id"
   setx SPOTIPY_CLIENT_SECRET "your-client-secret"
   ```
   Then close and reopen Command Prompt.
4. Run it:
   ```
   python spotify_wallpaper.py
   ```
   A browser tab opens once for you to log in. Press Ctrl+C to stop; your old wallpaper is restored.

## Run silently at login
Press `Win + R`, type `shell:startup`, and add a shortcut to:
```
pythonw "C:\path\to\spotify_wallpaper.py"
```

## Options (top of `spotify_wallpaper.py`)
| Option | Default | Meaning |
|---|---|---|
| `STYLE` | `"blur"` | `"blur"` or `"fill"` |
| `COVER_SCALE` | `0.70` | Cover size in blur style |
| `POLL_SECONDS` | `3` | How often Spotify is checked |
| `RESTORE_ON_EXIT` | `True` | Restore your old wallpaper on quit |

## Troubleshooting
- **Invalid redirect URI**: it must match the dashboard exactly: `http://127.0.0.1:8888/callback`.
- **Login says you are not registered**: add your email under *User Management* in the app's dashboard settings.
- **Nothing changes**: make sure a song is playing; ads and local files may have no cover.

## Security
Never commit your Client Secret. Keep it in environment variables. If it leaks, generate a new one in your Spotify app settings.
