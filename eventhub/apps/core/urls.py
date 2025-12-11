from django.urls import path

from . import views

# from django.contrib.auth import views as auth_views
# from .forms import PasswordResetValidator


urlpatterns = [
    path('', views.home, name="home"),
    path('contact/', views.contact, name="contact"),
    path('terms-and-conditions/', views.terms_and_conditions, name="terms_and_conditions"),

    # path('password-reset/',
    #     auth_views.PasswordResetView.as_view(
    #         subject_template_name='core/password-reset-email/password_reset_subject.txt',
    #         email_template_name='core/password-reset-email/password_reset_email.txt',
    #         template_name='core/password_reset.html'
    #     ),
    #     name='password_reset'),

    # path('password-reset/done/',
    #     auth_views.PasswordResetDoneView.as_view(
    #         template_name='core/password_reset_done.html'
    #     ),
    #     name='password_reset_done'),

    # path('reset/<uidb64>/<token>/',
    #     auth_views.PasswordResetConfirmView.as_view(
    #         form_class=PasswordResetValidator,
    #         template_name='core/password_reset_confirm.html'
    #     ),
    #     name='password_reset_confirm'),

    # path('reset/done/',
    #     auth_views.PasswordResetCompleteView.as_view(
    #         template_name='core/password_reset_complete.html'
    #     ),
    #     name='password_reset_complete'),
]
