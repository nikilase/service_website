import asyncio
import logging
import subprocess

from fastapi import FastAPI, Request, HTTPException, WebSocket, Response, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi_users import fastapi_users, BaseUserManager, models
from fastapi_users.authentication import Strategy
from fastapi_users.router import ErrorCode

from app.controller.logs import get_last_logs
from app.controller.overview import service_handler, get_status
from app.schema.services import Service
from app.models.users.users import auth_backend, active_users, fastapi_users, admin_users, get_user_manager, \
    get_jwt_strategy, optional_current_active_user
from app.schema.users import UserRead
from app.models.users.sqlite import User

try:
    from app.conf.config import services_list
except ModuleNotFoundError:
    print("No custom config found!\nUsing template config!\nPlease configure your config in app/conf/config.py")
    from app.conf.config_template import services_list


app = FastAPI()
templates = Jinja2Templates(directory="templates")

# ToDo: Refactor in better structured project

# ToDo: Implement Log with either a redirect/popup to a live version/last x lines of the log

# ToDo: Add more granular control to allow_functions using AllowFunction Enum

# ToDo: Add link to service (if service is webservice e.g. nodered/website)

# ToDo: Maybe add install script for systemd? https://gist.github.com/ahmedsadman/2c1f118a02190c868b33c9c71835d706

# ToDo: Add button to enable/disable service (automatic start of service) and show the enable status of the service


@app.get("/", response_class=HTMLResponse)
async def root(request: Request, user = Depends(optional_current_active_user)):
    # body is a 2D list of [Service Description, Service Name, Allow Functions,  Service Status, Service Status Class]
    #Service.print_service_list(services_list)

    if user is None:
        print(user)
        return RedirectResponse("/login")
    else:
        print(user.email)
        return "SUCCESS"
    html_services_data: list[object] = []
    for service in services_list:
        status = get_status(service.service_name)

        if status is None:
            service.status = "not found"
            service.status_class = "service_not_found"
        else:
            match status[0]:
                case "active":
                    match status[1]:
                        case "(running)":
                            service.status = "running"
                            service.status_class = "service_running"
                        case "(exited)":
                            service.status = "exited"
                            service.status_class = "service_exited"
                        case "(waiting)":
                            service.status = "waiting"
                            service.status_class = "service_running"
                case "inactive":
                    service.status = (status[0])
                    service.status_class = "service_disabled"
                case "enabled":
                    service.status = (status[0])
                    service.status_class = "service_running"
                case "disabled":
                    service.status = (status[0])
                    service.status_class = "service_disabled"
                case _:
                    service.status = (status[0])
                    service.status_class = "service_disabled"

        html_services_data.append(service.dict())

    return templates.TemplateResponse("root.html", {"request": request, "services": html_services_data})


@app.get("/api/service/{action}/{service}")
async def service_api(action: str, service: str):
    print(f"Just got a click from button {action} {service}")

    if Service.is_in_list(services_list, service):
        match action:
            case "start":
                service_handler(service, action)
            case "restart":
                service_handler(service, action)
            case "stop":
                service_handler(service, action)
            case _:
                raise HTTPException(status_code=400, detail="Wrong action provided")
    else:
        raise HTTPException(status_code=400, detail="Service not found")
    raise HTTPException(status_code=200, detail="Request executed")


@app.get("/api/last_log/{service}")
def print_last_log(request: Request, service: str):
    if Service.is_in_list(services_list, service):
        log = get_last_logs(service).decode("UTF-8")
        return templates.TemplateResponse("log.html", {"request": request, "output": log})


# ToDo: Add the service to the javascript part
@app.get("/api/live_log/{service}")
def print_last_log(request: Request, service: str):
    if Service.is_in_list(services_list, service):
        return templates.TemplateResponse("log_ws.html", {"request": request, "service": service})


@app.websocket("/api/live_log_ws/{service}")
async def websocket_endpoint(websocket: WebSocket, service: str):
    await websocket.accept()
    try:
        while True:
            await asyncio.sleep(1)
            logs = get_last_logs(service).decode("UTF-8")
            log_lines = []
            log_txt = ""
            for log in logs.split("\n"):
                if "ERROR" in log:
                    log_txt += f'<span class="text-red-400">{log}</span><br/>\n'
                elif "WARNING" in log:
                    log_txt += f'<span class="text-orange-300">{log}</span><br/>\n'
                elif "INFO" in log:
                    log_txt += f'<span class="text-blue-400">{log}</span><br/>\n'
                else:
                    log_txt += f"{log}<br/>\n"

            await websocket.send_text(log_txt)
        while False:
            process = subprocess.Popen(["journalctl", "-u", "servicewebsite.service", "-n 100", "-f"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            for line in iter(process.stdout.readline, b''):
                await websocket.send_text(line.decode('utf8'))
    except Exception as e:
        print(e)
    finally:
        await websocket.close()


@app.get("/login", tags=["auth"])
def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})



#app.include_router(fastapi_users.get_auth_router(auth_backend), prefix="", tags=["auth"])



@app.post("/login", name=f"auth:login",)
async def login(
    request: Request,
    credentials: OAuth2PasswordRequestForm = Depends(),
    user_manager: BaseUserManager[models.UP, models.ID] = Depends(get_user_manager),
    strategy: Strategy[models.UP, models.ID] = Depends(get_jwt_strategy),
):
    logging.getLogger('passlib').setLevel(logging.ERROR)
    errors = []
    user = await user_manager.authenticate(credentials)

    if user is None or not user.is_active:
        #raise HTTPException(
        #    status_code=status.HTTP_400_BAD_REQUEST,
        #    detail=ErrorCode.LOGIN_BAD_CREDENTIALS,
        #)
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

    resp = templates.TemplateResponse("login.html", {"request": request, "errors": ["SUCCESS!"]})
    resp.set_cookie(key="fastapiusersauth", value=auth_token, httponly=True, secure=True)
    resp = await auth_backend.login(strategy, user)
    await user_manager.on_after_login(user, request, resp)

    return resp