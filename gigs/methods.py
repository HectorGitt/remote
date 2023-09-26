
import threading
from django.core.mail import EmailMessage
from django.urls import reverse
from django.utils.html import format_html
from django.utils.http import urlencode
from .models import Transaction
 
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

class methods():
    def __init__(self):
        pass
    def approve(self, obj):
        if obj.status == obj.PENDING:
            return format_html('<a class="btn btn-success" href="{}">Approve</a>&nbsp;',
                               reverse('approve_transaction', args=[obj.id]))
        if obj.status == obj.APPROVED:
            return format_html('<a class="btn btn-success disabled">{}</a>&nbsp;',
                               obj.status)
        else:
            return '-'
    def reject(self, obj):
        if obj.status == obj.PENDING:
            return format_html('<a class="btn btn-danger" href="{}">Reject</a>&nbsp;',
                reverse('reject_transaction', args=[obj.id]))
        if obj.status == obj.REJECTED:
            return format_html('<a class="btn btn-danger disabled">{}</a>&nbsp;',
                obj.status)
        else:
            return '-'