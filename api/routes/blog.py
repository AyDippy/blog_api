from fastapi import APIRouter, HTTPException, status, Depends
from api.oauth2 import get_current_user
from api.schemas import BlogContent, BlogContentResponse, blog_collection
from datetime import datetime
from bson.objectid import ObjectId
from fastapi.responses import JSONResponse

router = APIRouter(
    prefix="/blog",
    tags= ["Blog Content Updated"]
)


@router.post("", response_description="Create Blog content", response_model=BlogContentResponse)
async def create_blog(blog_contents: BlogContent, current_user = Depends(get_current_user)):
    try:
        # Convert Pydantic model to dict with MongoDB-compatible field names
        blog_content = blog_contents.model_dump(by_alias=True, exclude={"id"})

        #add additionjal information
        blog_content["author_name"] = current_user["name"]
        blog_content["author_id"] = str(current_user["_id"])
        blog_content["created_at"] = str(datetime.utcnow())

        #collection for blogs in my mongo db database
        new_blog_content = await blog_collection.insert_one(blog_content)

        created_blog_post = await blog_collection.find_one({"_id": new_blog_content.inserted_id})
        return created_blog_post

    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("", response_description="Get blog Content", response_model=list[BlogContentResponse])
async def get_blogs(limit: int = 4, orderby:str = "created_at"):
    try:
        blog_posts = await blog_collection.find({"$query": {}, "$orderby": -1}).to_list(limit)
        return blog_posts

    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/{id}", response_description="Get blog Content", response_model=BlogContentResponse)
async def get_blogs(id: str):
    try:
        object_id = ObjectId(id)
        blog_posts = await blog_collection.find_one({"_id": object_id})
        if blog_posts is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Blog with id not found"
            )
        return blog_posts

    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.put("/{id}", response_description="Update Blog Post", response_model=BlogContentResponse)
async def update_blog(id: str, blog_content: BlogContent, current_user = Depends(get_current_user)):
    if blog_post := await blog_collection.find_one({'_id': ObjectId(id)}):
        if blog_post["author_id"] == str(current_user["_id"]):

            try:
                blog_content = {k: v for k, v in blog_content.dict().items() if v is not None}

                if len(blog_content) >= 1:
                    update_result = await blog_collection.update_one({"_id": ObjectId(id)}, {"$set": blog_content})

                    if update_result.modified_count == 1:
                        if (updated_blog_post := await blog_collection.find_one({"_id": ObjectId(id)})) is not None:
                            return updated_blog_post

                if (existing_post := await blog_collection.find_one({"_id": ObjectId(id)})) is not None:
                    return existing_post

                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail= "Blog content not found"
                )
            except Exception as e:
                print(e)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Internal Serval Error"
                )

        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="You're not the author of this blog post"
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog content not found"
        )

@router.delete('/{id}', response_description="Delete Blog Post")
async def delete_blog_post(id:str, current_user = Depends(get_current_user)):
    objectid = ObjectId(id)
    if blog_post := await blog_collection.find_one({"_id": objectid}):

        if blog_post["author_id"] == str(current_user["_id"]):

            try:
                delete_result = await blog_collection.delete_one({"_id": objectid})
                if delete_result.deleted_count == 1:
                    return JSONResponse(content={"message": f"Blog with ID {id} deleted successfully"})
                raise HTTPException(
                    status_code= status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Internal server error"
                )

            except Exception as e:
                print(e)
                raise HTTPException(
                    status_code= status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Internal server error"
                    )
        else:
            raise HTTPException(
                status_code= status.HTTP_401_UNAUTHORIZED,
                detail= "You are not authorized to delete this blog post"
            )
    else:
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,
            detail="Blog content not found"
        )