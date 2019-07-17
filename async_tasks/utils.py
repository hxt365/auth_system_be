from django_celery_beat.models import (
    CrontabSchedule,
    PeriodicTask
)
import datetime
import json


def create_task_resend(FROM, TO, msg):
    schedule, created = CrontabSchedule.objects.get_or_create(
        hour='0',
        timezone='Asia/Ho_Chi_Minh',
    )
    name = 'Resend email to {0} {1}'.format(TO, datetime.datetime.now())
    args = json.dumps([FROM, TO, msg])
    PeriodicTask.objects.create(
        crontab=schedule,
        name=name,
        task='async_tasks.tasks.async_send_mail',
        args=args,
        one_off=True,
    )