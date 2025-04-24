import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase Admin
cred = credentials.Certificate("keytodoapp.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

source_collection = "users"
target_collection = "users_backup"

# Fetch all docs from source
docs = db.collection(source_collection).stream()

for doc in docs:
    src_data = doc.to_dict()

    # Filter only selected fields
    filtered_src = {
        "name": src_data.get("name"),
        "email": src_data.get("email"),
        "role": src_data.get("role"),
        "is_active": src_data.get("is_active")
    }

    # Get the backup document (if exists)
    backup_ref = db.collection(target_collection).document(doc.id)
    backup_doc = backup_ref.get()

    if not backup_doc.exists:
        # Create if not exists
        backup_ref.set(filtered_src)
        print(f"Created backup for: {doc.id}")
    else:
        # Check if values differ
        current_backup = backup_doc.to_dict()
        if filtered_src != current_backup:
            backup_ref.set(filtered_src)
            print(f"Updated backup for: {doc.id}")
        else:
            print(f"No changes for: {doc.id}")
