# Phone Public Intel CLI

CLI para extraer metadatos públicos de números telefónicos desde múltiples APIs.

## Proveedores integrados
- Numverify (`NUMVERIFY_API_KEY`)
- Abstract Phone Intelligence (`ABSTRACT_API_KEY`)
- APILayer Number Verification (`APILAYER_NUMBER_VERIFICATION_API_KEY`)

## Configuración recomendada (sin hardcodear claves)
1. Copia `.env.example` a `.env`.
2. Pega tus claves dentro de `.env`.

```bash
cp .env.example .env
```

Formato de `.env`:
```env
NUMVERIFY_API_KEY=tu_key
ABSTRACT_API_KEY=tu_key
APILAYER_NUMBER_VERIFICATION_API_KEY=tu_key
```

## Uso
```bash
python3 phone_intel_cli.py +573001234567 --pretty
python3 phone_intel_cli.py +573001234567 --provider numverify --country-code CO --pretty
python3 phone_intel_cli.py +573001234567 --provider apilayer --pretty
python3 phone_intel_cli.py --pretty
```

Si usas otro archivo de entorno:
```bash
python3 phone_intel_cli.py +573001234567 --env-file .env.local --pretty
```

## Nota
Esta herramienta consulta fuentes públicas/API y no debe usarse para acoso, doxxing ni vigilancia sin autorización.
