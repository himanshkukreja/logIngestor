from config import config
from jose import JWTError, jwt
from datetime import datetime, timedelta
from services import auth_services
from fastapi.templating import Jinja2Templates
from db.models import Auth
from fastapi import Request,HTTPException
from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

templates = Jinja2Templates(directory="templates")


async def register_user(user_data: Auth.UserCreateModel):
    # Hash the user's password
    hashed_password = pwd_context.hash(user_data.password)
    new_user = {
        "username": user_data.username,
        "hashed_password": hashed_password,
        "roles": user_data.roles
    }
    # Insert the new user into your MongoDB collection
    auth_services.insert_new_user_to_db(new_user)
    
    return {"message": "User created successfully"}

async def login_for_access_token(form_data):
    user = auth_services.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    access_token_expires = timedelta(minutes=config.access_token_expiry_in_minutes)
    access_token = auth_services.create_access_token(
        data={"sub": user.username,"roles": user.roles}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


async def validate_token(token:str):
    try:
        payload = jwt.decode(token, config.jwt_secret_key, algorithms=[config.jwt_algorithm])
        return {"message": "Token is valid"}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


async def signup(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})
