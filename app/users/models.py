from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    full_name = models.CharField(max_length=120, null=True, blank=False)
    email = models.EmailField(blank=True, unique=False)

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "username"
