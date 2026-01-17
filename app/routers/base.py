from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["General"])


@router.get("/", response_class=HTMLResponse)
async def main_site_html():
    return """
    <!DOCTYPE html>
    <html lang="pl">
    <head><title>StuMedica API</title></head>
    <body>
        <h1>Witamy w StuMedica API! 💖</h1>
        <h2><a href="https://api.stumedica.pl/docs">Dokumentacja</a></h2>
    </body>
    </html>
    """


@router.get("/hello")
async def get_test_value():
    return {"success": True, "message": "Welcome to the StuMedica API!"}
