# Overview
I designed an authentication and authorization server API using Django Rest Framework and OAuth2. 
To register, all users must provide their email for verification. I send each user a confirmation email, including a link leads to confirmation page. This process is performed by woker in background with Celery's help. All emails unsuccessfully sent will be resend by crontab implemented with Celery beat.
After a successful login, user receives Access token and Refresh token, but can not see them in browser, because both are set as HttpOnly cookie. This work prevents some potential attacks like XSS.
# Todo
docker-compose up --build
