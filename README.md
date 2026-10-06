# Kushki — Technical Support Engineer Assessment

Santiago Alejandro Díaz Figueroa. Pruebas en UAT, México.

## Ejercicio II: Postman

Importa `Kushki_Ejercicio_2.postman_collection.json` en Postman. Incluye solicitudes y respuestas guardadas de tokenización, cargo, anulación y consulta de transacciones.

Configura `publicMerchantId` y `privateMerchantId` con el par de credenciales de tu comercio UAT. La variable privada se entrega vacía; conserva su valor únicamente de forma local.

Para repetir el flujo, genera un token nuevo, copia ese token al body del cargo y usa el nuevo ticket en la URL de anulación. Ajusta las fechas de consulta al período de tus pruebas. Los ejemplos son evidencia histórica y no se ejecutan automáticamente. Los códigos de los primeros tres ejemplos se corrigieron a 201 conforme a las capturas originales: Postman había guardado 200.

## Bonus: aplicación web

Frontend HTML/JavaScript con Kushki.js y backend Python/Flask. El navegador envía la tarjeta a Kushki para tokenizarla; el backend recibe únicamente el token y solicita el cargo usando la credencial privada de una variable de entorno. El monto está fijado en el servidor: 1,000 MXN.

Se probaron localmente pago aprobado y pago declinado. La URL pública se añadirá después de desplegar y verificar la aplicación.

### Ejecución local

1. Crea un entorno virtual: `python -m venv .venv`.
2. Actívalo e instala dependencias: `python -m pip install -r requirements.txt`.
3. Configura `KUSHKI_PRIVATE_KEY` con tu credencial privada UAT y `KUSHKI_PUBLIC_KEY` con la pública del mismo comercio. Si no configuras la pública, se usa la del assessment.
4. Ejecuta `python app.py` y abre `http://127.0.0.1:5000`.

En Windows PowerShell puedes configurar la privada sin mostrarla:

```powershell
$kushkiSecret = Read-Host "Credencial privada UAT" -AsSecureString
$env:KUSHKI_PRIVATE_KEY = [System.Net.NetworkCredential]::new("", $kushkiSecret).Password
Remove-Variable kushkiSecret
$env:KUSHKI_PUBLIC_KEY = "TU_CREDENCIAL_PUBLICA_UAT"
python app.py
```

### Publicación en Render

Crea un Web Service desde este repositorio, con Python 3, build command `pip install -r requirements.txt` y start command `gunicorn app:app --bind 0.0.0.0:$PORT --timeout 90`. Configura las dos credenciales UAT en Environment. Health check: `/health`. Gunicorn se instala en Linux; la ejecución local de Windows usa Flask.

### Pruebas UAT

- Aprobación: `5451951574925480`.
- Cargo declinado: `4349003000047015`.
- Nombre: Santiago Diaz; vencimiento 12/28; CVV 123. Actualiza el vencimiento cuando deje de ser futuro.

Usa únicamente tarjetas de prueba. Token generado no significa pago aprobado. La aplicación distingue aprobación, solicitud rechazada, error de autorización y resultado incierto. Ante timeout o respuesta inesperada, bloquea el botón en la página actual y pide verificar la transacción antes de reintentar. Recargar la página no resuelve un resultado incierto.

Es una demostración UAT. No incluye persistencia de órdenes, conciliación automática, webhooks, idempotencia de cargos ni flujo adicional OTP/3DS. Si el SDK solicita validación adicional, se detiene antes del cargo. No está preparada para producción.

### Apoyo de IA

Se utilizó IA como apoyo para generar y revisar código y documentación. El candidato realizó la configuración de UAT, las pruebas, la validación de respuestas y el seguimiento con soporte.
