from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton

# ───────────────────────────────
# INLINE KEYBOARDS
# ───────────────────────────────

def main_menu_inline():
    """Teclado con opciones principales"""
    keyboard = [
        [InlineKeyboardButton("Ver servicios", callback_data="ver_servicios")],
        [InlineKeyboardButton("Agendar cita", callback_data="agendar_cita")],
        [InlineKeyboardButton("Mis citas", callback_data="ver_citas")],
    ]
    return InlineKeyboardMarkup(keyboard)

def confirmacion_cita_inline(cita_id: int):
    """Teclado de confirmación para una cita"""
    keyboard = [
        [
            InlineKeyboardButton("Confirmar", callback_data=f"confirmar_{cita_id}"),
            InlineKeyboardButton("Cancelar", callback_data=f"cancelar_{cita_id}"),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def categorias_servicio_keyboard(servicios):
    """Botones únicos por categoría de servicio"""
    categorias = sorted(set(s['Categoria'] for s in servicios if s['Categoria']))
    keyboard = [[InlineKeyboardButton(cat, callback_data=f"cat_{cat}")] for cat in categorias]
    return InlineKeyboardMarkup(keyboard)

def servicios_por_categoria_keyboard(servicios, categoria):
    """Botones por nombre de servicio en una categoría"""
    filtrados = [s for s in servicios if s['Categoria'] == categoria]
    keyboard = [
        [InlineKeyboardButton(s['Nombre'], callback_data=f"serv_{s['Nombre']}")]
        for s in filtrados
    ]
    return InlineKeyboardMarkup(keyboard)

# ───────────────────────────────
# REPLY KEYBOARDS
# ───────────────────────────────

def telefono_reply():
    """Teclado para solicitar número de teléfono"""
    keyboard = [[KeyboardButton("📱 Enviar número", request_contact=True)]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

def menu_principal_reply():
    """Menú clásico con botones grandes"""
    keyboard = [
        ["💇 Servicios", "Nueva cita"],
        ["📋 Mis citas", "Cancelar cita"],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
