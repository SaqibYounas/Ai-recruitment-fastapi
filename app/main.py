from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.auth import auth_router
from app.routes.job import job_router
from app.models.auth import create_db
from app.routes.application import app_router
app = FastAPI()

origins = ["*"]

@app.on_event("startup")
def on_startup():
     create_db()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
) 

app.include_router(auth_router)
app.include_router(job_router)  
app.include_router(app_router)

@app.get("/")
def index():
    return {"msg": "Welcome to Recruitment AI Portal"}