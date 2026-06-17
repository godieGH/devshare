#!/usr/bin/env python3
from __future__ import annotations

import argparse

from .server import run_server


def main():
    parser = argparse.ArgumentParser(
        prog="devserve",
        description="Cross-platform local file server with browser UI",
    )
    parser.add_argument("--host", default="0.0.0.0", help="Bind address")
    parser.add_argument("--port", type=int, default=8080, help="Port number")
    parser.add_argument("--dir", default=".", help="Folder to serve")
    parser.add_argument("--theme", choices=["dark", "light"], default="dark", help="UI theme")
    parser.add_argument("--title", default="DevShare Pro", help="Browser title")

    args = parser.parse_args()
    run_server(
        host=args.host,
        port=args.port,
        root_dir=args.dir,
        theme=args.theme,
        title=args.title,
    )


if __name__ == "__main__":
    main()