from fastapi_mail import ConnectionConfig
from config import settings

conf = ConnectionConfig(
   MAIL_USERNAME=settings.email_sender.user,
   MAIL_PASSWORD=settings.email_sender.password,
   MAIL_PORT=settings.email_sender.port,
   MAIL_SERVER=settings.email_sender.host,

   MAIL_FROM=settings.email_sender.user,
   MAIL_FROM_NAME="Admin auth app (FastAPI)",
   MAIL_STARTTLS=True,
   MAIL_SSL_TLS=False,
   USE_CREDENTIALS=True,
   VALIDATE_CERTS=True
)
