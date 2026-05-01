# Phone Public Intel CLI

CLI para extraer metadatos públicos de números telefónicos desde múltiples APIs.

## Proveedores integrados
- APILayer Number Verification (`APILAYER_NUMBER_VERIFICATION_API_KEY`)
- Abstract Phone Intelligence (`ABSTRACT_API_KEY`)
- Numverify (`NUMVERIFY_API_KEY`)

## Configuración
Copia `.env.example` a `.env` y agrega tus keys.

## Uso
```bash
python3 phone_intel_cli.py +34610898074
```

### Salida por proveedor (ordenada)
Por defecto la salida es legible y separada por bloques:
1. APILAYER
2. ABSTRACT
3. NUMVERIFY

### JSON opcional
```bash
python3 phone_intel_cli.py +34610898074 --json --pretty
```
