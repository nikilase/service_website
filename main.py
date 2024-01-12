import subprocess

from fastapi import FastAPI, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

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


def get_status(service: str):
    if not service_exists(service):
        return None
    command_return = ""
    try:
        command_return = (subprocess.check_output(["systemctl", "--type=service", "status", service])
                          .replace(b"\xe2\x97\x8f", b"").decode("utf-8").lower())
    except subprocess.CalledProcessError as e:
        if e.returncode == 3:
            # Process not running https://github.com/systemd/systemd/blob/v239/src/systemctl/systemctl.c#L80
            command_return = e.output.replace(b"\xe2\x97\x8f", b"").decode("utf-8").lower()
        else:
            return None
    finally:
        return_lines = command_return.split("\n")
        for line in return_lines:
            line = [elem.lstrip() for elem in line.split(":", maxsplit=1)]
            line_header = line[0]

            # Go through all lines of the status page until we have the active status
            if line_header == "active":
                line_values = line[1].split(" ")
                status = line_values[0]
                active_status = ""
                if status == "active":
                    active_status = line_values[1]
                return status, active_status


def service_exists(service: str):
    if not Service.is_in_list(services_list, service):
        #print(f"{service} not in list of services")
        return False

    try:
        command_return1 = subprocess.Popen(["systemctl", "--type=service", "status", service],
                                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        #print(e)
        return False
    else:
        try:
            subprocess.check_output(["grep", "Active"], stdin=command_return1.stdout)
        except subprocess.CalledProcessError as e:
            #print(e)
            return False
        else:
            return True


def service_handler(service_name, handle_type):
    if not service_exists(service_name):
        return

    try:
        match handle_type:
            case "start":
                subprocess.check_output(["sudo", "systemctl", "start", service_name])
            case "restart":
                subprocess.check_output(["sudo", "systemctl", "restart", service_name])
            case "stop":
                subprocess.check_output(["sudo", "systemctl", "stop", service_name])
            case _:
                print(f"Incorrect Command {handle_type}")
    except subprocess.CalledProcessError as e:
        print(f"Cannot {handle_type} {service_name}: {e}")
    return
