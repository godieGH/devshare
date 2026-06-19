from __future__ import annotations

import os
from http.server import ThreadingHTTPServer

from . import __version__
from .auth import AuthManager
from .handlers import DevServeHandler
from .utils import get_lan_addresses


class DevHTTPServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True


def run_server(
    host: str,
    port: int,
    root_dir: str,
    theme: str,
    title: str,
    pin: str | None,
    share_expire_hours: float = 24.0,
):
    DevServeHandler.root_dir = os.path.realpath(root_dir)
    DevServeHandler.theme = theme
    DevServeHandler.title = title
    DevServeHandler.version = __version__
    DevServeHandler.port = port
    DevServeHandler.auth_manager = AuthManager(pin, share_expire_hours)

    httpd = DevHTTPServer((host, port), DevServeHandler)

    print(f"DevShare running on http://127.0.0.1:{port}")
    for url in get_lan_addresses(port):
        print(f"  LAN: {url}")
    print(f"Serving: {DevServeHandler.root_dir}")

    if pin:
        print(f"Host PIN: {pin}")
        print("Other devices need this PIN for full access, or use a share link.")
    else:
        print("Warning: PIN protection disabled (--no-auth). Anyone on the network has full access.")

    print("Press Ctrl+C to stop")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        httpd.server_close()
