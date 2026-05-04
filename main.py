from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, Float, DateTime # Correction ici
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import datetime

# 1. Configuration de la base de données SQLite
# SQLALCHEMY_DATABASE_URL = "sqlite:///./budget.db" #dev
SQLALCHEMY_DATABASE_URL = "sqlite:////home/elkhalefmed/budget_manager/budget.db" #prod
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 2. Modèle de la table dans la base de données
class Expense(Base):
    __tablename__ = "expenses"
    id = Column(Integer, primary_key=True, index=True)
    label = Column(String)
    amount = Column(Float)
    latitude = Column(Float)
    longitude = Column(Float)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

# Créer la table si elle n'existe pas
Base.metadata.create_all(bind=engine)

# 3. Schéma de données pour la validation (Pydantic)
# Note: Ces noms de champs doivent être EXACTEMENT les mêmes que vos "Keys" dans iOS Shortcuts
class ExpenseCreate(BaseModel):
    label: str
    amount: float
    latitude: float
    longitude: float

# 4. Initialisation de l'application FastAPI
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)