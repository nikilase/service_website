import asyncio
import logging

from fastapi import APIRouter, WebSocket

from app.controller.logs import get_last_logs

router = APIRouter()


@router.websocket("/live_log/{service}")
async def websocket_endpoint(websocket: WebSocket, service: str):
    await websocket.accept()
    log_size = 20
    log_level = logging.INFO
    log_level_include_others = True

    async def read_websocket(ws: WebSocket):
        nonlocal log_size, log_level, log_level_include_others
        # ws.iter_json() endlessly waits for messages
        async for message in ws.iter_json():
            match message["type"]:
                case "switch_log_size":
                    #print(f"Received switch_log_size {message['value']} {type(message['value'])}")
                    log_size = int(message["value"])
                case "switch_log_level":
                    #print(f"Received switch_log_level {message['value']} {type(message['value'])}")
                    log_level = int(message["value"])
                case "switch_log_level_inc":
                    #print(f"Received switch_log_level_inc {message['value']} {type(message['value'])}")
                    log_level_include_others = message["value"]

    task = asyncio.create_task(read_websocket(websocket))

    # ToDo: instead of throwing out wrong log level here, I need to add the log level into the get_last_logs function,
    #  to let journalctl do the sorting for me? Otherwise Number of entries won't work correctly
    try:
        while True:
            await asyncio.sleep(1)
            logs = await get_last_logs(service, log_size)
            log_txt = ""
            for log in logs.split("\n"):
                if "DEBUG" in log:
                    if log_level <= logging.DEBUG:
                        log_txt += f'<span style="color: #60A5FA">{log}</span><br/>\n'
                elif "INFO" in log:
                    if log_level <= logging.INFO:
                        log_txt += f'<span style="color: #22D3EE">{log}</span><br/>\n'
                elif "WARNING" in log:
                    if log_level <= logging.WARNING:
                        log_txt += f'<span style="color: #FACC15">{log}</span><br/>\n'
                elif "ERROR" in log:
                    if log_level <= logging.ERROR:
                        log_txt += f'<span style="color: #FB923C">{log}</span><br/>\n'
                elif "CRITICAL" in log:
                    if log_level <= logging.CRITICAL:
                        log_txt += f'<span style="color: #F87171">{log}</span><br/>\n'
                else:
                    if log_level_include_others:
                        if "systemd" in log:
                            log_txt += f'<span style="color: #4ADE80">{log}</span><br/>\n'
                        else:
                            log_txt += f"{log}<br/>\n"

            await websocket.send_text(log_txt)
    except Exception as e:
        print(f"Websocket Exception: {e}")
    finally:
        task.cancel()

