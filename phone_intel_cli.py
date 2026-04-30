#!/usr/bin/env python3
"""CLI para análisis de información pública de números telefónicos.

Este programa NO realiza intrusión, doxxing ni acceso no autorizado.
Solo usa APIs externas configuradas por el usuario para obtener:
- Validación de formato
- País/región/operador (si el proveedor lo expone)
- Tipo de línea
- Indicadores de riesgo cuando estén disponibles
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class ProviderResult:
    provider: str
    ok: bool
    status: int
    payload: Dict[str, Any]
    error: Optional[str] = None


def http_get_json(url: str, timeout: int = 15) -> tuple[int, Dict[str, Any]]:
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        body = resp.read().decode("utf-8", errors="replace")
        status = getattr(resp, "status", 200)
    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        data = {"raw": body}
    return status, data


def query_numverify(number: str, api_key: str) -> ProviderResult:
    query = urllib.parse.urlencode({"access_key": api_key, "number": number})
    url = f"http://apilayer.net/api/validate?{query}"
    try:
        status, data = http_get_json(url)
        return ProviderResult("numverify", True, status, data)
    except urllib.error.HTTPError as exc:
        return ProviderResult("numverify", False, exc.code, {}, str(exc))
    except Exception as exc:  # noqa: BLE001
        return ProviderResult("numverify", False, 0, {}, str(exc))


def query_abstract_phone(number: str, api_key: str) -> ProviderResult:
    query = urllib.parse.urlencode({"api_key": api_key, "phone": number})
    url = f"https://phonevalidation.abstractapi.com/v1/?{query}"
    try:
        status, data = http_get_json(url)
        return ProviderResult("abstract_phone_intelligence", True, status, data)
    except urllib.error.HTTPError as exc:
        return ProviderResult("abstract_phone_intelligence", False, exc.code, {}, str(exc))
    except Exception as exc:  # noqa: BLE001
        return ProviderResult("abstract_phone_intelligence", False, 0, {}, str(exc))


def normalize_output(results: list[ProviderResult], number: str) -> Dict[str, Any]:
    return {
        "query_number": number,
        "sources": [
            {
                "provider": r.provider,
                "ok": r.ok,
                "status": r.status,
                "error": r.error,
                "data": r.payload,
            }
            for r in results
        ],
        "compliance": {
            "notice": (
                "Usa este resultado solo con fines legales y legítimos. "
                "No se debe emplear para acoso, doxxing o vigilancia no autorizada."
            )
        },
    }


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="OSINT legal de números telefónicos usando APIs configuradas por el usuario"
    )
    p.add_argument("number", help="Número en formato internacional (ej. +34600111222)")
    p.add_argument(
        "--provider",
        choices=["all", "numverify", "abstract"],
        default="all",
        help="Proveedor a consultar",
    )
    p.add_argument(
        "--pretty",
        action="store_true",
        help="Imprime JSON con indentación",
    )
    return p


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    number = args.number.strip()
    if not number:
        print("Error: number vacío", file=sys.stderr)
        return 2

    results: list[ProviderResult] = []

    if args.provider in {"all", "numverify"}:
        key = os.getenv("NUMVERIFY_API_KEY")
        if key:
            results.append(query_numverify(number, key))
        elif args.provider == "numverify":
            print("Falta NUMVERIFY_API_KEY", file=sys.stderr)
            return 2

    if args.provider in {"all", "abstract"}:
        key = os.getenv("ABSTRACT_API_KEY")
        if key:
            results.append(query_abstract_phone(number, key))
        elif args.provider == "abstract":
            print("Falta ABSTRACT_API_KEY", file=sys.stderr)
            return 2

    if not results:
        print(
            "No hay proveedores configurados. Define NUMVERIFY_API_KEY y/o ABSTRACT_API_KEY.",
            file=sys.stderr,
        )
        return 2

    output = normalize_output(results, number)
    if args.pretty:
        print(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(output, ensure_ascii=False))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
