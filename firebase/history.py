from firebase.client import db
from datetime import datetime
from google.cloud.firestore_v1 import ArrayUnion

COLLECTION = "chat_history"

def save_message(user_id: str, role: str, content: str, **extra_fields):
    """
    Guarda un mensaje en la colección 'chat_history' en Firestore.
    El rol puede ser 'user', 'assistant', 'bot', etc.
    Extra fields se pueden usar para intención, corte recomendado, etc.
    """
    doc_ref = db.collection(COLLECTION).document(user_id)

    #entrada base del mensaje
    new_entry = {
        "role": role,
        "content": content,
        "timestamp": datetime.utcnow()
    }

    # Agrega cualquier otro campo adicional proporcionado
    new_entry.update(extra_fields)

    # Actualiza documento o lo crea
    doc = doc_ref.get()
    if doc.exists:
        doc_ref.update({
            "messages": ArrayUnion([new_entry]),
            "last_updated": datetime.utcnow()
        })
    else:
        doc_ref.set({
            "messages": [new_entry],
            "last_updated": datetime.utcnow()
        })

def get_history(user_id: str) -> list:
    """
    Recupera el historial completo de un usuario desde Firestore.
    """
    doc = db.collection(COLLECTION).document(user_id).get()
    if doc.exists:
        return doc.to_dict().get("messages", [])
    return []
