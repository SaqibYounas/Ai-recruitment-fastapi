from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.auth import auth_router
from app.routes.job import job_router
from app.models.user import create_db
from app.routes.application import app_router
from app.middleware.auth_handle import auth_middleware
from app.config.dbconnection import engine

app = FastAPI()

origins = ["*"]
app.middleware("http")(auth_middleware)
@app.on_event("startup")
def on_startup():
     create_db(engine)

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