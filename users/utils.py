import random
import threading

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
def generate_otp():
    return str(random.randint(100000, 999999))
def _send_email_thread(subject, html_content, text_content, from_email, recipient_list):
    msg = EmailMultiAlternatives(subject, text_content, from_email, recipient_list)
    msg.attach_alternative(html_content, "text/html")
    try:
        msg.send()
        print(f"Email sent successfully to {recipient_list}")
    except Exception as e:
        print(f"Failed to send email: {e}")
def send_otp_email(email, otp):
    subject = 'Reset Your Password - Academic Factor'
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [email]

    # Load the HTML template and pass the OTP context
    html_content = render_to_string('emails/otp_email.html', {'otp': otp})
    
    # Create a plain text version for email clients that block HTML
    text_content = strip_tags(html_content)

    # Use Threading to send email without freezing the website
    email_thread = threading.Thread(
        target=_send_email_thread,
        args=(subject, html_content, text_content, from_email, recipient_list)
    )
    email_thread.start()

def send_sms_otp(phone_number, otp):
    """
    Simulates sending an SMS.
    In production, replace the print statement with a request to an SMS API.
    """
    # --- SIMULATION ---
    print(f"----------------------------------------")
    print(f"Sending SMS to {phone_number}")
    print(f"OTP CODE: {otp}")
    print(f"----------------------------------------")
    
    # --- REAL WORLD EXAMPLE (ThaiBulkSMS) ---
    # import requests
    # url = "https://api-v2.thaibulksms.com/sms"
    # payload = {
    #     "msisdn": phone_number,
    #     "message": f"Your OTP is {otp}",
    #     "sender": "TeacherPeem",
    #     # Add your API Key/Secret here
    # }
    # requests.post(url, data=payload)