from fastapi import Request
from fastapi.responses import JSONResponse
from sqlmodel import select 
import jwt
from app.core.settings import settings
from app.models.auth import User 
from app.db.session import SessionLocal 
async def auth_middleware(request: Request, call_next):
    public_paths = ["/auth/login", "/auth/signup", "/docs", "/openapi.json", "/jobs/all"]
    if request.url.path in public_paths:
        return await call_next(request)

    token = request.cookies.get("access_token")
    if not token:
        return JSONResponse(status_code=401, content={"detail": "Unauthorized: No token found"})

    try:
        token = token.replace("Bearer ", "")
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email = payload.get("sub")

        with SessionLocal() as session:
            statement = select(User).where(User.email == email)
            user = session.exec(statement).first()
            if not user:
                return JSONResponse(status_code=401, content={"detail": "User not found"})
            
            request.state.user_id = str(user.id) 

    except jwt.ExpiredSignatureError:
        return JSONResponse(status_code=401, content={"detail": "Token has expired"})
    except Exception:
        return JSONResponse(status_code=401, content={"detail": "Invalid token"})

    return await call_next(request)