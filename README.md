# DevShare / DevServe

A small cross-platform local file server with a browser UI for browsing, previewing, downloading, and managing files.

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

### From installed package

```bash
devshare --dir . --port 8080 --theme dark --title "DevServe Pro"
```

### Without installing

```bash
python -m devserve --dir . --port 8080 --theme dark --title "DevServe Pro"
```

Then open:

```
http://localhost:8080
```

## Options

- `--host`: Bind address (default `0.0.0.0`)
- `--port`: Port number (default `8080`)
- `--dir`: Folder to serve (default `.`)
- `--theme`: `dark` or `light` (default `dark`)
- `--title`: Browser title

## Notes

- The project is pure Python and uses only standard libraries.
- It should run on any platform where Python 3.10+ is available.
- For Python 3.13+ compatibility, the upload endpoint now uses a custom multipart parser instead of the deprecated `cgi` module.
