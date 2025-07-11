from dotenv import load_dotenv
import os
import firebase_admin
from firebase_admin import credentials, firestore

load_dotenv()

#clave
cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "firebase/firebase_key.json")

#inicializa Firebase si no se ha hecho ya
if not firebase_admin._apps:
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)

#cliente de Firestore disponible para importar desde otros módulos
db = firestore.client()
