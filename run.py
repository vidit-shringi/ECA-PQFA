from __future__ import annotations

import argparse

from backend.app.cli import cmd_serve


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the ECA-PQFA research tool")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--reload", action="store_true")
    args = parser.parse_args()
    raise SystemExit(cmd_serve(args))
