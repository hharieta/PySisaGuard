import smtplib
import os
from dotenv import load_dotenv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

if os.getenv('ENV') == 'DEV':
    load_dotenv()

def send_email() -> None:
    # Configuración del servidor de correo y credenciales
    smtp_server = "smtp.office365.com"
    port = 587  # Para SSL
    sender_email = "vanitas_23vanitatum@hotmail.com"
    receiver_email = "sofiadelanoval@hotmail.com"
    password = os.getenv('EMAIL_PASSWORD')

    # Creación del mensaje
    message = MIMEMultipart("alternative")
    message["Subject"] = "Sisa Guard - Alerta de ataque detectado"
    message["From"] = sender_email
    message["To"] = receiver_email

    # Cuerpo del correo en texto plano y HTML
    text = """\
    Hi,
    This is a test email sent from Python.
    """
    html = """\
    <html>
    <body>
        <p>Hi,<br>
        This is a test email sent from Python.
        </p>
    </body>
    </html>
    """

    # Adjuntar ambas versiones al mensaje
    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")
    message.attach(part1)
    message.attach(part2)

    # Enviar el correo
    try:
        server = smtplib.SMTP(smtp_server,port)
        server.ehlo()  # Puede ser necesario
        server.starttls()  # Activar seguridad
        server.ehlo()  # Puede ser necesario
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(e)
        print("Error sending email")
