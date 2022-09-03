import os
import time
from datetime import datetime

from fastapi import Depends, APIRouter
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from firebase_admin import firestore


from routers.auth import get_current_user, get_user_exception
from utils.firebase_helpers import create_record, db
from utils.random_utils import create_user_dir, write_session_file
from schemas import input_schemas, output_schemas

router = APIRouter()

current_file_path = os.path.dirname(os.path.realpath(__file__))
output_path = os.path.join(current_file_path, "../output")


def fib(x, y, upperLimit):
    # recursive solutiondef fib(x, y, upperLimit):
    return [x] + fib(y, (x + y), upperLimit) if x < upperLimit else [x]


@router.post("/fibbonacci", response_model=output_schemas.SessionResponse)
async def get_fib(
    request_body: input_schemas.FibRequest, user=Depends(get_current_user)
) -> output_schemas.SessionResponse:
    """This function is the main endpoint for the fibonnaci series

    Args:
        number (int): the index up to the fibonnaci series will be calculated

    Returns:
        result (int): The sum at that index of the fib serie
    """
    if not user:
        return get_user_exception()
    timer = time.perf_counter()
    output = fib(0, 1, request_body.upper_limit)[:-1]
    elapsed = time.perf_counter() - timer
    document_id, record = create_record(
        {"output": output, "upper_limit": request_body.upper_limit, "elapsed": elapsed},
        user,
    )
    user_path = create_user_dir(user, output_path)
    write_session_file(document_id, record, user_path)
    record_schema = output_schemas.SessionResponse(session=record)

    return JSONResponse(status_code=200, content=record_schema.dict())


@router.get("/all_sessions", response_model=output_schemas.SessionsByuser)
async def fetch_sessions():
    """This function fetches all the sessions from the database

    Returns:
        Response (JSONRespose): A JSON response with a list of all the sessions
    """
    sessions = [
        sessions.to_dict().get("session_id")
        for sessions in db.collection("sessions").get()
    ]
    if not sessions:
        return JSONResponse(status_code=404, content={"message": "No sessions found"})
    return JSONResponse(status_code=200, content={"sessions": sessions})


@router.get("/all_users", response_model=output_schemas.UsersResponse)
async def fetch_users() -> output_schemas.UsersResponse:
    """This function fetches all the users from the database

    Returns:
        Response (JSONResponse): A JSON response with a list of all the users
    """
    users = db.collection("users").get()
    if not users:
        return JSONResponse(status_code=404, content={"message": "No users found"})
    users = output_schemas.UsersResponse(users=[user.to_dict() for user in users])

    return JSONResponse(status_code=200, content=users.dict())


@router.get("/sessions_by_user/", response_model=output_schemas.SessionsByuser)
async def fetch_sessions_by_user(user: dict = Depends(get_current_user)):
    """This function fetches all the sessions by a user from the database

    Args:
        user (dict, optional): The dictionary that authenticates the user from the JWT Token. Defaults to Depends(get_current_user).

    Raises:
        http_exception: Raises an HTTPException if the user is not found

    Returns:
        Response (JSONResponse): A JSON response with a list of all the sessions by a user
    """
    if not user:
        raise http_exception()
    sessions = [
        sessions.to_dict().get("session_id")
        for sessions in db.collection("sessions")
        .where("user", "==", user.get("id"))
        .get()
    ]
    if not sessions:
        return JSONResponse(status_code=404, content={"message": "No sessions found"})
    return JSONResponse(status_code=200, content={user.get("id"): sessions})


@router.get("/session_by_id/{id}", response_model=output_schemas.SessionResponse)
async def fetch_sessions_by_id(id: str, user: dict = Depends(get_current_user)):
    """This function fetches a session with given id from the database

    Args:
        id (str): The id of the session
        user (dict, optional): The dictionary that authenticates the user from the JWT Token. Defaults to Depends(get_current_user).

    Raises:
        http_exception: Raises an HTTPException if the user is not found

    Returns:
        Response (JSONResponse): A JSON response with the information of that particular session

    """
    if not user:
        raise get_user_exception()
    session = db.collection("sessions").document(id).get()
    if not session.exists:
        return JSONResponse(status_code=404, content={"message": "No session found"})
    return JSONResponse(status_code=200, content=session.to_dict())


@router.delete("/session/{id}", response_model=output_schemas.DeletedSession)
async def delete_session(id: str, user: dict = Depends(get_current_user)):
    """This function deletes a session with given id from the database

    Args:
        id (str): The id of the session
        user (dict, optional): The dictionary that authenticates the user from the JWT Token. Defaults to Depends(get_current_user).

    Raises:
        get_user_exception: Raises an HTTPException if the user is not found

    Returns:
        Response: A successful response if the session was deleted
    """
    if not user:
        raise get_user_exception()
    session = db.collection("sessions").document(id).get().to_dict()
    if session.get("user") != user.get("id"):
        return JSONResponse(
            status_code=403, content={"message": "Forbidden, not your session"}
        )
    db.collection("sessions").document(id).delete()
    return successful_response(200)


def successful_response(status_code: int):
    """Helper function to return a successful response

    Args:
        status_code (int): The status code of the response

    Returns:
        dict: A dictionary with the status code and a message
    """
    return {"status": status_code, "transaction": "Successful"}


def http_exception():
    return HTTPException(status_code=404, detail="User not found")
