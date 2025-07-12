from django.core.mail import send_mail, EmailMessage
from django.conf import settings


def send_invite_link(email: str, link: str):
    subject = "You're Invited: Interview Assessment"
    body = f"Hello,\n\nYou've been invited to take an interview assessment.\n\nPlease use the following link to start:\n{link}\n\nBest regards,\nThe Interview Team"
    _send_email(subject, body, [email])


def _send_email(subject: str, body: str, email: list):
    try:
        send_mail(subject, body, settings.EMAIL_HOST_USER, email, fail_silently=False)
    except Exception as e:
        raise e