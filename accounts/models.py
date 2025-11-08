from django.db import models

from django.conf import settings

class Porfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    # add additional fields in here
    date_of_birth = models.DateField(null=True, blank=True)
    photo=models.ImageField(upload_to='users/%Y/%m/%d/', blank=True)
    def __str__(self):
        return f'Profile for user {self.user.username}'
###PATH:accounts/views.py
