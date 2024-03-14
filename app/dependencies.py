import tomllib

from fastapi.templating import Jinja2Templates

from app.schema.services import Service

templates = Jinja2Templates(directory="templates")

try:
    with open("app/conf/config.toml", "rb") as f:
        config = tomllib.load(f)
except FileNotFoundError:
    print(
        "No custom config found!\nUsing template config!\nPlease configure your config in app/conf/config.toml"
    )
    with open("app/conf/config_template.toml", "rb") as f:
        config = tomllib.load(f)

server_config = config["server_config"]
other_config = config["other_config"]
admin_config = config["admin_user"]
services = config["services"]

services_list = []
for service in services:
    url = service["link"] if service["link"] != "" else None
    try:
        append_lines = service["append_line"]
    except KeyError:
        append_lines = False
    services_list.append(
        Service.new_service(
            service["name"],
            service["service"],
            service["allow_functions"],
            url,
            append_lines,
        )
    )
