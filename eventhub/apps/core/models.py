from django.db import models


class ContactInquiry(models.Model):
    """
    An inquiry created by user (existing or anonymous).

    Fields:
        full_name (CharField): User's full name.
        email (EmailField): User's email for communication.
        message (str): Description of the inquiry.
        date (DateTimeField): Date when the inquiry was created.
        status (CharField): Status of the inquiry (open or closed).
    """

    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    date = models.DateTimeField(auto_now_add=True, verbose_name="Date (UTC)")
    status = models.CharField(
        max_length=15,
        choices=[('open','Open'),('closed','Closed')],
        default='open'
    )

    def __str__(self):
        return f"Contact Inquiry by {self.email}"
