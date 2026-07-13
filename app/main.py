from fastapi import FastAPI
from app.core.database import engine, Base
from app.users.models import User
from app.expeditions.models import Expedition, ExpeditionMember
from app.users.router import router as auth_router
from app.expeditions.router import router as expeditions_router


Base.metadata.create_all(bind=engine)

app = FastAPI(title="Expedition Management Service")

app.include_router(auth_router)
app.include_router(expeditions_router)

@app.get("/")
def read_root():
    return {"status": "Cool"}