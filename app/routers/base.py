from fastapi import APIRouter, HTTPException
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

# @router.post("/send-test")
# async def send_test_email_endpoint(request: EmailRequest):
#     try:
#         await send_test_email(request.email)
#         return {"message": "E-mail testowy został wysłany"}
#     except Exception as e:
#         print(f"Błąd wysyłania maila: {e}")
#         raise HTTPException(status_code=500, detail="Nie udało się wysłać wiadomości")