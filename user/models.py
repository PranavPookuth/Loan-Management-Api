import random
from django.db import models
from datetime import timedelta
from random import randint
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.timezone import now



# Create your models here.
class UserManager(BaseUserManager):
    def create_user(self, username, email, otp=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')

        email = self.normalize_email(email)
        extra_fields.setdefault('is_active', True)  # Ensure user is active

        user = self.model(username=username, email=email, otp=otp, **extra_fields)
        user.set_password(extra_fields.get("password", None))  # Ensure password is set correctly
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, otp=None, **extra_fields):
        if otp is None:
            otp = str(random.randint(100000, 999999))  # Generate a random OTP

        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(username, email, otp, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=255, unique=True)
    mobile_number = models.IntegerField(unique=True,null=True,blank=True)
    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_generated_at = models.DateTimeField(null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = UserManager()

    def __str__(self):
        return self.username

    #
