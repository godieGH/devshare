from __future__ import annotations

import io
import json
import base64
try:
    import qrcode
    try:
        from qrcode.image.svg import SvgImage
    except Exception:
        SvgImage = None
except Exception:
    qrcode = None
    SvgImage = None
import os
import shutil
import zipfile
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

from .auth import SESSION_COOKIE, SHARE_COOKIE, AuthManager
from .ui import render_login_page, render_page, render_share_page
from .utils import (
    file_kind,
    format_mtime,
    guess_mime,
    human_size,
    join_rel,
    safe_join,
    share_allows_path,
)


class DevServeHandler(BaseHTTPRequestHandler):
    root_dir = os.getcwd()
    theme = "dark"
    title = "DevServe"
    version = "0.0.0"
    port = 8080
    auth_manager: AuthManager | None = None

    def log_message(self, format, *args):
        print(f"{self.address_string()} - {format % args}")

    def _cookie_value(self, name: str) -> str | None:
        raw = self.headers.get("Cookie", "")
        prefix = name + "="
        for part in raw.split(";"):
            part = part.strip()
            if part.startswith(prefix):
                return part[len(prefix):]
        return None

    def _set_cookie(self, name: str, value: str, max_age: int | None = None) -> None:
        parts = [f"{name}={value}", "Path=/", "HttpOnly", "SameSite=Strict"]
        if max_age is not None:
            parts.append(f"Max-Age={max_age}")
        self.send_header("Set-Cookie", "; ".join(parts))

    def _clear_cookie(self, name: str) -> None:
        self.send_header("Set-Cookie", f"{name}=; Path=/; Max-Age=0; HttpOnly; SameSite=Strict")

    def _session_token(self) -> str | None:
        return self._cookie_value(SESSION_COOKIE)

    def _share_token(self) -> str | None:
        return self._cookie_value(SHARE_COOKIE)

    def _is_host(self) -> bool:
        manager = self.auth_manager
        if manager is None or not manager.auth_enabled:
            return True
        return manager.validate_session(self._session_token())

    def _active_share(self):
        manager = self.auth_manager
        if manager is None:
            return None
        return manager.get_share(self._share_token())

    def _json(self, data, code=200, extra_headers=None):
        payload = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        if extra_headers:
            for key, value in extra_headers.items():
                self.send_header(key, value)
        self.end_headers()
        self.wfile.write(payload)

    def _text(self, text, code=200, content_type="text/plain; charset=utf-8", extra_headers=None):
        payload = text.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(payload)))
        if extra_headers:
            for key, value in extra_headers.items():
                self.send_header(key, value)
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
        content_type = self.headers.get("Content-Type", "")
        if "boundary=" not in content_type:
            return []

        boundary = content_type.split("boundary=")[1].split(";")[0].encode()
        body = self.rfile.read(int(self.headers.get("Content-Length", 0)))

        files = []
        parts = body.split(b"--" + boundary)

        for part in parts[1:-1]:
            if not part.strip():
                continue

            header_end = part.find(b"\r\n\r\n")
            if header_end == -1:
                continue

            headers_section = part[:header_end].decode("utf-8", errors="ignore")
            content = part[header_end + 4:]
            if content.endswith(b"\r\n"):
                content = content[:-2]

            filename = None
            for line in headers_section.split("\r\n"):
                if "filename=" in line:
                    filename = line.split('filename="')[1].split('"')[0]
                    break

            if filename:
                files.append({
                    "filename": filename,
                    "content": io.BytesIO(content),
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

    def _share_root_info(self, share):
        full = safe_join(self.root_dir, share.path)
        if not full or not os.path.exists(full):
            return None, None, "Shared item not found"
        is_file = os.path.isfile(full)
        return full, is_file, None

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

    def _file_item(self, rel: str):
        full = safe_join(self.root_dir, rel)
        if not full or not os.path.isfile(full):
            return None
        stat = os.stat(full)
        mime = guess_mime(full)
        kind = file_kind(full, mime)
        return {
            "name": os.path.basename(full),
            "path": rel.replace("\\", "/"),
            "type": "file",
            "kind": kind,
            "size": stat.st_size,
            "size_h": human_size(stat.st_size),
            "mtime": int(stat.st_mtime),
            "mtime_h": format_mtime(stat.st_mtime),
        }

    def _serve_home(self, current_path=""):
        if not self._is_host():
            self.send_response(302)
            self.send_header("Location", "/login")
            self.end_headers()
            return

        html = render_page(
            title=self.title,
            version=self.version,
            theme=self.theme,
            current_path=current_path,
            auth_enabled=self.auth_manager.auth_enabled if self.auth_manager else False,
        )
        self._text(html, content_type="text/html; charset=utf-8")

    def _serve_login(self):
        if self._is_host():
            self.send_response(302)
            self.send_header("Location", "/")
            self.end_headers()
            return

        html = render_login_page(title=self.title, theme=self.theme)
        self._text(html, content_type="text/html; charset=utf-8")

    def _serve_share_page(self, token: str):
        share = self.auth_manager.get_share(token) if self.auth_manager else None
        if not share:
            self._text("Share link not found or expired.", 404)
            return

        full, is_file, error = self._share_root_info(share)
        if error:
            self._text(error, 404)
            return

        name = os.path.basename(full.rstrip("/\\")) or share.path
        requires_password = getattr(share, "password_hash", None) is not None
        html = render_share_page(
            title=self.title,
            theme=self.theme,
            token=token,
            name=name,
            is_file=is_file,
            allow_upload=share.allow_upload and not is_file,
            requires_password=requires_password,
        )

        def write_html():
            self.wfile.write(html.encode("utf-8"))

        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(html.encode("utf-8"))))
        # Only set guest cookie automatically when the share has no password
        if not requires_password:
            self._set_cookie(SHARE_COOKIE, token, max_age=86400)
        self.end_headers()
        write_html()

    def _require_host(self) -> bool:
        if self._is_host():
            return True
        self._json({"error": "Unauthorized"}, 401)
        return False

    def _require_share(self):
        share = self._active_share()
        if share is None:
            self._json({"error": "Invalid or expired share link"}, 403)
            return None
        full, is_file, error = self._share_root_info(share)
        if error:
            self._json({"error": error}, 404)
            return None
        return share, full, is_file

    def do_GET(self):
        path, qs = self._query()

        if path == "/login":
            self._serve_login()
            return

        if path.startswith("/s/"):
            token = path[3:].strip("/").split("/")[0]
            self._serve_share_page(token)
            return

        if path == "/":
            self._serve_home(self._get_rel(qs))
            return

        if path == "/api/session":
            self._json({
                "authenticated": self._is_host(),
                "auth_enabled": self.auth_manager.auth_enabled if self.auth_manager else False,
            })
            return

        if path == "/api/info":
            if not self._require_host():
                return
            from .utils import get_lan_addresses

            self._json({
                "urls": get_lan_addresses(self.port),
                "port": self.port,
                "auth_enabled": self.auth_manager.auth_enabled if self.auth_manager else False,
            })
            return

        if path.startswith("/api/guest/"):
            ctx = self._require_share()
            if ctx is None:
                return
            share, _full, is_file = ctx
            return self._handle_guest_get(path, qs, share, is_file)

        if not self._require_host():
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

            if kind == "audio":
                self._json({
                    "kind": "audio",
                    "name": os.path.basename(full),
                    "url": f"/api/file?path={rel}",
                    "mime": mime,
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

    def _handle_guest_get(self, path, qs, share, is_file):
        rel = self._get_rel(qs)

        if path == "/api/guest/info":
            self._json({
                "name": os.path.basename(share.path) or share.path,
                "path": share.path,
                "is_file": is_file,
                "allow_upload": share.allow_upload and not is_file,
                "expires_at": share.expires_at,
            })
            return

        if not share_allows_path(share.path, rel, is_file):
            self._json({"error": "Access denied"}, 403)
            return

        if path == "/api/guest/list":
            if is_file:
                item = self._file_item(share.path)
                self._json({"path": "", "items": [item] if item else []})
                return

            list_rel = rel or share.path
            items, error = self._list_dir(list_rel)
            if error:
                self._json({"error": error}, 404)
                return
            self._json({"path": list_rel, "items": items})
            return

        if path == "/api/guest/file":
            file_rel = share.path if is_file else rel
            if not file_rel:
                self._json({"error": "File required"}, 400)
                return

            full = safe_join(self.root_dir, file_rel)
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

        if path == "/api/guest/zip":
            if is_file:
                self._json({"error": "Not a folder"}, 400)
                return

            zip_rel = rel or share.path
            full = safe_join(self.root_dir, zip_rel)
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

        if path == "/api/guest/auth":
            body = self._read_json_body()
            token = (body.get("token") or "").strip()
            password = body.get("password")
            manager = self.auth_manager
            if manager and manager.verify_share_password(token, password):
                self.send_response(200)
                self._set_cookie(SHARE_COOKIE, token, max_age=86400)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"ok": True}).encode("utf-8"))
                return
            self._json({"error": "Invalid token or password"}, 401)
            return

        if path == "/api/login":
            body = self._read_json_body()
            pin = (body.get("pin") or "").strip()
            manager = self.auth_manager
            if manager is None or not manager.auth_enabled:
                self._json({"ok": True})
                return

            if not manager.verify_pin(pin):
                self._json({"error": "Invalid PIN"}, 401)
                return

            token = manager.create_session()

            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self._set_cookie(SESSION_COOKIE, token, max_age=86400)
            self.end_headers()
            self.wfile.write(json.dumps({"ok": True}).encode("utf-8"))
            return

        if path == "/api/logout":
            manager = self.auth_manager
            if manager:
                manager.revoke_session(self._session_token())

            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self._clear_cookie(SESSION_COOKIE)
            self.end_headers()
            self.wfile.write(b'{"ok":true}')
            return

        if path.startswith("/api/guest/"):
            ctx = self._require_share()
            if ctx is None:
                return
            share, _full, is_file = ctx
            return self._handle_guest_post(path, qs, share, is_file)

        if not self._require_host():
            return

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

        if path == "/api/share":
            rel = (body.get("path") or "").replace("\\", "/").lstrip("/")
            full = safe_join(self.root_dir, rel)
            if not full or not os.path.exists(full):
                self._json({"error": "Not found"}, 404)
                return

            allow_upload = bool(body.get("allow_upload", True))
            if os.path.isfile(full):
                allow_upload = False

            password = body.get("password")
            if password:
                link = self.auth_manager.create_share_with_password(rel, password=password, allow_upload=allow_upload)
            else:
                link = self.auth_manager.create_share(rel, allow_upload=allow_upload)
            host = self.headers.get("Host", f"localhost:{self.port}")
            url = f"http://{host}/s/{link.token}"

            # Theme-aware QR colors
            req_theme = body.get("theme", self.theme or "dark")
            if req_theme == "dark":
                qr_fill, qr_back = "#ffffff", "transparent"
                png_fill, png_back = "white", "black"
            else:
                qr_fill, qr_back = "#0f172a", "#ffffff"
                png_fill, png_back = "black", "white"

            qr_data = None
            if qrcode is not None and SvgImage is not None:
                try:
                    img = qrcode.make(url, image_factory=SvgImage)
                    buf = io.BytesIO()
                    img.save(buf)
                    svg = buf.getvalue().decode("utf-8")
                    svg = svg.replace('fill="#000000"', f'fill="{qr_fill}"')
                    svg = svg.replace('fill="#ffffff"', f'fill="{qr_back}"')
                    svg = svg.replace('fill="black"', f'fill="{qr_fill}"')
                    svg = svg.replace('fill="white"', f'fill="{qr_back}"')
                    qr_data = "data:image/svg+xml;base64," + base64.b64encode(svg.encode("utf-8")).decode("ascii")
                except Exception:
                    qr_data = None
            elif qrcode is not None:
                try:
                    qr = qrcode.QRCode()
                    qr.add_data(url)
                    qr.make(fit=True)
                    img = qr.make_image(fill_color=png_fill, back_color=png_back)
                    buf = io.BytesIO()
                    img.save(buf, format="PNG")
                    qr_data = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("ascii")
                except Exception:
                    qr_data = None
            payload = {
                "ok": True,
                "token": link.token,
                "url": url,
                "expires_at": link.expires_at,
                "allow_upload": link.allow_upload,
            }
            if qr_data:
                payload["qr"] = qr_data
            self._json(payload)
            return

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

    def _handle_guest_post(self, path, qs, share, is_file):
        if path != "/api/guest/upload":
            self._json({"error": "Not found"}, 404)
            return

        if is_file or not share.allow_upload:
            self._json({"error": "Upload not allowed"}, 403)
            return

        rel_dir = self._get_rel(qs) or share.path
        if not share_allows_path(share.path, rel_dir, is_file=False):
            self._json({"error": "Access denied"}, 403)
            return

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