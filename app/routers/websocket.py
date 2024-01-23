import asyncio

from fastapi import APIRouter, WebSocket

from app.controller.logs import get_last_logs

router = APIRouter()


@router.websocket("/live_log/{service}")
async def websocket_endpoint(websocket: WebSocket, service: str):
    await websocket.accept()
    log_size = 20

    async def read_websocket(ws: WebSocket):
        nonlocal log_size
        # ws.iter_json() endlessly waits for messages
        async for message in ws.iter_json():
            if message["type"] == "switch_log_size":
                print("Received switch_log_size")
                if log_size == 20:
                    log_size = 40
                else:
                    log_size = 20

    task = asyncio.create_task(read_websocket(websocket))

    try:
        while True:
            await asyncio.sleep(1)
            logs = get_last_logs(service, log_size).decode("UTF-8")
            log_txt = ""
            for log in logs.split("\n"):
                if "ERROR" in log:
                    log_txt += f'<span class="text-red-400">{log}</span><br/>\n'
                elif "WARNING" in log:
                    log_txt += f'<span class="text-orange-300">{log}</span><br/>\n'
                elif "INFO" in log:
                    log_txt += f'<span class="text-blue-400">{log}</span><br/>\n'
                else:
                    log_txt += f"{log}<br/>\n"

            await websocket.send_text(log_txt)
    except Exception as e:
        print(f"Websocket Exception: {e}")
    finally:
        task.cancel()

