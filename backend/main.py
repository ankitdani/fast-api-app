import models, schemas
from database import engine, SessionLocal
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from fastapi import HTTPException

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

@app.post("/items/", response_model=schemas.Item)
def create_item(item: schemas.ItemCreate, db: Session = Depends(get_db)):
    db_item = models.Item(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.delete("/items/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_db)):
    db_item = db.query(models.Item).filter(models.Item.id==item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404,detail="Item not found")
    db.delete(db_item)
    db.commit()
    return {"message": f"Item id {item_id} has been deleted"}

@app.get("/items/{item_id}", response_model=schemas.Item)
def read_item(item_id: int, db : Session = Depends(get_db)):
    db_item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404,detail="Item not found")
    return db_item

@app.get("/items/", response_model=list[schemas.Item])
def get_all_items(skip:int = 0, limit:int = 100, db: Session = Depends(get_db)):
    items = db.query(models.Item).offset(skip).limit(limit).all()
    return items

@app.put("/items/{item_id}", response_model=schemas.Item)
def update_item(item_id:int, item: schemas.ItemCreate, db : Session = Depends(get_db)):
    db_item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404,detail="Item not found")
    for key, val in item.dict().items():
        setattr(db_item, key, val)
    db.commit()
    db.refresh(db_item)
    return db_item