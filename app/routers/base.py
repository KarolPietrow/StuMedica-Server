from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["General"])

@router.get("/", response_class=HTMLResponse)
async def main_site_html():
    return """
    <!DOCTYPE html>
    <html lang="pl">
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>StuMedica API</title>
        <link rel="icon" href="/static/favicon.png" type="image/png">
    </head>
    <body>
        <h1>Witamy w StuMedica API! 💖</h1>
        <h2><a href="https://api.stumedica.pl/docs">Dokumentacja</a></h2>
        <h2><a href="https://stumedica.pl">Przejdź do aplikacji</a></h2>
    </body>
    </html>
    """


@router.get("/hello")
async def get_test_value():
    return {"success": True, "message": "Welcome to the StuMedica API!"}
