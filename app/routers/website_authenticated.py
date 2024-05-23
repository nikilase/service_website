import asyncio
import time

from fastapi import APIRouter, Request

from app.controller.overview import get_status
from app.dependencies import services_list, templates
from app.schema.services import Service

router = APIRouter()


@router.get("/log_overview")
async def root(request: Request):
    html_services_data: list[object] = []
    t0 = time.time()
    # ToDo: make the get_status call async and do all of them at once using asyncio
    coros = [get_status(service.service_name) for service in services_list]
    results = await asyncio.gather(*coros)
    print(f"Await Time {time.time() - t0}")
    for service_index, service in enumerate(services_list):
        t1 = time.time()
        status = results[service_index]

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
                    service.status = status[0]
                    service.status_class = "service_inactive"
                case "enabled":
                    service.status = status[0]
                    service.status_class = "service_enabled"
                case "disabled":
                    service.status = status[0]
                    service.status_class = "service_disabled"
                case _:
                    service.status = status[0]
                    service.status_class = "service_disabled"
            service.enabled = status[2]

        html_services_data.append(service.dict())
        print(f"t1 {time.time() - t1}")
    print(f"t0 {time.time() - t0}")

    return templates.TemplateResponse(
        "root.html", {"request": request, "services": html_services_data}
    )


@router.get("/live_log/{service}")
def print_last_log(request: Request, service: str):
    if Service.is_in_list(services_list, service):
        return templates.TemplateResponse(
            "log_ws.html", {"request": request, "service": service}
        )
