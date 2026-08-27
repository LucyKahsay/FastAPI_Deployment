from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

import models
from database import get_db
from schemas import PostCreate, PostResponse, PostUpdate
from auth import CurrentUser

router = APIRouter()


@router.get("", response_model=list[PostResponse])
async def get_posts(db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(
        select(models.Post).options(selectinload(models.Post.author)).order_by(models.Post.date_posted.desc()),
    )
    posts = result.scalars().all()
    return posts 


 

@router.get("/{post_id}", response_model=PostResponse)
async def get_post(post_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(
        select(models.Post)
        .options(selectinload(models.Post.author))
        .where(models.Post.id == post_id),
    )
    post = result.scalars().first()
    if post:
        return post
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

@router.post(
    "",
    response_model=PostResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_post(
    post: PostCreate, 
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)]
    ):


    

    new_post = models.Post(
        title=post.title,
        content=post.content,
        user_id=current_user.id,
    )
    db.add(new_post)
    await db.commit()
    await db.refresh(new_post, attribute_names=["author"])
    return new_post



# # "This PUT endpoint expects the client to send me a complete set of post information 
# # in the request body. Validate that information using PostCreate, turn it into an object,
# # and give that object to my function under the name post_data.
# @app.put("/api/posts/{post_id}", response_model=PostResponse)
# def update_post_full(
#     post_id: int, 
#     post_data: PostCreate , 
#     db: Annotated[Session, Depends(get_db)],
#     ):

#     result = db.execute(select(models.Post).where(models.Post.id == post_id))
#     post = result.scalars().first()
#     # "Take the database result → unwrap it into my model objects → give me the first one "
#     # "→ store it in post."
#     if not post:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND, 
#             detail="Post not found") 
#     if post_data.user_id != post.user_id:
#     #    "If the user ID that came in with the new data is NOT the same as "
#     #    "the user ID that the existing post currently belongs to..." 
#         result =db.execute(
#             select(models.User).where(models.User.id ==post_data.user_id),

#         )
#         user = result.scalars().first()
#         if not user:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="User not found",
#             )
#     post.title = post_data.title
#     post.content = post_data.content
#     post.user_id = post_data.user_id

#     db.commit()
#     db.refresh(post)
#     return post


@router.put("/{post_id}", response_model=PostResponse)
async def update_post_full(
    post_id: int,
    current_user: CurrentUser,
    post_data: PostCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(select(models.Post).where(models.Post.id == post_id))
    post = result.scalars().first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )
    
    if post.user_id != current_user.id:
        raise HTTPException(
            status_code= status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this post",
        )
        
    post.title = post_data.title
    post.content = post_data.content


    await db.commit()
    await db.refresh(post, attribute_names=["author"])
    return post



# @app.patch("/api/posts/{post_id}", response_model=PostResponse)
# def update_post_partial(
#     post_id: int, 
#     post_data: PostUpdate , 
#     db: Annotated[Session, Depends(get_db)],
#     ):

#     result = db.execute(select(models.Post).where(models.Post.id == post_id))
#     post = result.scalars().first()
#     # "Take the database result → unwrap it into my model objects → give me the first one "
#     # "→ store it in post."
#     if not post:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND, 
#             detail="Post not found") 
#     update_data= post_data.model_dump(exclude_unset= True)
# # "Give me only the fields the client actually asked me to change."
   
#     for field, value in update_data.items():
#         setattr(post, field, value)

#     db.commit()
#     db.refresh(post)
#     return post

@router.patch("/{post_id}", response_model=PostResponse)
async def update_post_partial(
    post_id: int,
    post_data: PostUpdate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(select(models.Post).where(models.Post.id == post_id))
    post = result.scalars().first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )

    if post.user_id != current_user.id:
        raise HTTPException(
            status_code= status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this post",
        )

    update_data = post_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(post, field, value)

    await db.commit()
    await db.refresh(post, attribute_names=["author"])
    return post


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(post_id: int,current_user:CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.Post).where(models.Post.id == post_id))
    post = result.scalars().first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )

    if post.user_id != current_user.id:
            raise HTTPException(
                status_code= status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this post",
            )

    await db.delete(post)
    await db.commit()
