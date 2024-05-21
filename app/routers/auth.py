import logging

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_users import BaseUserManager, models
from fastapi_users.authentication import Authenticator, Strategy
from fastapi_users.router import ErrorCode

from app.dependencies import server_config, templates
from app.models.users.sqlite import User
from app.models.users.users import (
    active_users,
    auth_backend,
    current_user,
    get_jwt_strategy,
    get_user_manager,
)

router = APIRouter()


@router.get("/login", tags=["auth"])
def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.post(
    "/login",
    name=f"auth:login",
)
async def login(
    request: Request,
    credentials: OAuth2PasswordRequestForm = Depends(),
    user_manager: BaseUserManager[models.UP, models.ID] = Depends(get_user_manager),
    strategy: Strategy[models.UP, models.ID] = Depends(get_jwt_strategy),
):

    logging.getLogger("passlib").setLevel(logging.ERROR)
    errors = []
    user = await user_manager.authenticate(credentials)

    if user is None or not user.is_active:
        errors.append("User does not exists or is not active")
        return templates.TemplateResponse(
            "login.html", {"request": request, "errors": errors}
        )

    requires_verification = False
    if requires_verification and not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorCode.LOGIN_USER_NOT_VERIFIED,
        )

    auth_token = await strategy.write_token(user)

    resp = RedirectResponse("/log_overview", status_code=status.HTTP_303_SEE_OTHER)
    resp.set_cookie(
        key="fastapiusersauth",
        value=auth_token,
        httponly=True,
        secure=server_config["secure_only"],
    )

    return resp


@router.post("/logout", name=f"auth:.logout")
async def logout(current_user: User = Depends(active_users)):
    auth = Authenticator([auth_backend], get_user_manager(current_user))
    user_token = auth.current_user_token(active=True)

    await auth_backend.logout(auth_backend.get_strategy(), current_user, user_token)

    x = RedirectResponse("/login", status_code=status.HTTP_303_SEE_OTHER)
    x.set_cookie(
        key="fastapiusersauth",
        value="",
        httponly=True,
        max_age=0,
        expires=0,
        secure=server_config["secure_only"],
    )
    return x
