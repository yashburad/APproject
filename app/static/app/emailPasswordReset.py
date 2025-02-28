from flask import render_template
from app import app
from flask_mail import Message
from app import mail

def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    mail.send(msg)

def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email('[QuadCore.com] Reset Your Password',
               sender="systems.quadcore@gmail.com",
               recipients=[user.email],
               text_body=render_template('emailPasswordReset/reset_password.txt',
                                         user=user, token=token),
               html_body=render_template('emailPasswordReset/reset_password.html',
                                         user=user, token=token))
