from auth import create_hash_password, create_jwt_token, verify_password, decode_token
import models, schemas
from database import engine, SessionLocal
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from fastapi import HTTPException
from schemas import UserCreate
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm 

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(token: str = Depends(OAuth2PasswordBearer(tokenUrl="users/login")),
                     db: Session = Depends(get_db)):
    user = decode_token(token)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Could not validate user credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )
    username = user.get("sub")
    db_user = db.query(models.User).filter(models.User.username == username).first()
    if db_user is None:
        raise HTTPException(status_code=401,
                            detail="user not found",
                            headers={"WWW-Authenticate": "Bearer"})
    return db_user

@app.post("/items/", response_model=schemas.Item)
def create_item(item: schemas.ItemCreate, db: Session = Depends(get_db),
                current_user: models.User = Depends(get_current_user)):
    db_item = models.Item(**item.model_dump())
    db_item.user_id = current_user.id
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.delete("/items/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_db),
                current_user: models.User = Depends(get_current_user)):
    db_item = db.query(models.Item).filter(models.Item.id==item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404,detail="Item not found")
    if current_user.id != db_item.user_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="unauthorized to delete")
    db.delete(db_item)
    db.commit()
    return {"message": f"Item id {item_id} has been deleted"}

@app.get("/items/{item_id}", response_model=schemas.Item)
def read_item(item_id: int, db : Session = Depends(get_db),
              current_user: models.User = Depends(get_current_user)):
    db_item = db.query(models.Item).filter(models.Item.id == item_id, current_user.id == models.Item.user_id).first()
    if db_item is None:
        raise HTTPException(status_code=404,detail="Item not found")
    return db_item

@app.get("/items/", response_model=list[schemas.Item])
def get_all_items(skip:int = 0, limit:int = 100, db: Session = Depends(get_db),
                  current_user: models.User = Depends(get_current_user)):
    items = db.query(models.Item).filter(current_user.id == models.Item.user_id).offset(skip).limit(limit).all()
    return items

@app.put("/items/{item_id}", response_model=schemas.Item)
def update_item(item_id:int, item: schemas.ItemCreate, db : Session = Depends(get_db),
                current_user: models.User = Depends(get_current_user)):
    db_item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404,detail="Item not found")
    if current_user.id != db_item.user_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="unauthorized to update")
    for key, val in item.dict().items():
        setattr(db_item, key, val)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.post("/users/register", response_model=schemas.User)
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="username already registered")
    new_user = models.User(
        username = user.username,
        hashed_password = create_hash_password(user.password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.get("/users/", response_model=list[schemas.User])
def get_all_users(limit:int = 100, skip:int = 0, db : Session = Depends(get_db)):
    users = db.query(models.User).offset(skip).limit(limit).all()
    return users

@app.post("/users/login", response_model=schemas.Token)
def login(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    db_user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if db_user is None:
        raise HTTPException(status_code=401, detail="User not found")
    user_is_verified = verify_password(form_data.password, db_user.hashed_password)
    if not user_is_verified:
        raise HTTPException(status_code=401, detail="User login failed")
    tkn = create_jwt_token({"sub": db_user.username, "role": db_user.role})
    return {"access_token": tkn, "token_type": "bearer"}
