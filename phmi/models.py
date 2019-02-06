from collections import OrderedDict
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
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from incuna_mail import send

DUTY_OF_CONFIDENCE_CHOICES = (
    (
        "Implied consent/reasonable expectations or pseudo/anon data where it doesn't apply",
        "Implied consent/reasonable expectations or pseudo/anon data where it doesn't apply",
    ),
    (
        "Implied consent/reasonable expectations",
        "Implied consent/reasonable expectations",
    ),
    (
        "Set aside as data will be de-identified for this purpose",
        "Set aside as data will be de-identified for this purpose",
    ),
)


class Activity(models.Model):
    activity_category = models.ForeignKey(
        "ActivityCategory",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="activities",
    )

    name = models.TextField(unique=True)
    slug = models.SlugField(unique=True, blank=True, null=True)
    duty_of_confidence = models.CharField(
        max_length=256, default="", blank=True, choices=DUTY_OF_CONFIDENCE_CHOICES
    )

    class Meta:
        verbose_name_plural = "Activities"
        ordering = ["activity_category__index", "name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("activity-detail", kwargs={"slug": self.slug})

    def get_org_types(self):
        return OrgType.objects.filter(
            legaljustification__in=self.legal_justifications.all()
        ).distinct()

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)[:50]
        return super().save(*args, **kwargs)


class ActivityCategory(models.Model):
    group = models.ForeignKey(
        "ActivityCategoryGroup",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="categories",
    )

    name = models.CharField(max_length=256, unique=True)
    index = models.IntegerField(default=0)

    slug = models.SlugField(unique=True, blank=True, null=True)

    class Meta:
        ordering = ["index"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        activity_list_url = reverse("activity-list")
        return f"{activity_list_url}#{self.slug}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)[:50]
        return super().save(*args, **kwargs)


class ActivityCategoryGroup(models.Model):
    name = models.TextField()
    description = models.TextField()
    index = models.IntegerField(default=0)

    class Meta:
        ordering = ["index"]

    def __str__(self):
        return self.name


class Benefit(models.Model):
    aim = models.ForeignKey("BenefitAim", on_delete=models.CASCADE)

    name = models.TextField(unique=True)
    index = models.TextField(default=0)

    def __str__(self):
        return self.name


class BenefitAim(models.Model):
    name = models.TextField()

    def __str__(self):
        return self.name


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


class DataCategory(models.Model):
    name = models.TextField()

    def __str__(self):
        return self.name


class DataType(models.Model):
    activities = models.ManyToManyField("Activity", related_name="data_types")
    category = models.ForeignKey("DataCategory", on_delete=models.CASCADE)
    org_types = models.ManyToManyField("OrgType", related_name="data_types")
    services = models.ManyToManyField("Service", related_name="data_types")

    name = models.TextField()
    example_data_sets = models.TextField()

    def __str__(self):
        return self.name


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


class LawfulBasis(models.Model):
    name = models.TextField()
    number = models.IntegerField(unique=True)

    def __str__(self):
        return self.name


class LegalJustificationQuerySet(models.QuerySet):
    def by_org_type_and_activity(self, org_types, activities):
        by_org_type = OrderedDict()

        for org_type in org_types:
            by_org_type[org_type] = OrderedDict()
            for activity in activities:
                by_org_type[org_type][activity] = self.filter(
                    org_type_id=org_type.id
                ).filter(activities=activity)

        return by_org_type

    def by_org_and_activity(self, organisations, activities):
        result = OrderedDict()
        org_types = OrgType.objects.filter(orgs__in=organisations).distinct()
        by_org_type_and_activity = self.by_org_type_and_activity(org_types, activities)

        for organisation in organisations:
            result[organisation] = by_org_type_and_activity[organisation.type]
        return result


class LegalJustification(models.Model):
    activities = models.ManyToManyField("Activity")
    statutes = models.ManyToManyField("Statute", blank=True)
    org_types = models.ManyToManyField("OrgType", blank=True)

    name = models.TextField(unique=True)
    details = models.TextField(default="")

    objects = LegalJustificationQuerySet.as_manager()

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.__class__.__name__}: {self.name}"


class Organisation(models.Model):
    care_system = models.ManyToManyField("CareSystem", related_name="orgs", blank=True)
    type = models.ForeignKey("OrgType", on_delete=models.CASCADE, related_name="orgs")

    name = models.TextField()
    ods_code = models.TextField(unique=True, null=True)

    class Meta:
        ordering = ["type__name", "name"]

    def __str__(self):
        return self.name


class OrgFunction(models.Model):
    type = models.ForeignKey(
        "OrgType", on_delete=models.CASCADE, related_name="functions"
    )

    name = models.TextField()
    index = models.IntegerField(default=0)

    class Meta:
        unique_together = ["name", "type"]

    def __str__(self):
        return self.name


class OrgResponsibility(models.Model):
    function = models.ForeignKey(
        "OrgFunction", on_delete=models.CASCADE, related_name="responsibilities"
    )
    lawful_bases = models.ManyToManyField("LawfulBasis")

    index = models.IntegerField(default=0)
    name = models.TextField()
    additional_information = models.TextField()
    related_reading = models.TextField()

    def __str__(self):
        return self.name


class OrgType(models.Model):
    name = models.CharField(max_length=256, unique=True)
    slug = models.SlugField(unique=True, blank=True, null=True)
    index = models.IntegerField(default=0)

    class Meta:
        ordering = ["index"]

    def __str__(self):
        return self.name

    def get_activities(self):
        return Activity.objects.filter(
            legal_justifications__in=self.legal_justifications.all()
        )

    def get_absolute_url(self):
        return reverse("org-type-detail", kwargs=dict(slug=self.slug))

    @property
    def short_name(self):
        short, _, _ = self.name.partition("(")
        return short.strip()

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        return super().save(*args, **kwargs)


class Output(models.Model):
    type = models.ForeignKey("OutputType", on_delete=models.CASCADE)

    name = models.TextField()
    description = models.TextField()

    class Meta:
        unique_together = ["type", "name"]

    def __str__(self):
        return self.name


class OutputType(models.Model):
    name = models.TextField(unique=True)

    def __str__(self):
        return self.name


class Service(models.Model):
    name = models.TextField(unique=True)
    slug = models.SlugField(unique=True, blank=True)

    def __str__(self):
        return self.name


class Statute(models.Model):
    name = models.CharField(max_length=256)
    link = models.URLField(unique=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]


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
        related_name="users",
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
