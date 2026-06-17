from __future__ import annotations

import io
import json
import mimetypes
import os
import shutil
import zipfile
from email import message_from_bytes
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

from .ui import render_page
from .utils import (
    file_kind,
    format_mtime,
    guess_mime,
    human_size,
    join_rel,
    rel_path,
    safe_join,
)


class DevServeHandler(BaseHTTPRequestHandler):
    root_dir = os.getcwd()
    theme = "dark"
    title = "DevServe"
    version = "0.0.0"

    def log_message(self, format, *args):
        print(f"{self.address_string()} - {format % args}")

    def _json(self, data, code=200):
        payload = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def _text(self, text, code=200, content_type="text/plain; charset=utf-8"):
        payload = text.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def _bytes(self, data, code=200, content_type="application/octet-stream", headers=None):
        headers = headers or {}
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        for key, value in headers.items():
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(data)

    def _parse_multipart_form(self):
        """Parse multipart form data without using deprecated cgi module."""
        content_type = self.headers.get("Content-Type", "")
        if "boundary=" not in content_type:
            return []

        boundary = content_type.split("boundary=")[1].split(";")[0].encode()
        body = self.rfile.read(int(self.headers.get("Content-Length", 0)))

        files = []
        parts = body.split(b"--" + boundary)

        for part in parts[1:-1]:  # Skip first (empty) and last (closing boundary)
            if not part.strip():
                continue

            header_end = part.find(b"\r\n\r\n")
            if header_end == -1:
                continue

            headers_section = part[:header_end].decode("utf-8", errors="ignore")
            content = part[header_end + 4:]
            if content.endswith(b"\r\n"):
                content = content[:-2]

            # Extract filename from Content-Disposition header
            filename = None
            for line in headers_section.split("\r\n"):
                if "filename=" in line:
                    filename = line.split('filename="')[1].split('"')[0]
                    break

            if filename:
                files.append({
                    "filename": filename,
                    "content": io.BytesIO(content)
                })

        return files

    def _query(self):
        parsed = urlparse(self.path)
        return parsed.path, parse_qs(parsed.query)

    def _read_json_body(self):
        length = int(self.headers.get("Content-Length", "0") or 0)
        raw = self.rfile.read(length) if length else b"{}"
        try:
            return json.loads(raw.decode("utf-8"))
        except Exception:
            return {}

    def _get_rel(self, qs, key="path"):
        return qs.get(key, [""])[0] or ""

    def _list_dir(self, rel_dir):
        full = safe_join(self.root_dir, rel_dir)
        if not full or not os.path.isdir(full):
            return None, "Folder not found"

        items = []
        try:
            with os.scandir(full) as it:
                for entry in it:
                    if entry.name.startswith("."):
                        continue
                    stat = entry.stat(follow_symlinks=False)
                    abs_path = entry.path
                    mime = guess_mime(abs_path)
                    kind = "dir" if entry.is_dir(follow_symlinks=False) else file_kind(abs_path, mime)
                    items.append({
                        "name": entry.name,
                        "path": join_rel(rel_dir, entry.name),
                        "type": "dir" if kind == "dir" else "file",
                        "kind": kind,
                        "size": stat.st_size if entry.is_file(follow_symlinks=False) else 0,
                        "size_h": human_size(stat.st_size if entry.is_file(follow_symlinks=False) else 0),
                        "mtime": int(stat.st_mtime),
                        "mtime_h": format_mtime(stat.st_mtime),
                    })
        except OSError:
            return None, "Cannot read folder"

        items.sort(key=lambda x: (x["type"] != "dir", x["name"].lower()))
        return items, None

    def _serve_home(self, current_path=""):
        html = render_page(
            title=self.title,
            version=self.version,
            theme=self.theme,
            current_path=current_path,
        )
        self._text(html, content_type="text/html; charset=utf-8")

    def do_GET(self):
        path, qs = self._query()

        if path == "/":
            self._serve_home(self._get_rel(qs))
            return

        if path == "/api/list":
            rel = self._get_rel(qs)
            items, error = self._list_dir(rel)
            if error:
                self._json({"error": error}, 404)
                return
            self._json({"path": rel, "items": items})
            return

        if path == "/api/preview":
            rel = self._get_rel(qs)
            full = safe_join(self.root_dir, rel)
            if not full or not os.path.exists(full):
                self._json({"error": "Not found"}, 404)
                return

            if os.path.isdir(full):
                items, _ = self._list_dir(rel)
                names = [item["name"] for item in (items or [])[:12]]
                self._json({
                    "kind": "dir",
                    "name": os.path.basename(full) or "/",
                    "count": len(items or []),
                    "items": names,
                })
                return

            mime = guess_mime(full)
            kind = file_kind(full, mime)

            if kind == "image":
                self._json({
                    "kind": "image",
                    "name": os.path.basename(full),
                    "url": f"/api/file?path={rel}",
                })
                return

            if kind == "text":
                try:
                    with open(full, "rb") as f:
                        data = f.read(250_000)
                    text = data.decode("utf-8", errors="replace")
                except OSError:
                    self._json({"error": "Cannot read file"}, 500)
                    return

                self._json({
                    "kind": "text",
                    "name": os.path.basename(full),
                    "content": text,
                    "truncated": os.path.getsize(full) > 250_000,
                })
                return

            self._json({
                "kind": "binary",
                "name": os.path.basename(full),
                "size_h": human_size(os.path.getsize(full)),
            })
            return

        if path == "/api/file":
            rel = self._get_rel(qs)
            full = safe_join(self.root_dir, rel)
            if not full or not os.path.isfile(full):
                self._json({"error": "File not found"}, 404)
                return

            mime = guess_mime(full)
            download = qs.get("download", ["0"])[0] == "1"
            headers = {}

            if download or file_kind(full, mime) == "binary":
                headers["Content-Disposition"] = f'attachment; filename="{os.path.basename(full)}"'

            try:
                with open(full, "rb") as f:
                    data = f.read()
            except OSError:
                self._json({"error": "Cannot read file"}, 500)
                return

            self._bytes(data, content_type=mime, headers=headers)
            return

        if path == "/api/zip":
            rel = self._get_rel(qs)
            full = safe_join(self.root_dir, rel)
            if not full or not os.path.isdir(full):
                self._json({"error": "Folder not found"}, 404)
                return

            buf = io.BytesIO()
            with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
                for root, _, files in os.walk(full):
                    for filename in files:
                        fp = os.path.join(root, filename)
                        arc = os.path.relpath(fp, full)
                        zf.write(fp, arcname=arc)

            zip_bytes = buf.getvalue()
            zip_name = os.path.basename(full.rstrip("/\\")) or "folder"
            self._bytes(
                zip_bytes,
                content_type="application/zip",
                headers={"Content-Disposition": f'attachment; filename="{zip_name}.zip"'},
            )
            return

        self._json({"error": "Not found"}, 404)

    def do_POST(self):
        path, qs = self._query()

        if path == "/api/upload":
            rel_dir = self._get_rel(qs)
            target_dir = safe_join(self.root_dir, rel_dir)
            if not target_dir or not os.path.isdir(target_dir):
                self._json({"error": "Folder not found"}, 404)
                return

            files = self._parse_multipart_form()

            saved = []
            for file_info in files:
                name = os.path.basename(file_info["filename"])
                dest = os.path.join(target_dir, name)
                try:
                    with open(dest, "wb") as out:
                        file_info["content"].seek(0)
                        shutil.copyfileobj(file_info["content"], out)
                    saved.append(name)
                except OSError:
                    self._json({"error": f"Cannot save {name}"}, 500)
                    return

            self._json({"ok": True, "saved": saved})
            return

        body = self._read_json_body()

        if path == "/api/delete":
            rel = body.get("path", "")
            full = safe_join(self.root_dir, rel)
            if not full or not os.path.exists(full):
                self._json({"error": "Not found"}, 404)
                return

            if os.path.isdir(full):
                try:
                    shutil.rmtree(full)
                except OSError:
                    self._json({"error": "Cannot delete folder"}, 500)
                    return
            else:
                try:
                    os.remove(full)
                except OSError:
                    self._json({"error": "Cannot delete file"}, 500)
                    return

            self._json({"ok": True})
            return

        if path == "/api/rename":
            rel = body.get("path", "")
            new_name = os.path.basename((body.get("name") or "").strip())
            if not new_name:
                self._json({"error": "New name is required"}, 400)
                return

            full = safe_join(self.root_dir, rel)
            if not full or not os.path.exists(full):
                self._json({"error": "Not found"}, 404)
                return

            parent = os.path.dirname(full)
            dest = os.path.join(parent, new_name)

            try:
                os.rename(full, dest)
            except OSError:
                self._json({"error": "Rename failed"}, 500)
                return

            self._json({"ok": True})
            return

        if path == "/api/mkdir":
            rel_dir = body.get("path", "")
            name = os.path.basename((body.get("name") or "").strip())
            if not name:
                self._json({"error": "Folder name is required"}, 400)
                return

            parent = safe_join(self.root_dir, rel_dir)
            if not parent or not os.path.isdir(parent):
                self._json({"error": "Folder not found"}, 404)
                return

            target = os.path.join(parent, name)
            try:
                os.makedirs(target, exist_ok=False)
            except FileExistsError:
                self._json({"error": "Folder already exists"}, 409)
                return
            except OSError:
                self._json({"error": "Cannot create folder"}, 500)
                return

            self._json({"ok": True})
            return

        self._json({"error": "Not found"}, 404)