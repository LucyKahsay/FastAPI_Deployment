from __future__ import annotations
from datetime import UTC, datetime
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base

from config import settings

# Inheriting from Base is how you tell SQLAlchemy: 
# "Hey, this isn't just a regular Python class. "
# "This is a database table."
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password_hash:Mapped[str] = mapped_column(String(200), nullable=False)
    image_file: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
        default=None,
    )

    posts: Mapped[list[Post]] = relationship(back_populates="author", cascade= "all, delete-orphan",)

    reset_tokens: Mapped[list[PasswordResetToken]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
# "A User is connected to their reset tokens, and ."
# "reset_tokens lets me go from the User to those tokens."

# "On the other side of this relationship, there is an attribute called author."
# Mapped literally means: "This Python variable is directly "
# "mapped to a live column in the database."
# So the purpose of Mapped is:
# To mark an attribute as something SQLAlchemy should manage.
# A SQLAlchemy-managed attribute that contains a list of Post objects.
# Create an attribute called posts.
# This attribute is managed by SQLAlchemy.
# It will contain a list of Post objects.
# SQLAlchemy should connect it to the relationship called author on the Post class.
# mapped_column is the actual construction worker that builds the table in your database
# Mapped[...] is for Python. It is passive. It just sits there telling your code editor 
# what the data looks like so your auto-complete works.

# mapped_column(...) is for SQL. It is active. It configures the real database settings,
# sets limits, and creates the actual table structure.

# cascade = tell SQLAlchemy what should happen to related objects when 
# operations happen to their parent/relationship.
    @property
    def image_path(self) -> str:
        if self.image_file:
            return f"https://{settings.s3_bucket_name}.s3.{settings.s3_region}.amazonaws.com/profile_pics/{self.image_file}"
        return "/static/profile_pics/default.jpg"


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    date_posted: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )

    likes: Mapped[int] = mapped_column(Integer, default=0, server_default="0")

    author: Mapped[User] = relationship(back_populates="posts")



class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )

    user: Mapped[User] = relationship(back_populates="reset_tokens")
# "A PasswordResetToken is connected to a User, and ."
# "user lets me go from the token to that User."