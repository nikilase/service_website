import subprocess

from fastapi import FastAPI, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from app.controller.logs import get_last_logs
from app.controller.overview import service_handler, get_status
from app.schema.services import Service

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
async def root(request: Request):
    # body is a 2D list of [Service Description, Service Name, Allow Functions,  Service Status, Service Status Class]
    #Service.print_service_list(services_list)

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

