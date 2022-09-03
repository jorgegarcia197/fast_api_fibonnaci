import os
import json


def create_user_dir(user: dict, filepath: str):
    """This function creates a directory for a user in order to store their sessions

    Args:
        user (dict): the user dictionary

    Returns:
        path: the user path
    """

    path = os.path.join(filepath)
    if not os.path.exists(path):
        os.mkdir(path)
    user_path = os.path.join(path, user.get("id"))
    if not os.path.exists(user_path):
        os.mkdir(user_path)
    return user_path


def write_session_file(session_id, data, user_path):
    """This function writes the session data to a file

    Args:
        session_id (str): the session id
        data (dict): the data to be written
        user_path (str): the user path

    Returns:
        None
    """
    session_id = f"{session_id}.json"
    file = os.path.join(user_path, session_id)
    with open(file, "w") as f:
        json.dump(data, f)
    return None
