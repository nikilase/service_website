import asyncio
import subprocess

from app.schema.services import Service
from app.dependencies import services_list


async def get_status(service: str):
    if not await service_exists(service):
        return None
    command_return = ""

    try:
        proc = await asyncio.create_subprocess_exec("systemctl", "--type=service", "status", service,
                                                    stdout=asyncio.subprocess.PIPE,
                                                    stderr=asyncio.subprocess.PIPE)
        stdout, stderr = await proc.communicate()
        if stderr:
            print(stderr)
            return None

        command_return = stdout.replace(b"\xe2\x97\x8f", b"").decode("utf-8").lower()

    finally:
        status = None
        active_status = None
        enabled = None

        return_lines = command_return.split("\n")
        for line in return_lines:
            line = [elem.lstrip() for elem in line.split(":", maxsplit=1)]
            line_header = line[0]

            if line_header == "loaded":
                line_values = line[1].split(" ")
                enabled = line_values[2].replace(";", "")

            # Go through all lines of the status page until we have the active status
            if line_header == "active":
                line_values = line[1].split(" ")
                status = line_values[0]
                active_status = ""
                if status == "active":
                    active_status = line_values[1]
        return status, active_status, enabled


async def service_exists(service: str):
    if not Service.is_in_list(services_list, service):
        #print(f"{service} not in list of services")
        return False

    try:
        proc = await asyncio.create_subprocess_exec("systemctl", "--type=service", "status", service,
                                                    stdout=asyncio.subprocess.PIPE,
                                                    stderr=asyncio.subprocess.PIPE)
        stdout, stderr = await proc.communicate()
        if stderr:
            return False
        else:
            return True
    except subprocess.CalledProcessError as e:
        return False


async def service_handler(service_name, handle_type):
    if not await service_exists(service_name):
        return

    try:
        match handle_type:
            case "start" | "restart" | "stop" | "enable" | "disable":
                command = handle_type
            case _:
                print(f"Incorrect Command {handle_type}")
                return
        proc = await asyncio.create_subprocess_exec("sudo", "systemctl", command, service_name,
                                                    stdout=asyncio.subprocess.PIPE,
                                                    stderr=asyncio.subprocess.PIPE)
        _, stderr = await proc.communicate()
        if stderr:
            print(f"Cannot {handle_type} {service_name}: {stderr.decode('utf-8').strip()}")
    except subprocess.CalledProcessError as e:
        print(f"Cannot {handle_type} {service_name}: {e}")
    return
