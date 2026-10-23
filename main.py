from fastapi import FastAPI, Request, HTTPException, status, Depends
from fastapi.staticfiles import StaticFiles
# "Serve files from a folder."
from fastapi.templating import Jinja2Templates
# This Jinja2Templates class knows how to load HTML files.

from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exceptions import RequestValidationError

from typing import Annotated
from sqlalchemy import select, func, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from contextlib import asynccontextmanager
from routers import posts, users 

from config import settings

from fastapi.exception_handlers import (
    http_exception_handler, 
    request_validation_exception_handler,
)   
import models
from database import  engine, get_db
# Get the SQLAlchemy base and database connection setup.


# Base.metadata.create_all(bind=engine)
# Create the tables described by my models in that database.
#  Take all the tables defined by my SQLAlchemy models and
# create them inside blog.db using this engine."

# manage what happens when your FastAPI app starts and stops.
# START → create tables → yield → app runs → STOP → clean up.
@asynccontextmanager
async def lifespan(_app:FastAPI):
##startup
    
    yield

    await engine.dispose()
# Start → create database tables → let the app run → 
# stop → clean up the database engine.
            #     FastAPI starts
            #            ↓
            #   lifespan() starts
            #            ↓
            #   Create DB tables
            #            ↓
            #          yield
            #            ↓
            #   🚀 APP RUNNING
            #            ↓
            #   GET/POST/PATCH/etc.
            #            ↓
            #     App shuts down
            #            ↓
            #   dispose database engine
            #            ↓
            #          DONE


app = FastAPI(lifespan= lifespan)
# "FastAPI, use MY lifespan function to handle startup and shutdown."

app.mount("/static", StaticFiles(directory="static"), name="static")



templates = Jinja2Templates(directory= "templates")

app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(posts.router, prefix="/api/posts", tags=["posts"])




# The tags setting tells FastAPI how to visually group your routes on
# that webpage.All the user routes will be nicely bundled together 
# under a big "users" folder header, and all the post routes will 
# be grouped under a "posts" header, making your API beautifully 
# organized for anyone reading it.





# @app.get("/")
# @app.get("/posts")
# def home(request: Request):
#     return templates.TemplateResponse(request, "home.html", {"posts": posts, "title":"Home"})
# templates is object of the Jinja2Templates class and the TemplateResponse is method created by the fastapi developers
# request object is literally a Python object full of information about what the browser sent.
# "Jinja, I'm giving you a variable called posts. "
# "Its value is whatever is stored in my Python variable posts."


## Health Check Endpoint
@app.get("/health")
async def health_check(db: Annotated[AsyncSession, Depends(get_db)]):
    try:
        await db.execute(text("SELECT 1"))
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database unavailable",
        ) from exc
    return {"status": "healthy"}

@app.get("/", include_in_schema=False, name="home")
@app.get("/posts", include_in_schema=False, name="posts")
async def home(request: Request, db: Annotated[AsyncSession, Depends(get_db)]):
    count_result = await db.execute(select(func.count()).select_from(models.Post))
    total = count_result.scalar() or 0

    result = await db.execute(
        select(models.Post)
        .options(selectinload(models.Post.author))
        .order_by(models.Post.date_posted.desc())
        .limit(settings.posts_per_page),
    )
    posts = result.scalars().all()

    has_more = len(posts) < total

    return templates.TemplateResponse(
        request,
        "home.html",
        {
            "posts": posts,
            "title": "Home",
            "limit": settings.posts_per_page,
            "has_more": has_more,
        },
    )

@app.get("/posts/{post_id}", include_in_schema=False)
async def post_page(
    request: Request, post_id: int, db: Annotated[AsyncSession, Depends(get_db)]
    ):
    result =await db.execute(select(models.Post)
                             .options(selectinload(models.Post.author))
                             .where(models.Post.id == post_id)
                             )
    post = result.scalars().first()
    if post:
        title = post.title[:50]
        return templates.TemplateResponse(
            request,
            "post.html",
            {"post": post, "title": title},
        )
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")


##user_posts_page route - paginated
@app.get("/users/{user_id}/posts", include_in_schema=False, name="user_posts")
async def user_posts_page(
    request: Request,
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    count_result = await db.execute(
        select(func.count())
        .select_from(models.Post)
        .where(models.Post.user_id == user_id),
    )
    total = count_result.scalar() or 0

    result = await db.execute(
        select(models.Post)
        .options(selectinload(models.Post.author))
        .where(models.Post.user_id == user_id)
        .order_by(models.Post.date_posted.desc())
        .limit(settings.posts_per_page),
    )
    posts = result.scalars().all()

    has_more = len(posts) < total

    return templates.TemplateResponse(
        request,
        "user_posts.html",
        {
            "posts": posts,
            "user": user,
            "title": f"{user.username}'s Posts",
            "limit": settings.posts_per_page,
            "has_more": has_more,
        },
    )






# @app.post(
#     "/api/users",
#     response_model=UserResponse,
#     status_code=status.HTTP_201_CREATED,
# )

# def create_user(user: UserCreate, db:Annotated[Session, Depends(get_db)]):
    
# # Before running create_user, get me a database session using get_db()."
# # "This parameter is a Session, and FastAPI should obtain it using get_db."
# # this one is for the Annotated part 

# # user → UserCreate object

# # db → SQLAlchemy Session

#     result = db.execute(
#         select(models.User).where(models.User.username == user.username)
#     )
#     existing_user= result.scalars().first()
#     # "Give me the first User object found by this query. if there is nothing give me None"
#     if existing_user:
#         raise HTTPException(
#             status_code= status.HTTP_400_BAD_REQUEST,
#             detail= "username already exists",
#         )


#     result = db.execute(
#             select(models.User).where(models.User.email == user.email)
#         )
#     existing_email= result.scalars().first()
#         # "Give me the first User object found by this query. if there is nothing give me None"
#     if existing_email:
#             raise HTTPException(
#                 status_code= status.HTTP_400_BAD_REQUEST,
#                 detail= "Email already exists",
#             )
#     # "Use the User blueprint/class from models.py to create a new User object."
#     # "Using my User model, create a Python object representing this new user.
#     new_user= models.User(
#         username=user.username,
#         email=user.email,

#     )

#     db.add(new_user)
#     db.commit()
#     db.refresh(new_user)

#     return new_user

@app.get("/login", include_in_schema=False)
async def login_page(request: Request):
    return templates.TemplateResponse(
        request,
        "login.html",
        {"title": "Login"},
    )


@app.get("/register", include_in_schema=False)
async def register_page(request: Request):
    return templates.TemplateResponse(
        request,
        "register.html",
        {"title": "Register"},
    )



@app.get("/account", include_in_schema=False)
async def account_page(request: Request):
    return templates.TemplateResponse(
        request,
        "account.html",
        {"title": "Account"},
    )


@app.get("/forgot-password", include_in_schema=False)
async def forgot_password_page(request: Request):
    return templates.TemplateResponse(
        request,
        "forgot_password.html",
        {"title": "Forgot Password"},
    )


@app.get("/reset-password", include_in_schema=False)
async def reset_password_page(request: Request):
    response = templates.TemplateResponse(
        request,
        "reset_password.html",
        {"title": "Reset Password"},
    )
    response.headers["Referrer-Policy"] = "no-referrer"
    return response





@app.exception_handler(StarletteHTTPException)
async def general_http_exception_handler(request: Request, exception: StarletteHTTPException):
    

    if request.url.path.startswith("/api"):
        return await http_exception_handler(request, exception)

    message = (
        exception.detail
        if exception.detail
        else "An error occurred. Please check your request and try again."
    )
       
    return templates.TemplateResponse(
        request,
        "error.html",
        {
            "status_code": exception.status_code,
            "title": exception.status_code,
            "message": message,
        },
        status_code=exception.status_code,
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exception: RequestValidationError):
    if request.url.path.startswith("/api"):
        return await request_validation_exception_handler(request, exception)
        
    return templates.TemplateResponse(
        request,
        "error.html",
        {
            "status_code": status.HTTP_422_UNPROCESSABLE_CONTENT,
            "title": status.HTTP_422_UNPROCESSABLE_CONTENT,
            "message": "Invalid request. Please check your input and try again.",
        },
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
    )