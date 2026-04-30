# Phone Public Intel CLI

Herramienta en Python para consultar **metadatos públicos y de validación** de números telefónicos mediante APIs externas.

## Alcance y límites
- ✅ Validación de número, país, operador y tipo de línea (según proveedor).
- ✅ Integra `Numverify` y `Abstract Phone Intelligence`.
- ❌ No realiza intrusión, scraping ilegal, doxxing ni obtención de datos privados.

## Requisitos
- Python 3.10+
- API keys:
  - `NUMVERIFY_API_KEY` (opcional)
  - `ABSTRACT_API_KEY` (opcional)

## Uso
```bash
export NUMVERIFY_API_KEY='tu_key'
export ABSTRACT_API_KEY='tu_key'
python3 phone_intel_cli.py +34600111222 --pretty
```

### Seleccionar proveedor
```bash
python3 phone_intel_cli.py +34600111222 --provider numverify --pretty
python3 phone_intel_cli.py +34600111222 --provider abstract --pretty
```

## Ejemplo de salida
```json
{
  "query_number": "+34600111222",
  "sources": [
    {
      "provider": "numverify",
      "ok": true,
      "status": 200,
      "error": null,
      "data": {"valid": true}
    }
  ]
}
```

## Buenas prácticas legales
Usa la herramienta únicamente cuando tengas base legal/consentimiento y para finalidades legítimas (prevención de fraude, validación de contacto, seguridad).
