from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.auth import auth_router
from app.routes.job import job_router
from app.models.user import create_db
from app.routes.application import app_router
from app.routes.subscription import subscription_router
from app.config.dbconnection import engine
from app.core.security import verify_token
from fastapi import Depends

app = FastAPI()

origins = ["*"]

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
app.include_router(job_router, dependencies=[Depends(verify_token)])
app.include_router(app_router, dependencies=[Depends(verify_token)])
app.include_router(subscription_router, dependencies=[Depends(verify_token)])
@app.get("/")
def index():
    return {"msg": "Welcome to Recruitment AI Portal"}