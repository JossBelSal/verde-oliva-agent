# memory/memory.py

from langchain.memory import ConversationBufferMemory
from firebase.langchain_memory import FirestoreChatHistory

# Namespace exclusivo para la memoria del modelo (separado del historial enriquecido)
MEMORY_NAMESPACE = "langchain_memory"

def get_memory(user_id: str) -> ConversationBufferMemory:
    """
    Inicializa la memoria conversacional para el usuario especificado,
    utilizando Firestore como backend con el namespace 'langchain_memory'.
    """
    chat_history = FirestoreChatHistory(user_id=user_id, namespace=MEMORY_NAMESPACE)

    memory = ConversationBufferMemory(
        memory_key="chat_history",
        chat_memory=chat_history,
        return_messages=True
    )

    return memory
