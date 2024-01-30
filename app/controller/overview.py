import subprocess

from app.schema.services import Service
from app.dependencies import services_list


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
            case "enable":
                subprocess.check_output(["sudo", "systemctl", "enable", service_name])
            case "disable":
                subprocess.check_output(["sudo", "systemctl", "disable", service_name])
            case _:
                print(f"Incorrect Command {handle_type}")
    except subprocess.CalledProcessError as e:
        print(f"Cannot {handle_type} {service_name}: {e}")
    return