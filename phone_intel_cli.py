#!/usr/bin/env python3
"""CLI para análisis de información pública de números telefónicos."""

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


def http_get_json(url: str, timeout: int = 20) -> tuple[int, Dict[str, Any]]:
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        body = resp.read().decode("utf-8", errors="replace")
        status = getattr(resp, "status", 200)
    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        data = {"raw": body}
    return status, data


def provider_result(provider: str, number: str, url: str) -> ProviderResult:
    try:
        status, data = http_get_json(url)
        return ProviderResult(provider, True, status, data)
    except urllib.error.HTTPError as exc:
        return ProviderResult(provider, False, exc.code, {"number": number}, str(exc))
    except Exception as exc:  # noqa: BLE001
        return ProviderResult(provider, False, 0, {"number": number}, str(exc))


def query_numverify(number: str, api_key: str, country_code: Optional[str] = None) -> ProviderResult:
    params = {"access_key": api_key, "number": number}
    if country_code:
        params["country_code"] = country_code
    query = urllib.parse.urlencode(params)
    return provider_result("numverify", number, f"https://apilayer.net/api/validate?{query}")


def query_abstract_phone(number: str, api_key: str) -> ProviderResult:
    query = urllib.parse.urlencode({"api_key": api_key, "phone": number})
    return provider_result(
        "abstract_phone_intelligence",
        number,
        f"https://phonevalidation.abstractapi.com/v1/?{query}",
    )


def query_apilayer_number_verification(number: str, api_key: str) -> ProviderResult:
    query = urllib.parse.urlencode({"apikey": api_key, "number": number})
    return provider_result(
        "apilayer_number_verification",
        number,
        f"https://api.apilayer.com/number_verification/validate?{query}",
    )


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
            "notice": "Uso exclusivo con base legal y para finalidades legítimas."
        },
    }


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Phone OSINT público (legal)")
    p.add_argument(
        "number",
        nargs="?",
        help="Número en formato internacional (ej. +34600111222). Si se omite, se pedirá por consola.",
    )
    p.add_argument(
        "--provider",
        choices=["all", "numverify", "abstract", "apilayer"],
        default="all",
        help="Proveedor a consultar",
    )
    p.add_argument("--country-code", help="Código de país ISO-2 para Numverify (opcional)")
    p.add_argument("--pretty", action="store_true", help="Imprime JSON con indentación")
    return p


def main() -> int:
    args = build_parser().parse_args()
    if args.number:
        number = args.number.strip()
    else:
        number = input("Ingresa el número telefónico (formato internacional, ej. +34600111222): ").strip()

    if not number:
        print("Error: number vacío", file=sys.stderr)
        return 2

    results: list[ProviderResult] = []

    if args.provider in {"all", "numverify"}:
        key = os.getenv("NUMVERIFY_API_KEY")
        if key:
            results.append(query_numverify(number, key, args.country_code))
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

    if args.provider in {"all", "apilayer"}:
        key = os.getenv("APILAYER_NUMBER_VERIFICATION_API_KEY")
        if key:
            results.append(query_apilayer_number_verification(number, key))
        elif args.provider == "apilayer":
            print("Falta APILAYER_NUMBER_VERIFICATION_API_KEY", file=sys.stderr)
            return 2

    if not results:
        print(
            "No hay proveedores configurados. Define NUMVERIFY_API_KEY, ABSTRACT_API_KEY y/o APILAYER_NUMBER_VERIFICATION_API_KEY.",
            file=sys.stderr,
        )
        return 2

    output = normalize_output(results, number)
    print(json.dumps(output, ensure_ascii=False, indent=2 if args.pretty else None))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
