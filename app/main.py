from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import RedirectResponse


from app.models.users.users import active_users, get_user_from_token_websocket
from app.models.users.sqlite import create_db_and_tables
from app.routers import api, auth, website_authenticated, website_unauthenticated, websocket

try:
    from app.conf.config import services_list
except ModuleNotFoundError:
    print("No custom config found!\nUsing template config!\nPlease configure your config in app/conf/config.py")
    from app.conf.config_template import services_list


app = FastAPI()

# ToDo: Add more granular control to allow_functions using AllowFunction Enum

# ToDo: Add link to service (if service is webservice e.g. nodered/website)

# ToDo: Maybe add install script for systemd? https://gist.github.com/ahmedsadman/2c1f118a02190c868b33c9c71835d706

# ToDo: Add button to enable/disable service (automatic start of service) and show the enable status of the service


@app.on_event("startup")
async def startup_event():
    await create_db_and_tables()


@app.exception_handler(HTTPException)
async def require_login(request: Request, e: HTTPException):
    if e.status_code == 401 and e.detail not in ("Unauthorized Websocket Access!",):
        print("Exception Handler Redirect")
        return RedirectResponse("/login", 303)
    else:
        print(f"Got Exception {e}")
        return e


app.include_router(website_unauthenticated.router)

app.include_router(auth.router,
                   tags=["auth"]
                   )

app.include_router(website_authenticated.router,
                   dependencies=[Depends(active_users)]
                   )

app.include_router(api.router,
                   prefix="/api",
                   tags=["api"],
                   dependencies=[Depends(active_users)]
                   )

app.include_router(websocket.router,
                   prefix="/ws",
                   tags=["websocket"],
                   dependencies=[Depends(get_user_from_token_websocket)]
                   )
