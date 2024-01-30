from fastapi import Request, HTTPException, APIRouter

from app.dependencies import services_list
from app.controller.logs import get_last_logs
from app.controller.overview import service_handler
from app.dependencies import templates
from app.schema.services import Service

router = APIRouter()


@router.get("/service/{action}/{service}")
async def service_api(action: str, service: str):
    print(f"Just got a click from button {action} {service}")

    if Service.is_in_list(services_list, service):
        match action:
            case "start" | "restart" | "stop" | "enable" | "disable":
                service_handler(service, action)
            case _:
                raise HTTPException(status_code=400, detail="Wrong action provided")
    else:
        raise HTTPException(status_code=400, detail="Service not found")
    raise HTTPException(status_code=200, detail="Request executed")


@router.get("/last_log/{service}")
def print_last_log(request: Request, service: str):
    if Service.is_in_list(services_list, service):
        log = get_last_logs(service).decode("UTF-8")
        return templates.TemplateResponse("log.html", {"request": request, "output": log})
