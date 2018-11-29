from collections import OrderedDict
from datetime import timedelta
from django.utils.text import slugify
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
    _user_has_module_perms,
    _user_has_perm,
)
from django.utils.functional import cached_property
from django.urls import reverse
from django.core.signing import TimestampSigner
from django.db import models
from django.utils import timezone
from incuna_mail import send


class JustificationCache(object):
    def is_care_system_justified(self):
        pass


class CareSystem(models.Model):
    type = models.ForeignKey(
        "GroupType", on_delete=models.CASCADE, related_name="care_systems"
    )

    name = models.TextField()

    class Meta:
        unique_together = ("type", "name")
        ordering = ["-type__name", "name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("group-detail", args=[str(self.id)])


class GroupType(models.Model):
    name = models.TextField(unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def get_display_name(self):
        if "(" and ")" in self.name:
            start = self.name.find("(") + 1
            end = self.name.find(")")
            return self.name[start:end]
        return self.name


class OrgType(models.Model):
    name = models.CharField(
        max_length=256, unique=True
    )
    slug = models.SlugField(unique=True, blank=True, null=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def get_activities(self):
        return Activity.objects.filter(
            legaljustification__in=self.legaljustification_set.all()
        )

    def save(self):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save()


class Activity(models.Model):
    class Meta:
        verbose_name_plural = "Activities"

    DUTY_OF_CONFIDENCE_CHOICES = (
        (
            "Implied consent/reasonable expectations",
            "Implied consent/reasonable expectations",
        ),
        (
            "Set aside as data will be de-identified for this purpose",
            "Set aside as data will be de-identified for this purpose",
        ),
    )

    name = models.TextField(unique=True)
    slug = models.SlugField(unique=True, blank=True, null=True)

    duty_of_confidence = models.CharField(
        max_length=256,
        default="",
        blank=True,
        choices=DUTY_OF_CONFIDENCE_CHOICES
    )

    def get_org_types(self):
        return OrgType.objects.filter(
            legaljustification__in=self.legaljustification_set.all()
        ).distinct()

    def __str__(self):
        return "{}: {}".format(
            self.__class__.__name__,
            self.name
        )

    def get_absolute_url(self):
        return reverse("activity-detail", kwargs=dict(slug=self.slug))

    class Meta:
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)[:50]
        return super().save(*args, **kwargs)


class LegalJustificationQuerySet(models.QuerySet):
    def by_org_type_and_activity(self, org_types, activities):
        by_org_type = OrderedDict()

        for org_type in org_types:
            by_org_type[org_type] = OrderedDict()
            for activity in activities:
                by_org_type[org_type][activity] = self.filter(
                    org_type_id=org_type.id
                ).filter(
                    activities=activity
                )

        return by_org_type

    def by_org_and_activity(self, organisations, activities):
        result = OrderedDict()
        org_types = OrgType.objects.filter(orgs__in=organisations).distinct()
        by_org_type_and_activity = self.by_org_type_and_activity(
            org_types, activities
        )

        for organisation in organisations:
            result[organisation] = by_org_type_and_activity[
                organisation.type
            ]
        return result


class LegalJustification(models.Model):
    name = models.TextField()
    org_type = models.ForeignKey(
        OrgType,
        blank=True,
        null=True,
        on_delete=models.CASCADE
    )
    statute = models.TextField(
        default=""
    )
    activities = models.ManyToManyField(Activity)

    objects = LegalJustificationQuerySet.as_manager()

    def __str__(self):
        return "{}: {}".format(
            self.__class__.__name__,
            self.name
        )

    class Meta:
        ordering = ["name"]
        unique_together = (("name", "org_type",),)


class Organisation(models.Model):
    care_system = models.ManyToManyField(
        "CareSystem", related_name="orgs", blank=True
    )
    type = models.ForeignKey("OrgType", on_delete=models.CASCADE, related_name="orgs")

    name = models.TextField()
    ods_code = models.TextField(unique=True, null=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("organisation-detail", args=[str(self.id)])


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
        "CareSystem",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="users"
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
