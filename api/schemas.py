import motor.motor_asyncio
from dotenv import load_dotenv
import os
from bson import ObjectId
from pydantic import BaseModel, Field, EmailStr, ConfigDict, BeforeValidator
from pydantic_core import CoreSchema, core_schema
from pydantic import GetJsonSchemaHandler
from typing import Any, Annotated, Optional



#load env
load_dotenv()

client = motor.motor_asyncio.AsyncIOMotorClient(os.getenv("MONGODB_URL"))
db = client.get_database("blogAPIdb")
users_collection = db.get_collection("users")

# Represents an ObjectId field in the database.
# It will be represented as a `str` on the model so that it can be serialized to JSON.
PyObjectId = Annotated[str, BeforeValidator(str)]

# Then fix the User models to use string IDs
class User(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    name: str = Field(...)
    email: EmailStr = Field(...)
    password: str = Field(...)

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "name": "John Doe",
                "email": "jdoe@example.com",
                "password": "secret_code"
            }
        }
    )

class UserResponse(BaseModel):
    name: str = Field(...)
    email: EmailStr = Field(...)

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "name": "John Doe",
                "email": "jdoe@example.com"
            }
        }
    )


class TokenData(BaseModel):
    email: str

class PasswordReset(BaseModel):
    email: str

class NewPassword(BaseModel):
    password: str

class BlogContent(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    title: str = Field(...)
    body: str = Field(...)

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "title": "Blog title",
                "body": "Blog content"
            }
        }
    )


class BlogContentResponse(BaseModel):
    title: str = Field(...)
    body: str = Field(...)
    author_name: str = Field(...)
    author_id: str = Field(...)
    created_at: str = Field(...)

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "title": "Blog title",
                "body": "Blog content",
                "author_name": "John Doe",
                "author_id": "ID of author",
                "created_at": "date created"
            }
        }
    )


blog_collection = db.get_collection("blogs")
