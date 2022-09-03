from firebase_admin import credentials, firestore, initialize_app
from datetime import datetime
import uuid
import os

current_file_path = os.path.dirname(os.path.realpath(__file__))

cred = credentials.Certificate(os.path.join(current_file_path, "fb.json"))


app = initialize_app(cred)
db = firestore.client(app)


def create_record(data: dict, user: dict):
    """Helper function to create a record in firebase firestore
    Args:
        data (dict): the data to be stored
        user (dict): the user dictionary
    Returns:
        document_id (str): the document id
        record (dict): the record object
    """
    session_id = str(uuid.uuid4().hex)
    record = {
        "user": user.get("id"),
        "time": data.get("elapsed"),
        "output": data.get("output"),
        "upper_limit": data.get("upper_limit"),
        "execution_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "session_id": session_id,
    }
    db.collection("sessions").document(session_id).set(record)

    return session_id, record
