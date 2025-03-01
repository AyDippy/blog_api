from fastapi import APIRouter, HTTPException, status
from api.schemas import PasswordReset, users_collection, NewPassword
from api.oauth2 import create_access_token, get_current_user
from api.send_email import password_reset
from api.utils import get_password_hash



router = APIRouter(
    prefix="/password",
    tags = ["password reset"]
)


@router.post("", response_description="Reset Password")
async def reset_password(user_email: PasswordReset):
    user = await users_collection.find_one({"email": user_email.email})
    if user is not None:
        token = create_access_token({"email": user["email"]})

        reset_link = f"http://localhost:8000/reset?token={token}"

        #send email to user

        await password_reset(subject="Password Reset",
                            email_to= user["email"],
                             body= {"title":"Password Reset",
                                    "name": user["name"],
                                    "reset_link": reset_link})
        return {"message": "Email has been sent"}


    else:
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,
            detail="User with this email not found"
        )


@router.put("", response_description="Reset Password")
async def reset(token: str, new_password: NewPassword):
    request_data = {k: v for k, v in new_password.dict().items() if v is not None}

    # Fixed typo in "password" key
    request_data["password"] = get_password_hash(request_data["password"])

    if len(request_data) >= 1:
        user = await get_current_user(token)

        update_result = await users_collection.update_one({"_id": user["_id"]}, {"$set": request_data})

        if update_result.modified_count == 1:
            updated_user = await users_collection.find_one({"_id": user["_id"]})

            if updated_user is not None:
                # Convert ObjectId to string
                updated_user["_id"] = str(updated_user["_id"])
                return updated_user

    user = await get_current_user(token)
    existing_user = await users_collection.find_one({"_id": user["_id"]})

    if existing_user is not None:
        # Convert ObjectId to string
        existing_user["_id"] = str(existing_user["_id"])
        return existing_user

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User Information not found"
    )