import os
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from api.schemas import TokenData, users_collection
from jose import JWTError, jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv


load_dotenv()


secret_key = os.getenv("SECRET_KEY")


ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def create_access_token(payload: dict):
    to_encode = payload.copy()

    expiration_time = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expiration_time})
    jw_token = jwt.encode(to_encode, key=secret_key, algorithm=ALGORITHM)

    return jw_token

def verify_access_token(token:str, credential_exception):
    try:
        payload = jwt.decode(token, key=secret_key, algorithms=ALGORITHM)

        email: str = payload.get("email")

        if not email:
            raise credential_exception

        token_data = TokenData(email=email)
        return token_data

    except JWTError:
        raise credential_exception


async def get_current_user(token:str = Depends(oauth2_scheme)):
    credential_exception = HTTPException(
        status_code= status.HTTP_401_UNAUTHORIZED,
        detail="Token could not be verified",
        headers = {"WWW-AUTHENTICATE": "Bearer"}
    )
    current_user_email = verify_access_token(token, credential_exception).email

    current_user = await users_collection.find_one({"email": current_user_email})

    return current_user