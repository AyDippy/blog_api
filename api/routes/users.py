from fastapi import APIRouter, HTTPException, status
from api.schemas import User, users_collection, UserResponse
from fastapi.encoders import jsonable_encoder
from api.utils import get_password_hash, verify_password
from api.send_email import send_registration_mail
import secrets


router = APIRouter(
    tags = ["Users Routes"]
)


@router.post(
    "/registration",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    description="Register a new user"
)
async def registration(user_info: User):
    # Convert Pydantic model to dict with MongoDB-compatible field names
    user = user_info.model_dump(by_alias=True, exclude={"id"})

    # Check for duplicates using modern MongoDB syntax
    if await users_collection.find_one({"name": user_info.name}):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists"
        )

    if await users_collection.find_one({"email": user_info.email}):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already exists"
        )

    # Hash password - accessing model attribute directly
    user["password"] = get_password_hash(user_info.password)

    # Add API key
    user["apiKey"] = secrets.token_hex(30)

    # Insert user and handle potential errors
    try:
        result = await users_collection.insert_one(user)

        # Fetch and return created user
        if created_user := await users_collection.find_one(
                {"_id": result.inserted_id}
        ):
            # Sending Emails
            await send_registration_mail(subject="Registration Successful", email_to=user_info.email,
                                         body={
                                             "title": "Registration successful",
                                             "name": user_info.name
                                         })

            return created_user

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve created user"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user: {str(e)}"
        )




