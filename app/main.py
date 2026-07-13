from fastapi import FastAPI
from app.core.database import engine, Base
from app.users.router import router as auth_router


Base.metadata.create_all(bind=engine)

app = FastAPI(title="Expedition Management Service")

app.include_router(auth_router)

@app.get("/")
def read_root():
    return {"status": "Cool"}
