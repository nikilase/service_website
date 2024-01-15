import subprocess


def get_last_logs(service_name):
    try:
        last_logs = subprocess.check_output(["journalctl", "-u", service_name, "-n 100"])
    except subprocess.CalledProcessError as e:
        print(f"Cannot get last log of {service_name}: {e}")
    else:
        print(last_logs)
        return last_logs
