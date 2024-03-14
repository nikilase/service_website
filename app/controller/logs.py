import asyncio
import subprocess


async def get_last_logs(service_name: str, count: int = 20):
    try:
        proc = await asyncio.create_subprocess_exec(
            "journalctl",
            "-u",
            service_name,
            "-n",
            str(count),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        last_logs, stderr = await proc.communicate()
        if stderr:
            print(f"Cannot get last log of {service_name}: {stderr.decode('utf-8')}")
            return None
    except subprocess.CalledProcessError as e:
        print(f"Cannot get last log of {service_name}: {e}")
    else:
        return last_logs.decode("utf-8")
