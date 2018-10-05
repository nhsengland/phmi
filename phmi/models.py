from datetime import timedelta

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
    _user_has_module_perms,
    _user_has_perm,
)
from django.core.signing import TimestampSigner
from django.db import models
from django.utils import timezone
from incuna_mail import send


class CareSystem(models.Model):
    type = models.ForeignKey(
        "GroupType", on_delete=models.CASCADE, related_name="care_systems"
    )

    name = models.TextField()

    class Meta:
        unique_together = ("type", "name")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        from django.urls import reverse

        return reverse("group-detail", args=[str(self.id)])


class GroupType(models.Model):
    name = models.TextField(unique=True)

    def __str__(self):
        return self.name


class OrgType(models.Model):
    name = models.TextField(unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Organisation(models.Model):
    care_system = models.ManyToManyField("CareSystem", related_name="orgs")
    type = models.ForeignKey("OrgType", on_delete=models.CASCADE, related_name="orgs")

    name = models.TextField()
    ods_code = models.TextField(unique=True, null=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class UserManager(BaseUserManager):
    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    care_system = models.ForeignKey(
        "CareSystem", null=True, on_delete=models.SET_NULL, related_name="users"
    )

    email = models.TextField(null=False, unique=True)
    password = models.TextField(null=True, blank=True)

    is_staff = models.BooleanField(
        "staff status",
        default=False,
        help_text="Designates whether the user can log into this admin site.",
    )
    is_active = models.BooleanField(
        "active",
        default=True,
        help_text=(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )
    date_joined = models.DateTimeField("date joined", default=timezone.now)

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"

    objects = UserManager()

    LOGIN_SALT = "login"

    def email_login_url(self, url):
        """Email the given URL to the User."""
        send(
            to=self.email,
            subject="Log into PHMI",
            template_name="emails/login.txt",
            context={"login_url": url},
        )

    @classmethod
    def get_pk_from_signed_url(cls, signed_pk):
        signer = TimestampSigner(salt=cls.LOGIN_SALT)
        return signer.unsign(signed_pk, max_age=timedelta(hours=2))

    def has_perm(self, perm, obj=None):
        return _user_has_perm(self, perm, obj=obj)

    def has_module_perms(self, module):
        return _user_has_module_perms(self, module)

    def sign_pk(self):
        """
        Signs the User's PK.

        Uses TimestampSigner so we can check the age of the signed data when
        unsigning.
        """
        return TimestampSigner(salt=self.LOGIN_SALT).sign(self.pk)
