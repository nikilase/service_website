import subprocess


def get_last_logs(service_name: str, count: int = 20):
    try:
        last_logs = subprocess.check_output(["journalctl", "-u", service_name, "-n", str(count)])
    except subprocess.CalledProcessError as e:
        print(f"Cannot get last log of {service_name}: {e}")
    else:
        return last_logs
