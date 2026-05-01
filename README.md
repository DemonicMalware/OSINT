# Phone Public Intel CLI

CLI para extraer metadatos públicos de números telefónicos desde múltiples APIs.

## Proveedores integrados
- Numverify (`NUMVERIFY_API_KEY`)
- Abstract Phone Intelligence (`ABSTRACT_API_KEY`)
- APILayer Number Verification (`APILAYER_NUMBER_VERIFICATION_API_KEY`)

## Configuración
```bash
export NUMVERIFY_API_KEY='...'
export ABSTRACT_API_KEY='...'
export APILAYER_NUMBER_VERIFICATION_API_KEY='...'
```

## Uso
```bash
python3 phone_intel_cli.py +573001234567 --pretty
python3 phone_intel_cli.py +573001234567 --provider numverify --country-code CO --pretty
python3 phone_intel_cli.py +573001234567 --provider apilayer --pretty
```

También puedes ejecutarlo sin argumento y te pedirá el número por consola:
```bash
python3 phone_intel_cli.py --pretty
```

## Nota
Esta herramienta consulta fuentes públicas/API y no debe usarse para acoso, doxxing ni vigilancia sin autorización.
