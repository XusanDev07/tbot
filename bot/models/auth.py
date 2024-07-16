from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
import uuid


class CustomUserManager(BaseUserManager):
    def create_user(self, tg_user_id, username, phone_number, password=None, **extra_fields):
        if not tg_user_id:
            raise ValueError('The Telegram user ID must be set')
        user = self.model(tg_user_id=tg_user_id, username=username, phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, tg_user_id, username, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(tg_user_id, username, phone_number, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    tg_user_id = models.IntegerField(unique=True)
    username = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'tg_user_id'
    REQUIRED_FIELDS = ['username', 'phone_number']

    def __str__(self):
        return f"{self.username} | {self.phone_number}"
