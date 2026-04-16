from fastapi import Request
from fastapi.responses import JSONResponse
import jwt
from app.core.settings import settings

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
        
        request.state.user_email = payload.get("sub")
        
    except jwt.ExpiredSignatureError:
        return JSONResponse(status_code=401, content={"detail": "Token has expired"})
    except jwt.InvalidTokenError:
        return JSONResponse(status_code=401, content={"detail": "Invalid token"})

    response = await call_next(request)
    return response