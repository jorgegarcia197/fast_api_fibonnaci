from pydantic import BaseModel
from typing import List


class UsersResponse(BaseModel):
    users: list

    class Config:
        schema_extra = {
            "example": {
                "users": [
                    {
                        "id": "02341091234123",
                        "name": "John Doe",
                        "email": "randommail@gmail.com",
                        "phone": "",
                        "username": "johndoe",
                        "password": "password",
                    },
                    {
                        "id": "12341234",
                        "name": "John Doe 2",
                        "email": "randommail2@gmail.com",
                        "phone": "",
                        "username": "johndoe2",
                        "password": "password123",
                    },
                ]
            }
        }


class SessionResponse(BaseModel):
    session: dict

    class Config:
        schema_extra = {
            "example": {
                "session": {
                    "user": "5bee56e9a2c7473b8f2aca7cf41875db",
                    "time": 0.000008400005754083395,
                    "output": [0, 1, 1, 2, 3, 5, 8, 13],
                    "upper_limit": 20,
                    "execution_date": "2022-09-03 11:28:47",
                    "session_id": "4b7031c012ed422da720ce13b173e0ef",
                }
            }
        }


class SessionsByuser(BaseModel):
    sessions: List[str]

    class Config:
        schema_extra = {
            "example": {
                "sessions": [
                    "4b7031c012ed422da720ce13b173e0ef",
                    "3e1398352eb840a292d0cdc4289615e5",
                    "43db1eeb1b6e4140bf58f554b8f3b595",
                    "4b7031c012ed422da720ce13b173e0ef",
                    "5e6f1d1d6ee54dc988bf1dc2be232154",
                    "a47c165bbcc64b8fab16980e1e64e022",
                    "c537f25049f2416092b1f71c7a2dcd8b",
                ]
            }
        }


class UserCreated(BaseModel):
    message: str

    class Config:
        schema_extra = {"example": {"message": "User created successfully"}}


class DeletedSession(BaseModel):
    message: str

    class Config:
        schema_extra = {"example": {"message": "Session deleted successfully"}}
