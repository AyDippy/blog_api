from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from api.schemas import users_collection
from api.utils import verify_password
from api.oauth2 import create_access_token


router = APIRouter(
    prefix="/login",
    tags = ["Authentication"]
)

@router.post("", status_code=status.HTTP_200_OK)
async def login(user_credentials: OAuth2PasswordRequestForm = Depends()):
    user = await users_collection.find_one({"name": user_credentials.username})
    if user and verify_password(user_credentials.password, user["password"]):
        access_token = create_access_token({"email": user["email"]})

        return {"access_token": access_token, "token_type": "bearer"}
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid user credentials"
        )
