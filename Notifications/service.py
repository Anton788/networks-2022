from django.core.mail import send_mail


def send(user_email, subject="", text=""):
    pass
    # send_mail(
    #     subject,
    #     text,
    #     "supplydirector.org@gmail.com",
    #     [user_email],
    #     fail_silently=False,
    #     )
