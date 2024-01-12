from enum import Enum
from typing import Optional

from pydantic import BaseModel


class AllowFunction(Enum):
    NONE = 0
    START = 1
    RESTART = 2     # Also allows start
    ALL = 3


class Service(BaseModel):
    description: str
    service_name: str
    allow_functions: bool
    status: Optional[str] = None
    status_class: Optional[str] = None

    @classmethod
    def new_service(cls, description: str, service_name: str, allow_functions: bool):
        return Service(description=description, service_name=service_name, allow_functions=allow_functions)

    @classmethod
    def print_service_list(cls, services: list['Service']) -> None:
        for service in services:
            print(service)

    @classmethod
    def is_in_list(cls, services: list['Service'], service_name: str) -> bool:
        for service in services:
            if service.service_name == service_name:
                return True
        return False
