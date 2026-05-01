# Phone Public Intel CLI

CLI para extraer metadatos públicos de números telefónicos desde múltiples APIs.

## Proveedores integrados
- APILayer Number Verification (`APILAYER_NUMBER_VERIFICATION_API_KEY`)
- Abstract Phone Intelligence (`ABSTRACT_API_KEY`)
- Numverify (`NUMVERIFY_API_KEY`)
- Veriphone (`VERIPHONE_API_KEY`)

## Configuración
Copia `.env.example` a `.env` y agrega tus keys.

## Uso
```bash
python3 phone_intel_cli.py +34610898074
```

### Salida por proveedor (ordenada)
Por defecto la salida es legible y separada por bloques:
1. APILAYER
2. VERIPHONE
3. ABSTRACT
4. NUMVERIFY

### JSON opcional
```bash
python3 phone_intel_cli.py +34610898074 --json --pretty
```


## Diagnóstico rápido
Si aparece "No hay proveedores configurados", ejecuta:
```bash
python3 phone_intel_cli.py --doctor
```
Te mostrará qué archivo cargó (`.env` o `.env.example`) y si cada key fue detectada.


### Si en VS Code sigue diciendo "NO CONFIGURADA"
1. Guarda el archivo con **Ctrl+S** (en tu captura aparece `1 unsaved`).
2. Verifica que estés editando el archivo dentro de la misma carpeta desde donde ejecutas Python.
3. Ejecuta: `python3 phone_intel_cli.py --doctor`


## Geolocalización
Sí: el CLI ahora muestra **geolocalización aproximada** por proveedor (`country`, `country_code`, `region_hint`) y un enlace de búsqueda en mapa.

> Importante: no es geolocalización GPS ni tiempo real; depende de metadatos públicos del operador/API.


## Veriphone
Para habilitarlo, agrega en tu archivo de entorno:
```env
VERIPHONE_API_KEY=tu_key
```
También puedes consultar solo ese proveedor:
```bash
python3 phone_intel_cli.py +34610898074 --provider veriphone
```


### Visibilidad de proveedores sin key
Si falta la key de un proveedor, ahora también aparecerá en el reporte con `Estado: ERROR` y el campo `missing_env`, para que veas claramente qué configuración falta (por ejemplo, `VERIPHONE_API_KEY`).
