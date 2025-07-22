from google.cloud import firestore
from typing import List, Dict
from langchain.schema import BaseMessage, HumanMessage, AIMessage
from langchain_core.chat_history import BaseChatMessageHistory
from firebase.client import db

def _message_to_dict(message: BaseMessage) -> Dict:
    return {
        "type": message.__class__.__name__,
        "content": message.content,
    }

def _dict_to_message(d: Dict) -> BaseMessage:
    if d["type"] == "HumanMessage":
        return HumanMessage(content=d["content"])
    elif d["type"] == "AIMessage":
        return AIMessage(content=d["content"])
    else:
        raise ValueError(f"Tipo de mensaje desconocido: {d['type']}")

class FirestoreChatHistory(BaseChatMessageHistory):
    """
    Clase compatible con LangChain que guarda historial de mensajes simples
    en Firestore (colección por default: langchain_memory).
    """
    def __init__(self, user_id: str, namespace: str = "langchain_memory"):
        self.user_id = user_id
        self.namespace = namespace
        self.collection = db.collection(namespace).document(user_id)

    @property
    def messages(self) -> List[BaseMessage]:
        doc = self.collection.get()
        if not doc.exists:
            return []
        return [_dict_to_message(d) for d in doc.to_dict().get("messages", [])]

    def add_user_message(self, message: str) -> None:
        self._append_message(HumanMessage(content=message))

    def add_ai_message(self, message: str) -> None:
        self._append_message(AIMessage(content=message))

    def clear(self) -> None:
        self.collection.set({"messages": []})

    def _append_message(self, message: BaseMessage) -> None:
        doc = self.collection.get()
        current = doc.to_dict() if doc.exists else {}
        messages = current.get("messages", [])
        messages.append(_message_to_dict(message))
        self.collection.set({"messages": messages})
