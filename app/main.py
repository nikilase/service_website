from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import RedirectResponse, Response
from fastapi.staticfiles import StaticFiles

from app.dependencies import server_config
from app.models.users.sqlite import create_db_and_tables
from app.models.users.users import active_users, get_user_from_token_websocket
from app.routers import (
    api,
    auth,
    website_authenticated,
    website_unauthenticated,
    websocket,
)

app = FastAPI()

app.add_middleware(TrustedHostMiddleware, allowed_hosts=server_config["allowed_hosts"])

# ToDo: Add more granular control to allow_functions using AllowFunction Enum

# ToDo: Add link to service (if service is webservice e.g. nodered/website) and more info e.g. ip/port etc.

# ToDo: Maybe add install script for systemd? https://gist.github.com/ahmedsadman/2c1f118a02190c868b33c9c71835d706

# ToDo: Add button to enable/disable service (automatic start of service) and show the enable status of the service

# ToDo: Refresh of data in log_overview, instead of refreshing page just execute a JS Script that updates the Elements


@app.on_event("startup")
async def startup_event():
    await create_db_and_tables()


@app.exception_handler(HTTPException)
async def require_login(request: Request, e: HTTPException):
    if e.status_code == 401 and e.detail not in ("Unauthorized Websocket Access!",):
        print("Exception Handler Redirect")
        return RedirectResponse("/login", 303)
    elif e.status_code == 200:
        return Response(status_code=200, headers=e.headers, content=e.detail)
    else:
        print(f"Got Exception {e}")
        return e


app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(website_unauthenticated.router)

app.include_router(auth.router, tags=["auth"])

app.include_router(website_authenticated.router, dependencies=[Depends(active_users)])

app.include_router(
    api.router, prefix="/api", tags=["api"], dependencies=[Depends(active_users)]
)

app.include_router(
    websocket.router,
    prefix="/ws",
    tags=["websocket"],
    dependencies=[Depends(get_user_from_token_websocket)],
)
