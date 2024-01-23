from django.core.mail import send_mail
from django.utils.html import format_html
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from twilio.rest import Client
from django.conf import settings

account_sid = settings.TWILIO_SID
auth_token = settings.TWILIO_AUTH_TOKEN
twilio_sender = settings.TWILIO_SENDER_PHONE

def send_confirmation_email(email , code):
    # activation_url = f'http://cec5-213-109-66-242.ngrok-free.app/api/account/activate/?u={code}'
    activation_url_1 = f'http://127.0.0.1.8000/api/account/activate/?u={code}'
    context = {'activation_url': activation_url_1}
    subject = 'Здраствуйте потвердите свое присудствие '
    html_message = render_to_string('activate.html',context)
    plain_message = strip_tags(html_message)
    
    
    send_mail(
        subject,
        plain_message,
        'JuJutsuKaisen@gmail.com',
        [email],
        html_message=html_message,
        fail_silently=False
    )
def send_activation_sms(phone_number, activation_code):
    message = f'Ваш код активации: {activation_code}'
    client = Client(account_sid,auth_token)
    client.messages.create(body=message,from_=twilio_sender,to=phone_number)


def send_confirmation_password(email,code):
    
    send_mail(
            'Подтвердите ваше изменение',
            f'Ваш код подтверждение: {code}',
            'Book_Store@gmail.com',
            [email],
            fail_silently=False,
        )