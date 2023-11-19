from pydantic import BaseModel, Field
from typing import List,Optional

class User(BaseModel):
    username: str
    hashed_password: str  # Include the hashed_password field
    disabled: Optional[bool] = None
    roles: List[str] = []

class TokenData(BaseModel):
    username: Optional[str] = None
    roles: List[str] = []

class UserCreateModel(BaseModel):
    username: str
    password: str
    roles: List[str] = ["user"]