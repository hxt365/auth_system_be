# Auth-Sytem

A highly secure authentication and authorization server written on Python.  
This is the back-end part of the project. Here is the [front-end part](https://github.com/hxt365/auth_system_fe).

## Overview and technologies
**Auth-system** provides APIs to deal with authentication and authorization, and was implemented with **Django Rest Framework**.   
Firstly, to register a new account, all users must provide their email for verification. 
The server then sends each user a confirmation email, which includes a link leading to a confirmation page.  
This process is performed by a woker in background with **Celery**'s management. 
Next, all emails that were unsuccessfully sent will be resent by a crontab setup by **Celery Beat**.   
Secondly, after successfully login, user receives an Access token and a Refresh token, that are **JSON Web Token**, but user can not see them in browser, because both are sent within **HttpOnly** cookie. 
This prevents some potential attacks like XSS.  
Finally, **Redis** also was used to support cache and Celery job queue. In addition, **Google Recaptcha** was also used to prevent spam requests.  

<div style="padding: 0 30%; display: flex; justify-content: space-between;">
  <span style="padding-right: 20px">
  <img src="https://www.django-rest-framework.org/img/logo.png" alt="Django Rest Framework" height="100"/>
  </span>
  <span style="padding-right: 20px">
  <img src="https://jwt.io/img/pic_logo.svg" alt="JSON Web Token" height="100"/>
  </span>
  <span style="padding-right: 20px">
  <img src="https://docs.celeryproject.org/en/stable/_static/celery_512.png" alt="Celery" height="100"/>
  </span>
  <span style="padding-right: 20px">
  <img src="https://res.cloudinary.com/practicaldev/image/fetch/s--gWwIv4vV--/c_limit%2Cf_auto%2Cfl_progressive%2Cq_auto%2Cw_880/https://thepracticaldev.s3.amazonaws.com/i/787xlgwc2hhq3ctzxcvs.png" alt="Redis" height="100"/>
  </span>
  <span style="padding-right: 20px">
  <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/a/ad/RecaptchaLogo.svg/1024px-RecaptchaLogo.svg.png" alt="Google Recaptcha" height="100"/>
  </span>
</div>
