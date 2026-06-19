# DevShare / DevServe

A small cross-platform local file server for **secure LAN file sharing** with a browser UI.

Share files between devices on the same network using a host PIN and time-limited share links. Guests can download (and upload to shared folders) without full access to your files.

## Requirements

- Python 3.10 or newer
- Works on Windows, macOS, and Linux

## Install

From the repository root:

```bash
python -m pip install -e .
```

If you use a virtual environment, activate it first:

Windows:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
```

macOS/Linux:

```bash
source .venv/bin/activate
python -m pip install -e .
```

## Run

```bash
devshare --dir . --port 8080 --theme dark --title "DevShare Pro"
```

On startup, DevShare prints:

- Local and LAN URLs (e.g. `http://192.168.1.5:8080`)
- A **6-digit host PIN** (auto-generated unless you set one)

Open the LAN URL on another phone or laptop. Use the PIN for full host access, or open a **share link** for guest-only access.

### Set your own PIN

```bash
devshare --dir ./shared --port 8080 --pin 482910
```

### Disable PIN (not recommended on open networks)

```bash
devshare --no-auth --dir .
```

## How sharing works

1. **Host** runs `devshare` and opens the app in a browser.
2. Enter the PIN shown in the terminal to unlock host controls.
3. Select a file or folder and click **Share** to create a link like:
   `http://192.168.1.5:8080/s/abc123xyz`
4. Send that link to another device on the same Wi‑Fi/LAN.
5. **Guests** open the link — no PIN needed. They can:
   - Download the shared file or browse the shared folder
   - Upload files into a shared **folder** (if enabled)

Share links expire after 24 hours by default.

## Options

- `--host`: Bind address (default `0.0.0.0`)
- `--port`: Port number (default `8080`)
- `--dir`: Folder to serve (default `.`)
- `--theme`: `dark` or `light` (default `dark`)
- `--title`: Browser title
- `--pin`: Host access PIN (default: auto-generated 6-digit)
- `--no-auth`: Disable PIN protection
- `--share-expires`: Share link lifetime in hours (default `24`, use `0` for no expiry)

## Notes

- The project is pure Python and uses only standard libraries.
- Host sessions and share tokens are kept in memory (reset when the server restarts).
- For Python 3.13+ compatibility, the upload endpoint uses a custom multipart parser instead of the deprecated `cgi` module.
