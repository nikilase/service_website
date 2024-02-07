from fastapi import Request, APIRouter
from fastapi.responses import HTMLResponse, FileResponse

from app.dependencies import templates

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/favicon.ico")
async def favicon():
    return FileResponse("static/favicon/favicon.ico")
