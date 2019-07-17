from celery.task import task
from celery.signals import task_failure, task_retry
from django.conf import settings
from .utils import create_task_resend
import smtplib


@task(bind=True, max_retries=2, default_retry_delay=10)
def async_send_mail(self, FROM, TO, message):
    try:
        server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
        server.ehlo()
        server.starttls()
        server.login(
            settings.EMAIL_HOST_USER,
            settings.EMAIL_HOST_PASSWORD,
        )
        server.sendmail(FROM, TO, message)
        server.close()
    except Exception as exc:
        # if self.request.retries == self.max_retries:
        #     raise exc
        raise self.retry(exc=exc, args=[FROM, TO, message])


@task_failure.connect(sender=async_send_mail)
def task_failure_handler(**kwargs):
    args = kwargs['args']
    create_task_resend(*args)