from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from datetime import datetime, timezone
import os

# 1. Configuration de la base de données
# Sur Render, on utilise DATABASE_URL. Sinon, on utilise SQLite en local.
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./budget.db")

# Correction pour SQLAlchemy si l'URL commence par postgres:// (fréquent sur Render/Heroku)
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Configuration de l'engine
if "postgresql" in DATABASE_URL:
    # Pour PostgreSQL
    engine = create_engine(DATABASE_URL)
else:
    # Pour SQLite (connect_args est nécessaire uniquement pour SQLite)
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 2. Modèle de la table
class Expense(Base):
    __tablename__ = "expenses"
    id = Column(Integer, primary_key=True, index=True)
    label = Column(String)
    amount = Column(Float)
    latitude = Column(Float)
    longitude = Column(Float)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))

# Créer les tables au démarrage
Base.metadata.create_all(bind=engine)

# 3. Schéma Pydantic
class ExpenseCreate(BaseModel):
    label: str
    amount: float
    latitude: float
    longitude: float

# 4. FastAPI App
app = FastAPI(title="Mon Budget API")

@app.post("/depense")
async def create_expense(expense: ExpenseCreate):
    db = SessionLocal()
    try:
        new_expense = Expense(
            label=expense.label,
            amount=expense.amount,
            latitude=expense.latitude,
            longitude=expense.longitude
        )
        db.add(new_expense)
        db.commit()
        db.refresh(new_expense)
        return {"status": "success", "id": new_expense.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@app.get("/depenses")
async def get_all_expenses():
    db = SessionLocal()
    expenses = db.query(Expense).all()
    db.close()
    return expenses