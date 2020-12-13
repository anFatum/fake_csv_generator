from django.db import models
from django.utils.translation import gettext_lazy as _


class CharacterType(models.IntegerChoices):
    COLUMN_SEPARATOR = 1
    STRING_CHARACTER = 2


class FieldType(models.TextChoices):
    FULL_NAME = "name", _("Full Name")
    JOB = "job", _("Job")
    EMAIL = "email", _("Email")
    DOMAIN_NAME = "domain_name", _("Domain name")
    PHONE_NUMBER = "phone_number", _("Phone number")
    COMPANY_NAME = "company", _("Company name")
    TEXT = "sentence", _("Text")
    INTEGER = 'random_int', _("Integer")
    ADDRESS = "address", _("Address")
    DATE = 'date', _("Date")


class DatasetStatus(models.IntegerChoices):
    PENDING = 0
    DONE = 1
    ERROR = 2
