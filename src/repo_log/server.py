from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse

from repo_log.actions import (
    ActionResult,
    add_project,
    capture_file,
    catalog_notes,
    drop_project,
    init_notes,
    load_state,
)

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8765


def state_payload(settings_path: Path | None = None) -> dict[str, Any]:
    st = load_state(settings_path)
    return {
        "ok": True,
        "graph": str(st["graph"]),
        "ready": st["ready"],
        "projects": st["projects"],
    }


def result_payload(result: ActionResult, settings_path: Path | None = None) -> dict[str, Any]:
    payload = state_payload(settings_path)
    payload["ok"] = result.ok
    payload["message"] = result.message
    return payload


def dispatch(method: str, path: str, body: dict, settings_path: Path | None) -> tuple[int, dict]:
    if method == "GET" and path == "/api/status":
        return 200, state_payload(settings_path)
    if method == "POST" and path == "/api/init":
        return 200, result_payload(init_notes(settings_path), settings_path)
    if method == "POST" and path == "/api/catalog":
        return 200, result_payload(catalog_notes(settings_path), settings_path)
    if method == "POST" and path == "/api/projects":
        root = body.get("root") or ""
        ide = str(body.get("ide") or "cursor")
        pid = body.get("id") or None
        return 200, result_payload(
            add_project(root, ide=ide, project_id=pid, settings_path=settings_path),
            settings_path,
        )
    if method == "DELETE" and path.startswith("/api/projects/"):
        pid = unquote(path[len("/api/projects/") :]).strip()
        return 200, result_payload(drop_project(pid, settings_path=settings_path), settings_path)
    if method == "POST" and path == "/api/capture":
        return 200, result_payload(
            capture_file(
                body.get("path") or "",
                kind=str(body.get("kind") or "cursor"),
                title=str(body.get("title") or ""),
                concept=str(body.get("concept") or ""),
                settings_path=settings_path,
            ),
            settings_path,
        )
    return 404, {"ok": False, "message": f"unknown {method} {path}"}


def make_handler(settings_path: Path | None) -> type[BaseHTTPRequestHandler]:
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt: str, *args: object) -> None:
            return

        def _cors(self) -> None:
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")

        def _read_json(self) -> dict:
            length = int(self.headers.get("Content-Length") or 0)
            if length <= 0:
                return {}
            raw = self.rfile.read(length)
            if not raw:
                return {}
            data = json.loads(raw.decode("utf-8"))
            return data if isinstance(data, dict) else {}

        def _send(self, code: int, payload: dict) -> None:
            blob = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(code)
            self._cors()
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(blob)))
            self.end_headers()
            self.wfile.write(blob)

        def do_OPTIONS(self) -> None:  # noqa: N802
            self.send_response(204)
            self._cors()
            self.end_headers()

        def do_GET(self) -> None:  # noqa: N802
            self._route("GET")

        def do_POST(self) -> None:  # noqa: N802
            self._route("POST")

        def do_DELETE(self) -> None:  # noqa: N802
            self._route("DELETE")

        def _route(self, method: str) -> None:
            parsed = urlparse(self.path)
            try:
                body = self._read_json() if method in {"POST", "PUT"} else {}
                code, payload = dispatch(method, parsed.path, body, settings_path)
            except ValueError as exc:
                code, payload = 400, {"ok": False, "message": str(exc)}
            except Exception as exc:  # isolation errors already ValueError
                code, payload = 500, {"ok": False, "message": str(exc)}
            self._send(code, payload)

    return Handler


def make_server(
    *,
    host: str = DEFAULT_HOST,
    port: int = DEFAULT_PORT,
    settings_path: Path | None = None,
) -> ThreadingHTTPServer:
    if host not in {"127.0.0.1", "localhost", "::1"}:
        raise ValueError("engine HTTP must bind localhost only")
    return ThreadingHTTPServer((host, port), make_handler(settings_path))


def serve(
    *,
    host: str = DEFAULT_HOST,
    port: int = DEFAULT_PORT,
    settings_path: Path | None = None,
) -> None:
    httpd = make_server(host=host, port=port, settings_path=settings_path)
    bound = httpd.server_address
    print(f"Repo Log 引擎 http://{bound[0]}:{bound[1]}  （Logseq 插件连这个地址）")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()
