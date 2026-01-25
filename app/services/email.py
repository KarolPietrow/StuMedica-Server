import os
from datetime import datetime
from typing import List
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import EmailStr, SecretStr
from dotenv import load_dotenv

load_dotenv()

conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=SecretStr(os.getenv("MAIL_PASSWORD")),
    MAIL_FROM=os.getenv("MAIL_FROM", "noreply@stumedica.pl"),
    MAIL_PORT=int(os.getenv("MAIL_PORT")),
    MAIL_SERVER=os.getenv("MAIL_SERVER"),
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

async def send_email(subject: str, recipients: List[EmailStr], body: str):
    message = MessageSchema(
        subject=subject,
        recipients=recipients,
        body=body,
        subtype=MessageType.html
    )

    fm = FastMail(conf)
    await fm.send_message(message)

async def send_test_email(to_email: EmailStr):
    primary_color = "#76e7a1"
    bg_color = "#f4f7f6"

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: {bg_color}; margin: 0; padding: 0; }}
            .container {{ max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 10px rgba(0,0,0,0.05); margin-top: 20px; margin-bottom: 20px; }}
            .header {{ background-color: {primary_color}; padding: 30px 20px; text-align: center; }}
            .header h1 {{ color: #ffffff; margin: 0; font-size: 24px; font-weight: 600; letter-spacing: 1px; }}
            .content {{ padding: 30px; color: #333333; }}
            .greeting {{ font-size: 18px; margin-bottom: 20px; }}
            .card {{ background-color: #f8f9fa; border-left: 5px solid {primary_color}; padding: 20px; border-radius: 4px; margin: 20px 0; }}
            .card-row {{ margin-bottom: 10px; display: flex; align-items: center; }}
            .card-row:last-child {{ margin-bottom: 0; }}
            .label {{ font-weight: 600; color: #666; width: 100px; display: inline-block; }}
            .value {{ font-weight: 500; color: #333; }}
            .footer {{ background-color: #eeeeee; padding: 20px; text-align: center; font-size: 12px; color: #888; }}
            .btn {{ display: inline-block; background-color: {primary_color}; color: #ffffff; padding: 12px 24px; text-decoration: none; border-radius: 50px; font-weight: bold; margin-top: 20px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>StuMedica</h1>
            </div>
            <div class="content">
                <p class="greeting">Cześć <strong>Imię</strong>,</p>
                <p>Twoja wizyta została pomyślnie potwierdzona!</p>
                <p>Oto szczegóły Twojej rezerwacji:</p>

                <div class="card">
                    <div class="card-row">
                        <span class="label">Lekarz:</span>
                    </div>
                    <div class="card-row">
                        <span class="label">Specjalizacja:</span>
                    </div>
                    <div class="card-row">
                        <span class="label">Data:</span>
                    </div>
                    <div class="card-row">
                        <span class="label">Godzina:</span>
                    </div>
                    <div class="card-row">
                        <span class="label">Miejsce:</span>
                    </div>
                </div>

                <p>Prosimy o przybycie 10 minut przed planowaną godziną wizyty.</p>

                <div style="text-align: center;">
                    <a href="#" class="btn" style="color: #ffffff;">Zobacz w aplikacji</a>
                </div>
            </div>
            <div class="footer">
                <p>&copy; 2026 StuMedica. Wszystkie prawa zastrzeżone.</p>
                <p>Ta wiadomość została wygenerowana automatycznie. Prosimy na nią nie odpowiadać.</p>
            </div>
        </div>
    </body>
    </html>
    """
    await send_email("Test konfiguracji e-mail", [to_email], html_content)


async def send_email_core(subject: str, recipients: List[EmailStr], body: str):
    message = MessageSchema(
        subject=subject,
        recipients=recipients,
        body=body,
        subtype=MessageType.html
    )
    fm = FastMail(conf)
    await fm.send_message(message)


def get_confirmation_template(patient_name: str, doctor_name: str, specialization: str, date_str: str, time_str: str,
                              location: str = "Gabinet 24 (II Piętro)"):
    primary_color = "#76e7a1"
    bg_color = "#f4f7f6"

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: {bg_color}; margin: 0; padding: 0; }}
            .container {{ max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 10px rgba(0,0,0,0.05); margin-top: 20px; margin-bottom: 20px; }}
            .header {{ background-color: {primary_color}; padding: 30px 20px; text-align: center; }}
            .header h1 {{ color: #ffffff; margin: 0; font-size: 24px; font-weight: 600; letter-spacing: 1px; }}
            .content {{ padding: 30px; color: #333333; }}
            .greeting {{ font-size: 18px; margin-bottom: 20px; }}
            .card {{ background-color: #f8f9fa; border-left: 5px solid {primary_color}; padding: 20px; border-radius: 4px; margin: 20px 0; }}
            .card-row {{ margin-bottom: 10px; display: flex; align-items: center; }}
            .card-row:last-child {{ margin-bottom: 0; }}
            .label {{ font-weight: 600; color: #666; width: 100px; display: inline-block; }}
            .value {{ font-weight: 500; color: #333; }}
            .footer {{ background-color: #eeeeee; padding: 20px; text-align: center; font-size: 12px; color: #888; }}
            .btn {{ display: inline-block; background-color: {primary_color}; color: #ffffff; padding: 12px 24px; text-decoration: none; border-radius: 50px; font-weight: bold; margin-top: 20px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>StuMedica</h1>
            </div>
            <div class="content">
                <p class="greeting">Cześć <strong>{patient_name}</strong>,</p>
                <p>Twoja wizyta została pomyślnie potwierdzona!</p>
                <p>Oto szczegóły Twojej rezerwacji:</p>

                <div class="card">
                    <div class="card-row">
                        <span class="label">Lekarz:</span>
                        <span class="value">{doctor_name}</span>
                    </div>
                    <div class="card-row">
                        <span class="label">Specjalizacja:</span>
                        <span class="value">{specialization}</span>
                    </div>
                    <div class="card-row">
                        <span class="label">Data:</span>
                        <span class="value">{date_str}</span>
                    </div>
                    <div class="card-row">
                        <span class="label">Godzina:</span>
                        <span class="value">{time_str}</span>
                    </div>
                    <div class="card-row">
                        <span class="label">Miejsce:</span>
                        <span class="value">{location}</span>
                    </div>
                </div>

                <p>Prosimy o przybycie 10 minut przed planowaną godziną wizyty.</p>

                <div style="text-align: center;">
                    <a href="#" class="btn" style="color: #ffffff;">Zobacz w aplikacji</a>
                </div>
            </div>
            <div class="footer">
                <p>&copy; 2026 StuMedica. Wszystkie prawa zastrzeżone.</p>
                <p>Ta wiadomość została wygenerowana automatycznie. Prosimy na nią nie odpowiadać.</p>
            </div>
        </div>
    </body>
    </html>
    """


async def send_appointment_confirmation(to_email: EmailStr, patient_name: str, doctor_name: str, specialization: str,
                                        date_time: datetime):
    try:
        date_str = date_time.strftime("%d.%m.%Y")
        time_str = date_time.strftime("%H:%M")

        html_content = get_confirmation_template(
            patient_name=patient_name,
            doctor_name=doctor_name,
            specialization=specialization,
            date_str=date_str,
            time_str=time_str
        )

        subject = f"Potwierdzenie wizyty: {date_str} - {doctor_name}"

        await send_email_core(subject, [to_email], html_content)
        print(f"E-mail z potwierdzeniem wysłany do {to_email}")

    except Exception as e:
        print(f"Błąd podczas wysyłania e-maila: {e}")
