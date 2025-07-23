# app/twilio_webhook.py

from flask import Blueprint, request, Response
from twilio.twiml.messaging_response import MessagingResponse

#crear blueprint para Twilio
bp = Blueprint('twilio_webhook', __name__)

@bp.route('/twilio_webhook', methods=['POST'])
def twilio_webhook():
    """Punto de entrada para Twilio WhatsApp o SMS"""
    mensaje = request.form.get("Body")
    numero = request.form.get("From")

    print(f"[Twilio] Mensaje recibido de {numero}: {mensaje}")

    #agregar funciones de core/functions.py o LangChain
    respuesta_texto = "Recibido"

    #respuesta Twilio
    respuesta = MessagingResponse()
    respuesta.message(respuesta_texto)

    return Response(str(respuesta), mimetype="application/xml")
