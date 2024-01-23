from fastapi import Request, APIRouter
from fastapi.responses import HTMLResponse

from app.dependencies import templates

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
