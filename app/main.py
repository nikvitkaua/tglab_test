from fastapi import FastAPI

app = FastAPI(title="Expedition Management Service")

@app.get("/")
def read_root():
    return {"status": "Service is running"}