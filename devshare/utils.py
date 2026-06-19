from __future__ import annotations

import os
import mimetypes
import socket
from datetime import datetime


TEXT_EXTS = {
    ".txt", ".md", ".py", ".js", ".mjs", ".cjs", ".json", ".html", ".htm",
    ".css", ".xml", ".yml", ".yaml", ".toml", ".ini", ".cfg", ".csv",
    ".rs", ".go", ".java", ".c", ".h", ".cpp", ".hpp", ".ts", ".tsx", ".jsx",
    ".sh", ".bat", ".ps1", ".sql", ".log"
}


def safe_join(root: str, rel_path: str) -> str | None:
    root_real = os.path.realpath(root)
    rel_path = (rel_path or "").replace("\\", "/").lstrip("/")
    candidate = os.path.realpath(os.path.join(root_real, rel_path))
    try:
        if os.path.commonpath([root_real, candidate]) != root_real:
            return None
    except ValueError:
        return None
    return candidate


def rel_path(root: str, full_path: str) -> str:
    rel = os.path.relpath(full_path, root)
    return "" if rel == "." else rel.replace(os.sep, "/")


def join_rel(base: str, name: str) -> str:
    base = (base or "").replace("\\", "/").strip("/")
    return name if not base else base + "/" + name


def human_size(num_bytes: int) -> str:
    num = float(num_bytes or 0)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if num < 1024.0:
            return f"{num:.0f} {unit}" if unit == "B" else f"{num:.1f} {unit}"
        num /= 1024.0
    return f"{num:.1f} PB"


def format_mtime(ts: float) -> str:
    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M")


def guess_mime(path: str) -> str:
    mime, _ = mimetypes.guess_type(path)
    return mime or "application/octet-stream"


def file_kind(path: str, mime: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    if os.path.isdir(path):
        return "dir"
    if mime.startswith("image/"):
        return "image"
    if mime.startswith("text/") or ext in TEXT_EXTS or mime in {
        "application/json",
        "application/xml",
        "application/javascript",
    }:
        return "text"
    return "binary"


def get_lan_addresses(port: int) -> list[str]:
    urls: list[str] = []
    seen: set[str] = set()

    def add(ip: str) -> None:
        if ip.startswith("127.") or ip in seen:
            return
        seen.add(ip)
        urls.append(f"http://{ip}:{port}")

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.connect(("8.8.8.8", 80))
            add(sock.getsockname()[0])
    except OSError:
        pass

    try:
        hostname = socket.gethostname()
        for info in socket.getaddrinfo(hostname, None, socket.AF_INET):
            add(info[4][0])
    except OSError:
        pass

    if not urls:
        urls.append(f"http://127.0.0.1:{port}")
    return urls


def share_allows_path(share_path: str, rel_path: str, is_file_share: bool) -> bool:
    share_path = (share_path or "").replace("\\", "/").strip("/")
    rel_path = (rel_path or "").replace("\\", "/").strip("/")

    if is_file_share:
        return rel_path in ("", share_path)

    if not rel_path:
        return True
    if rel_path == share_path:
        return True
    return rel_path.startswith(share_path + "/")