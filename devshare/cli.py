#!/usr/bin/env python3
from __future__ import annotations

import argparse

from .auth import generate_pin
from .server import run_server


def main():
    parser = argparse.ArgumentParser(
        prog="devshare",
        description="Secure LAN file sharing with browser UI",
    )
    parser.add_argument("--host", default="0.0.0.0", help="Bind address")
    parser.add_argument("--port", type=int, default=8080, help="Port number")
    parser.add_argument("--dir", default=".", help="Folder to serve")
    parser.add_argument("--theme", choices=["dark", "light"], default="dark", help="UI theme")
    parser.add_argument("--title", default="DevShare Pro", help="Browser title")
    parser.add_argument(
        "--pin",
        default=None,
        help="6-digit access PIN for host login (default: auto-generated)",
    )
    parser.add_argument(
        "--no-auth",
        action="store_true",
        help="Disable PIN protection (open access, not recommended on LAN)",
    )
    parser.add_argument(
        "--share-expires",
        type=float,
        default=24.0,
        help="Share link lifetime in hours (0 = never expires)",
    )

    args = parser.parse_args()

    pin = None
    if not args.no_auth:
        pin = args.pin or generate_pin()

    run_server(
        host=args.host,
        port=args.port,
        root_dir=args.dir,
        theme=args.theme,
        title=args.title,
        pin=pin,
        share_expire_hours=args.share_expires,
    )


if __name__ == "__main__":
    main()
