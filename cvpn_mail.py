import smtplib, ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import credentials

rcv_email = credentials.rcv_email


def send_mail(sender_email, password, subject, body):
    receiver_email = rcv_email

    # Create a multipart message and set headers
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message["Bcc"] = receiver_email  # Recommended for mass emails

    # Add body to email
    message.attach(MIMEText(body, "plain"))
    text = message.as_string()
    # Log in to server using secure context and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, text)


# if __name__ == "__main__":
#     # pruebacrg2020@gmail.com CRG3mpow3rs
#     send_mail('crgalert2020@gmail.com', 'CRG3mpow3rs', 'Prueba', 'Prueba')
