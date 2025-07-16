from flask import Blueprint, request
from telegram import Update, Bot
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, CallbackQueryHandler, Filters
from .keyboards import (
    main_menu_inline,
    telefono_reply,
    categorias_servicio_keyboard,
    servicios_por_categoria_keyboard,
)
from core.customers import crear_cliente_si_no_existe
from core.functions import cargar_servicios  # Debes tener esta función en core/
import os

bp = Blueprint('webhook', __name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = Bot(token=TELEGRAM_TOKEN)
dispatcher = Dispatcher(bot, None, use_context=True)

# ───────────────────────────────
# Cargar servicios una sola vez
# ───────────────────────────────
SERVICIOS = cargar_servicios()

# ───────────────────────────────
# Handlers
# ───────────────────────────────

def start(update, context):
    """Manejador del comando /start"""
    user = update.effective_user
    chat_id = update.effective_chat.id

    # Registrar al cliente
    crear_cliente_si_no_existe(user.id, user.first_name)

    context.bot.send_message(
        chat_id=chat_id,
        text=f"¡Hola {user.first_name}! Soy Oliva 🤖. ¿Qué deseas hacer?",
        reply_markup=main_menu_inline()
    )

def handle_text(update, context):
    """Manejador de mensajes de texto"""
    text = update.message.text
    chat_id = update.effective_chat.id

    if "servicio" in text.lower():
        context.bot.send_message(
            chat_id=chat_id,
            text="Aquí están nuestras categorías:",
            reply_markup=categorias_servicio_keyboard(SERVICIOS)
        )
    else:
        context.bot.send_message(
            chat_id=chat_id,
            text="No entendí. Usa el menú ⬇️",
            reply_markup=main_menu_inline()
        )

def handle_callback(update, context):
    """Manejador de botones inline"""
    query = update.callback_query
    query.answer()

    data = query.data
    chat_id = query.message.chat_id

    if data == "ver_servicios":
        context.bot.send_message(
            chat_id=chat_id,
            text="Elige una categoría de servicios:",
            reply_markup=categorias_servicio_keyboard(SERVICIOS)
        )

    elif data.startswith("cat_"):
        categoria = data[4:]
        context.bot.send_message(
            chat_id=chat_id,
            text=f"Servicios disponibles en *{categoria}*:",
            reply_markup=servicios_por_categoria_keyboard(SERVICIOS, categoria),
            parse_mode="Markdown"
        )

    elif data.startswith("serv_"):
        nombre_servicio = data[5:]
        servicio = next((s for s in SERVICIOS if s['Nombre'] == nombre_servicio), None)

        if servicio:
            detalle = (
                f"*{servicio['Nombre']}*\n"
                f"📂 Categoría: {servicio['Categoria']}\n"
                f"⏱️ Duración: {servicio['Duracion']}\n"
                f"💵 Precio: {servicio['Precio']}\n"
                f"📌 Depósito: {servicio['Deposito']}\n"
                f"📝 Detalles: {servicio['Detalles']}"
            )
            context.bot.send_message(chat_id=chat_id, text=detalle, parse_mode="Markdown")
        else:
            context.bot.send_message(chat_id=chat_id, text="Servicio no encontrado.")

    elif data == "agendar_cita":
        context.bot.send_message(chat_id=chat_id, text="¿Cuál servicio deseas agendar?")
        # Aquí más adelante se integrará flujo para agendar

    else:
        context.bot.send_message(chat_id=chat_id, text=f"Elegiste: {data}")

# ───────────────────────────────
# Registro de handlers
# ───────────────────────────────

dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_text))
dispatcher.add_handler(CallbackQueryHandler(handle_callback))

# ───────────────────────────────
# Endpoint Flask
# ───────────────────────────────

@bp.route('/webhook', methods=['POST'])
def telegram_webhook():
    """Punto de entrada de Telegram"""
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "ok"
