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
from pathlib import Path
from typing import Any, Dict, Optional

ENV_KEYS = (
    "NUMVERIFY_API_KEY",
    "ABSTRACT_API_KEY",
    "APILAYER_NUMBER_VERIFICATION_API_KEY",
    "VERIPHONE_API_KEY",
)

PROVIDER_ORDER = ["apilayer", "veriphone", "abstract", "numverify"]


@dataclass
class ProviderResult:
    provider: str
    ok: bool
    status: int
    payload: Dict[str, Any]
    error: Optional[str] = None


def load_local_env(filepath: str = ".env") -> None:
    path = Path(filepath)
    if not path.exists():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and value and key in ENV_KEYS and not os.getenv(key):
            os.environ[key] = value


def resolve_env_file(cli_env_file: str) -> str:
    path = Path(cli_env_file)
    if path.exists():
        return str(path)
    fallback = Path(".env.example")
    if cli_env_file == ".env" and fallback.exists():
        return str(fallback)
    return str(path)


def mask_secret(value: str) -> str:
    if len(value) <= 6:
        return '*' * len(value)
    return value[:3] + '*' * (len(value) - 6) + value[-3:]


def config_diagnostics(env_file: str) -> str:
    lines = [f"Archivo de configuración cargado: {env_file}"]
    for key in ENV_KEYS:
        raw = os.getenv(key, "")
        state = mask_secret(raw) if raw else "NO CONFIGURADA"
        lines.append(f"- {key}: {state}")
    return "\n".join(lines)


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
    return provider_result("abstract_phone_intelligence", number, f"https://phonevalidation.abstractapi.com/v1/?{query}")




def query_veriphone(number: str, api_key: str) -> ProviderResult:
    query = urllib.parse.urlencode({"phone": number, "key": api_key})
    return provider_result("veriphone", number, f"https://api.veriphone.io/v2/verify?{query}")

def query_apilayer_number_verification(number: str, api_key: str) -> ProviderResult:
    query = urllib.parse.urlencode({"apikey": api_key, "number": number})
    return provider_result("apilayer_number_verification", number, f"https://api.apilayer.com/number_verification/validate?{query}")






def missing_key_result(provider: str, number: str, env_var: str) -> ProviderResult:
    return ProviderResult(
        provider=provider,
        ok=False,
        status=0,
        payload={"number": number, "missing_env": env_var},
        error=f"Falta configurar {env_var}",
    )


def derive_geo_hint(payload: Dict[str, Any]) -> Dict[str, str]:
    country = str(payload.get("country_name", "") or "").strip()
    country_code = str(payload.get("country_code", "") or "").strip()
    region = str(payload.get("location", "") or "").strip()
    if not country and not region:
        return {}

    query = ", ".join([part for part in [region, country] if part])
    maps_url = f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote_plus(query)}" if query else ""
    return {
        "country": country,
        "country_code": country_code,
        "region_hint": region,
        "maps_search_url": maps_url,
    }


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
                "geo_hint": derive_geo_hint(r.payload),
            }
            for r in results
        ],
        "compliance": {"notice": "Uso exclusivo con base legal y para finalidades legítimas."},
    }


def format_provider_block(result: ProviderResult) -> str:
    lines = []
    title = result.provider.upper()
    lines.append(f"\n{'=' * 20} {title} {'=' * 20}")
    lines.append(f"Estado: {'OK' if result.ok else 'ERROR'}")
    lines.append(f"HTTP: {result.status}")
    if result.error:
        lines.append(f"Error: {result.error}")

    geo_hint = derive_geo_hint(result.payload)
    if geo_hint:
        lines.append("Geolocalización aproximada (no GPS):")
        for k, v in geo_hint.items():
            lines.append(f"  {k:<22}: {v}")

    for key in sorted(result.payload.keys()):
        value = result.payload[key]
        if isinstance(value, (dict, list)):
            value = json.dumps(value, ensure_ascii=False)
        lines.append(f"{key:<24}: {value}")
    return "\n".join(lines)


def format_human_report(results: list[ProviderResult], number: str) -> str:
    header = [f"Número consultado: {number}", "Resultados por proveedor:"]
    body = [format_provider_block(r) for r in results]
    footer = ["\nNota legal: uso exclusivo con base legal y finalidades legítimas."]
    return "\n".join(header + body + footer)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Phone OSINT público (legal)")
    p.add_argument("number", nargs="?", help="Número internacional. Si se omite, se pedirá por consola.")
    p.add_argument("--provider", choices=["all", "numverify", "abstract", "apilayer", "veriphone"], default="all")
    p.add_argument("--country-code", help="Código ISO-2 para Numverify (opcional)")
    p.add_argument("--pretty", action="store_true", help="(Solo JSON) Imprime JSON con indentación")
    p.add_argument("--json", action="store_true", help="Salida en JSON en vez de reporte tabulado")
    p.add_argument("--env-file", default=".env", help="Ruta a .env (default: .env)")
    p.add_argument("--doctor", action="store_true", help="Muestra diagnóstico de carga de keys y sale")
    return p


def main() -> int:
    args = build_parser().parse_args()
    resolved_env = resolve_env_file(args.env_file)
    load_local_env(resolved_env)

    if args.doctor:
        print(config_diagnostics(resolved_env))
        return 0
    number = args.number.strip() if args.number else input("Ingresa el número telefónico: ").strip()
    if not number:
        print("Error: number vacío", file=sys.stderr)
        return 2

    results: list[ProviderResult] = []

    providers = [args.provider] if args.provider != "all" else PROVIDER_ORDER
    for provider in providers:
        if provider == "numverify":
            key = os.getenv("NUMVERIFY_API_KEY")
            if key:
                results.append(query_numverify(number, key, args.country_code))
            else:
                results.append(missing_key_result("numverify", number, "NUMVERIFY_API_KEY"))
        elif provider == "abstract":
            key = os.getenv("ABSTRACT_API_KEY")
            if key:
                results.append(query_abstract_phone(number, key))
            else:
                results.append(missing_key_result("abstract_phone_intelligence", number, "ABSTRACT_API_KEY"))
        elif provider == "apilayer":
            key = os.getenv("APILAYER_NUMBER_VERIFICATION_API_KEY")
            if key:
                results.append(query_apilayer_number_verification(number, key))
            else:
                results.append(missing_key_result("apilayer_number_verification", number, "APILAYER_NUMBER_VERIFICATION_API_KEY"))
        elif provider == "veriphone":
            key = os.getenv("VERIPHONE_API_KEY")
            if key:
                results.append(query_veriphone(number, key))
            else:
                results.append(missing_key_result("veriphone", number, "VERIPHONE_API_KEY"))

    if not results:
        print("No hay proveedores configurados. Revisa .env/.env.example, guarda el archivo (Ctrl+S en VS Code) y verifica con --doctor.", file=sys.stderr)
        print(config_diagnostics(resolved_env), file=sys.stderr)
        return 2

    if args.json:
        output = normalize_output(results, number)
        print(json.dumps(output, ensure_ascii=False, indent=2 if args.pretty else None))
    else:
        print(format_human_report(results, number))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
