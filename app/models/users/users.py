from fastapi import Depends, Request, HTTPException
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin
from fastapi_users.authentication import AuthenticationBackend, CookieTransport, JWTStrategy
from fastapi_users.db import SQLAlchemyUserDatabase
from app.models.users.sqlite import get_user_db

#ToDo: get more info on proper Secrets
SECRET = "mysecret"


class UserManager(UUIDIDMixin, BaseUserManager):
	reset_password_token_secret = SECRET
	verify_password_token_secret = SECRET


class RequiresLogin(HTTPException):
	pass


async def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
	yield UserManager(user_db)

cookie_transport = CookieTransport(cookie_httponly=True, cookie_secure=True)


# Should make auto logout after an hour
def get_jwt_strategy():
	return JWTStrategy(secret=SECRET, lifetime_seconds=3600)

auth_backend = AuthenticationBackend(name="jwst", transport=cookie_transport, get_strategy=get_jwt_strategy)

fastapi_users = FastAPIUsers(get_user_manager, [auth_backend])

active_users = fastapi_users.current_user(active=True)
admin_users = fastapi_users.current_user(active=True, superuser=True)


async def current_user():
	user = fastapi_users.current_user(active=True, optional=True)
	if not user:
		return None

	return user


optional_current_active_user = fastapi_users.current_user(active=True, optional=True)