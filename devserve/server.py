from __future__ import annotations

import os
from http.server import ThreadingHTTPServer

from . import __version__
from .handlers import DevServeHandler


class DevHTTPServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True


def run_server(host: str, port: int, root_dir: str, theme: str, title: str):
    DevServeHandler.root_dir = os.path.realpath(root_dir)
    DevServeHandler.theme = theme
    DevServeHandler.title = title
    DevServeHandler.version = __version__

    httpd = DevHTTPServer((host, port), DevServeHandler)
    print(f"DevServe running on http://{host}:{port}")
    print(f"Serving: {DevServeHandler.root_dir}")
    print("Press Ctrl+C to stop")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        httpd.server_close()