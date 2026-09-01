from database import Base
from sqlalchemy import Column, Integer, String, ForeignKey

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, index=True, primary_key=True)
    username = Column(String, index=True, unique=True)
    hashed_password = Column(String)
    role = Column(String, default="user")

