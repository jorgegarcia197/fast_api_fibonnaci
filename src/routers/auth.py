import uuid
from datetime import datetime, timedelta
from typing import List, Optional

import firebase_admin
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from firebase_admin import credentials, firestore
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, Field
from schemas import input_schemas, output_schemas
from utils.firebase_helpers import db

SECRET_KEY = "KlgH6AzYDeZeGwD288to79I3vTHT8wp7"
ALGORITHM = "HS256"

router = APIRouter()


class CreateUser(BaseModel):
    """Pydantic model fo the user creation"""

    username: str
    email: Optional[str]
    name: str
    password: str
    phone_number: Optional[str] = None
    id: str = Field(None)

    class Config:
        schema_extra = {
            "example": {
                "username": "TestUser",
                "email": "test.user97@gmail.com",
                "name": "Test User",
                "password": "UserPassword",
            }
        }


bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")


def get_password_hash(password):
    return bcrypt_context.hash(password)


def verify_password(plain_password, hashed_password):
    return bcrypt_context.verify(plain_password, hashed_password)


def create_access_token(
    username: str, user_id: int, expires_delta: Optional[timedelta] = None
):
    """This function creates the access token for the user

    Args:
        username (str): The username of the user
        user_id (int): The user id
        expires_delta (Optional[timedelta], optional): Optional expiration time. Defaults to None.

    Returns:
        token: JWT access token
    """

    encode = {"sub": username, "id": user_id}
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    encode.update({"exp": expire})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


def authenticate_user(username: str, password: str, db=db):
    """This function authenticates the user with the username and password from the database


    Args:
        username (str): The username of the user
        password (str): The password of the user
        db (firestore.client, optional): The firestore object that we interact with. Defaults to db.

    Returns:
        user_info (dict|False): The user info if the user exists, False otherwise
    """
    user = db.collection("users").where("username", "==", username).get()
    if not user:
        return False
    user_info = user[0].to_dict()
    if not verify_password(password, user_info.get("password")):
        return False
    return user_info


async def get_current_user(token: str = Depends(oauth2_bearer)):
    """This function gets the current user from the token

    Args:
        token (str, optional): The outhbearer for the swaggerUI. Defaults to Depends(oauth2_bearer).

    Raises:
        get_user_exception: The exception for the user not found case

    Returns:
        dict: The username and the id of the user
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        if username is None or user_id is None:
            raise get_user_exception()
        return {"username": username, "id": user_id}
    except JWTError:
        raise get_user_exception()


@router.post("/create_user", response_model=output_schemas.UserCreated)
async def create_new_user(user: CreateUser):
    """API endpoint to create a new user

    Args:
        user (CreateUser): The user object

    Returns:
        Response (JSONResponse): The response object successful when the user is created
    """
    user.password = get_password_hash(user.password)
    user.id = str(uuid.uuid4().hex)

    db.collection("users").document(user.id).set(user.dict())
    return JSONResponse(
        status_code=201, content={"message": "User created successfully"}
    )


@router.post("/token")
async def login_for_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """API endpoint to get the token for the user
    This could also be done via the swaggerUI


    Args:
        form_data (OAuth2PasswordRequestForm, optional): The Oauth Form with the user and password flow. Defaults to Depends().

    Raises:
        token_exception: The exception for the token if the password or username does not match

    Returns:
        response (JSONResponse): The response object with the token and token type
    """
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise token_exception()
    token_expires = timedelta(minutes=20)
    access_token = create_access_token(
        user.get("username"), user.get("id"), token_expires
    )
    return JSONResponse(
        status_code=200, content={"access_token": access_token, "token_type": "bearer"}
    )


# Exceptions
def get_user_exception():
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return credentials_exception


def token_exception():
    token_exception_response = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return token_exception_response
