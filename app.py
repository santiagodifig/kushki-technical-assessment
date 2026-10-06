import os

import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 4096

CHARGE_URL = "https://api-uat.kushkipagos.com/card/v1/charges"


@app.route("/")
def inicio():
    return render_template(
        "index.html",
        public_merchant_id=os.environ.get("KUSHKI_PUBLIC_KEY", "afc9e1699f3b472a954d663bce6e528c")
    )


@app.route("/health")
def health():
    return jsonify(status="ok"), 200


@app.route("/checkout", methods=["POST"])
def checkout():
    datos = request.get_json(silent=True)

    if not isinstance(datos, dict):
        return jsonify(message="Se esperaba un objeto JSON."), 400

    token = datos.get("token")

    if not isinstance(token, str) or not token.strip() or len(token) > 512:
        return jsonify(message="Falta un token válido."), 400

    private_key = os.environ.get("KUSHKI_PRIVATE_KEY")

    if not private_key:
        return jsonify(
            message="Falta configurar la credencial privada UAT."
        ), 503

    # El servidor define el monto; no lo toma del navegador.
    payload = {
        "token": token.strip(),
        "amount": {
            "currency": "MXN",
            "subtotalIva": 0,
            "subtotalIva0": 1000,
            "iva": 0,
            "ice": 0
        },
        "metadata": {
            "proyecto": "TiagoLunch Bonus UAT"
        }
    }

    try:
        respuesta = requests.post(
            CHARGE_URL,
            headers={
                "Private-Merchant-Id": private_key,
                "Content-Type": "application/json"
            },
            json=payload,
            timeout=(10, 35)
        )
    except requests.RequestException:
        return jsonify(
            status="unknown",
            message=(
                "No se pudo confirmar el resultado del cargo. "
                "Consulta la transacción en Kushki antes de reintentar."
            )
        ), 200

    try:
        resultado = respuesta.json()
    except ValueError:
        resultado = {}

    if not isinstance(resultado, dict):
        resultado = {}

    ticket = resultado.get("ticketNumber")

    if respuesta.status_code == 201 and ticket and not resultado.get("code"):
        return jsonify(
            status="approved",
            ticketNumber=ticket,
            transactionReference=resultado.get("transactionReference"),
            message=f"Pago de prueba aprobado. Ticket: {ticket}"
        ), 200

    if respuesta.status_code == 400:
        codigo = resultado.get("code", "")
        detalle = resultado.get("message") or "Solicitud rechazada."

        return jsonify(
            status="rejected",
            message=f"Kushki rechazó la solicitud: {codigo} — {detalle}"
        ), 200

    if respuesta.status_code in (401, 403):
        return jsonify(
            status="error",
            message="Kushki no autorizó la solicitud. Revisa la credencial UAT."
        ), 200

    return jsonify(
        status="unknown",
        message=(
            f"Resultado sin confirmar (HTTP {respuesta.status_code}). "
            "Revisa la transacción en Kushki antes de reintentar."
        )
    ), 200


if __name__ == "__main__":
    app.run(debug=False)