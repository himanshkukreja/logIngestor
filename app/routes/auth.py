from fastapi import Body, HTTPException, APIRouter,Depends,Header,Request
from controllers import auth_controllers
from db.models import Auth
from fastapi.security import OAuth2PasswordBearer
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, SecurityScopes
router = APIRouter(tags=['Auth'], prefix="")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.post("/register")
async def register_user(user_data: Auth.UserCreateModel):
    return await  auth_controllers.register_user(user_data)
    

@router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    return await auth_controllers.login_for_access_token(form_data)

@router.get("/validate-token")
async def validate_token(token: str = Depends(oauth2_scheme)):
    return await auth_controllers.validate_token(token)

    
@router.get("/login")
async def login(request: Request):
    return await auth_controllers.login(request)

@router.get("/signup")
async def signup(request: Request):
    return await auth_controllers.signup(request)

