
import threading
from django.core.mail import EmailMessage
 
class EmailThread(threading.Thread):
    def __init__(self, subject, html_content, recipient_list, sender):
        self.subject = subject
        self.recipient_list = recipient_list
        self.html_content = html_content
        self.sender = sender
        threading.Thread.__init__(self)

    def run(self):
        msg = EmailMessage(self.subject, self.html_content, self.sender, self.recipient_list)
        msg.content_subtype = 'html'
        msg.send()


def send_mail(subject, from_email,plain_message, recipient_list):
    EmailThread(subject, plain_message, recipient_list, from_email).start()

