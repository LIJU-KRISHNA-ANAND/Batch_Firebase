import os
import json
import base64
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv

# --- Load environment variables ---
load_dotenv()

# --- Load Firebase credentials ---
firebase_key_base64 = os.getenv('FIREBASE_KEY_BASE64')

if firebase_key_base64:
    firebase_key_json = base64.b64decode(firebase_key_base64).decode('utf-8')
    cred = credentials.Certificate(json.loads(firebase_key_json))
else:
    raise ValueError("Firebase credentials not provided!")

firebase_admin.initialize_app(cred)
db = firestore.client()

# --- Read logging mode from config file ---
def read_log_mode():
    try:
        with open("log_config.txt", "r") as f:
            for line in f:
                if line.startswith("PRINT_MODE="):
                    return line.strip().split("=")[1].lower()
    except FileNotFoundError:
        return "verbose"  # default to verbose if not found

log_mode = read_log_mode()

def log(message):
    with open("backup_log.txt", "a") as f:
        f.write(message + "\n")

# --- Collections ---
source_collection = "users"
target_collection = "users_backup"

# --- Backup operation ---
docs = db.collection(source_collection).stream()

for doc in docs:
    src_data = doc.to_dict()

    filtered_src = {
        "name": src_data.get("name"),
        "email": src_data.get("email"),
        "role": src_data.get("role"),
        "is_active": src_data.get("is_active")
    }

    backup_ref = db.collection(target_collection).document(doc.id)
    backup_doc = backup_ref.get()

    if not backup_doc.exists:
        backup_ref.set(filtered_src)
        log(f"Created backup for: {doc.id}")
    else:
        current_backup = backup_doc.to_dict()
        if filtered_src != current_backup:
            backup_ref.set(filtered_src)
            log(f"Updated backup for: {doc.id}")
        else:
            log(f"No changes for: {doc.id}")
