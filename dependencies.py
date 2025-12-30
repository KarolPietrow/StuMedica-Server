from fastapi import Request, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from typing import Optional
from jose import JWTError, jwt
import auth
from database import UserDatabase

db = UserDatabase()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login", auto_error=False)

async def get_token(
    request: Request,
    token_header: Optional[str] = Depends(oauth2_scheme)
):
    if token_header:
        return token_header

    token_cookie = request.cookies.get("access_token")
    if token_cookie:
        return token_cookie

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Brak autoryzacji"
    )

async def get_current_user(token: str = Depends(get_token)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Nie można zweryfikować poświadczeń",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.get_user_by_email(email)
    if user is None:
        raise credentials_exception

    return user