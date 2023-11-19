from db import db_config
from db.models import Auth
from config import config
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, SecurityScopes
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import List,Optional
from fastapi import HTTPException,Security,Depends,status

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def insert_new_user_to_db(new_user):
    db_config.user_collection.insert_one(new_user)
    
    
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def authenticate_user(username: str, password: str):
    user = db_config.user_collection.find_one({"username": username})
    if not user:
        return False
    user = Auth.User(**user)  # Convert the dictionary to a User model instance
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, config.jwt_secret_key, algorithm=config.jwt_algorithm)
    return encoded_jwt

def get_user_by_username(username: str):
    user_document = db_config.user_collection.find_one({"username": username})
    if user_document:
        return Auth.User(**user_document)
    return None

async def create_user(user_data: dict):
    user_data["hashed_password"] = pwd_context.hash(user_data["password"])
    del user_data["password"]  # Remove plain password
    db_config.user_collection.insert_one(user_data)
    

def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return User(**user_dict)


def get_current_user(security_scopes: SecurityScopes, token: str= Depends(oauth2_scheme)):
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )
    try:
        payload = jwt.decode(token, config.jwt_secret_key, algorithms=[config.jwt_algorithm])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_roles = payload.get("roles", [])
        token_data = Auth.TokenData(roles=token_roles, username=username)
    
    except JWTError:
        raise credentials_exception
   
    # Fetch user from MongoDB
    user = get_user_by_username(username=token_data.username)
    if user is None:
        raise credentials_exception
    
    for scope in security_scopes.scopes:
        print(scope,token_data)
        if scope in token_data.roles:
            return user
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not enough permissions",
        headers={"WWW-Authenticate": authenticate_value},
    )
    

def get_current_active_user(current_user: Auth.User = Security(get_current_user, scopes=["admin"])):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
