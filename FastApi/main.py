import logging
from fastapi import FastAPI, HTTPException, Depends
from typing import Annotated, List
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import SessionLocal, engine
import models
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(level=logging.INFO)

app = FastAPI()

origins = [
    'http://localhost:3000',
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
)


class TransactionBase(BaseModel):
    amount: float
    category: str
    description: str
    is_income: bool
    date: str


class TransactionModel(TransactionBase):
    id: int

    class Config:
        orm_mode = True


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependancy = Annotated[Session, Depends(get_db)]

models.Base.metadata.create_all(bind=engine)


@app.post("/transactions/", response_model=TransactionModel)
async def create_transaction(transaction: TransactionBase, db: db_dependancy):
    logging.info(f"Received transaction: {transaction}")
    db_transaction = models.Transaction(**transaction.dict())
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction


@app.get("/transactions/", response_model=List[TransactionModel])
async def read_transactions(db: db_dependancy, skip: int = 0, limit: int = 100):
    transaction = db.query(models.Transaction).offset(skip).limit(limit).all()
    return transaction


@app.get("/health/")
async def health():
    return "200"
