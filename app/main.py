from fastapi import FastAPI
from app.core.database import engine, Base


Base.metadata.create_all(bind=engine)

app = FastAPI(title="Expedition Management Service")

@app.get("/")
def read_root():
    return {"status": "Service is running with Modular Architecture!"}