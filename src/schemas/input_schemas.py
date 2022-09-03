from pydantic import BaseModel


class FibRequest(BaseModel):
    upper_limit: int

    class Config:
        schema_extra = {"example": {"upper_limit": 10}}
        

