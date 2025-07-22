# tests/probar_memoria.py
#para ejecutarlo desde la consola  escribir: python tests/probar_memoria.py

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from memory.memory import get_memory
from google.cloud import firestore
from pprint import pprint

USER_ID = "test_memoria_chat_123"
COLLECTION_NAME = "langchain_memory"

def main():
    memory = get_memory(USER_ID)
    memory.chat_memory.clear()

    memory.chat_memory.add_user_message("Hola, ¿hay disponibilidad mañana?")
    memory.chat_memory.add_ai_message("Sí, con gusto. Tenemos a las 9:00 y 11:00.")

    print("\nMemoria cargada:")
    for msg in memory.chat_memory.messages:
        print(f"[{msg.__class__.__name__}] {msg.content}")

    db = firestore.Client()
    doc = db.collection(COLLECTION_NAME).document(USER_ID).get()
    if doc.exists:
        print("\nDocumento en Firestore:")
        pprint(doc.to_dict())
    else:
        print("\nDocumento no encontrado en Firestore.")

if __name__ == "__main__":
    main()
