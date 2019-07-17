# Generated by Django 2.2.3 on 2019-07-17 03:16

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import users.models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20190716_1417'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='signuprequest',
            managers=[
                ('objects', users.models.SignupRequestManager()),
            ],
        ),
        migrations.CreateModel(
            name='Log',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(choices=[('login', 'LOGIN'), ('logout', 'LOGOUT'), ('refresh', 'REFRESH'), ('reset_pw', 'RESET PASSWORD'), ('change_pw', 'CHANGE PASSWORD')], max_length=9)),
                ('status', models.CharField(choices=[('success', 'Success'), ('fail', 'Fail')], max_length=7)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Log',
                'verbose_name_plural': 'Logs',
                'ordering': ('-timestamp',),
            },
        ),
    ]
