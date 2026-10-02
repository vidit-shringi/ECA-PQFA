from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _hash_file(path: str) -> dict[str, str | int]:
    p = Path(path).expanduser().resolve()
    if not p.is_file():
        raise FileNotFoundError(str(p))
    data = p.read_bytes()
    return {
        "path": str(p),
        "file_name": p.name,
        "file_size": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "sha3_256": hashlib.sha3_256(data).hexdigest(),
    }


def cmd_serve(args: argparse.Namespace) -> int:
    import uvicorn

    uvicorn.run(
        "backend.app.main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
    )
    return 0


def cmd_demo(_: argparse.Namespace) -> int:
    from scripts.demo_pipeline import main as demo_main

    demo_main()
    return 0


def cmd_test(args: argparse.Namespace) -> int:
    cmd = [sys.executable, "-m", "pytest", "-q"]
    if args.keyword:
        cmd.extend(["-k", args.keyword])
    return subprocess.call(cmd, cwd=ROOT)


def cmd_hash(args: argparse.Namespace) -> int:
    print(json.dumps(_hash_file(args.path), indent=2))
    return 0


def cmd_inventory(args: argparse.Namespace) -> int:
    from backend.app.services.inventory import scan_directory

    print(json.dumps(scan_directory(args.path, args.recursive), indent=2))
    return 0


def cmd_cbom(args: argparse.Namespace) -> int:
    from backend.app.services.cbom import build_cbom

    result = build_cbom(args.path, args.recursive)
    rendered = json.dumps(result, indent=2)
    if args.output:
        Path(args.output).expanduser().resolve().write_text(rendered + "\n", encoding="utf-8")
        print(args.output)
    else:
        print(rendered)
    return 0


def cmd_audit(_: argparse.Namespace) -> int:
    from backend.app.services.provenance import audit_chain

    print(json.dumps(audit_chain(), indent=2))
    return 0


def cmd_tree_head(_: argparse.Namespace) -> int:
    from backend.app.services.provenance import create_tree_head

    print(json.dumps(create_tree_head(), indent=2))
    return 0


def cmd_health(args: argparse.Namespace) -> int:
    print(
        json.dumps(
            {
                "tool": "ECA-PQFA",
                "version": "3.1.0",
                "root": str(ROOT),
                "python": sys.version.split()[0],
                "endpoint": f"http://{args.host}:{args.port}",
            },
            indent=2,
        )
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="eca-pqfa",
        description=(
            "ECA-PQFA: evidence-carrying AI-assisted cryptanalysis and "
            "post-quantum forensic assurance research tool."
        ),
    )
    parser.add_argument("--version", action="version", version="ECA-PQFA 3.1.0")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("serve", help="Run the FastAPI research tool")
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=8000)
    p.add_argument("--reload", action="store_true")
    p.set_defaults(func=cmd_serve)

    p = sub.add_parser("demo", help="Run the complete synthetic end-to-end workflow")
    p.set_defaults(func=cmd_demo)

    p = sub.add_parser("test", help="Run the automated test suite")
    p.add_argument("-k", "--keyword", help="Optional pytest -k expression")
    p.set_defaults(func=cmd_test)

    p = sub.add_parser("hash", help="Hash an evidence file with SHA-256 and SHA3-256")
    p.add_argument("path")
    p.set_defaults(func=cmd_hash)

    p = sub.add_parser("inventory", help="Scan a controlled directory for crypto artifacts")
    p.add_argument("path")
    p.add_argument("--no-recursive", dest="recursive", action="store_false")
    p.set_defaults(recursive=True, func=cmd_inventory)

    p = sub.add_parser("cbom", help="Generate a CycloneDX-style cryptographic inventory")
    p.add_argument("path")
    p.add_argument("--output")
    p.add_argument("--no-recursive", dest="recursive", action="store_false")
    p.set_defaults(recursive=True, func=cmd_cbom)

    p = sub.add_parser("audit", help="Audit the provenance chain and current tree head")
    p.set_defaults(func=cmd_audit)

    p = sub.add_parser("tree-head", help="Seal the current provenance log")
    p.set_defaults(func=cmd_tree_head)

    p = sub.add_parser("health", help="Show local tool/runtime information")
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=8000)
    p.set_defaults(func=cmd_health)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        return int(args.func(args))
    except KeyboardInterrupt:
        return 130
    except Exception as exc:
        print(f"ECA-PQFA error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
