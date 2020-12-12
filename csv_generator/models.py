from django.db import models
from django.contrib.auth import get_user_model
from csv_generator.abc import TimestampedModel
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class Character(models.Model):
    class Type(models.IntegerChoices):
        COLUMN_SEPARATOR = 1
        STRING_CHARACTER = 2

    character = models.CharField(max_length=1, blank=False, null=False)
    character_name = models.CharField(max_length=128, blank=False, null=False)
    character_type = models.IntegerField(choices=Type.choices, blank=False, null=False)

    def __str__(self):
        return f"{self.character_name} ({self.character})"

    @property
    def is_separator(self):
        return self.character_type == Character.Type.COLUMN_SEPARATOR


class Schema(TimestampedModel):
    title = models.CharField(max_length=128, blank=False, null=False)
    owner = models.ForeignKey(User,
                              related_name="schemas",
                              on_delete=models.CASCADE)
    column_separator = models.ForeignKey(Character,
                                         on_delete=models.PROTECT,
                                         related_name="column_separator_schemas")
    string_character = models.ForeignKey(Character,
                                         on_delete=models.PROTECT,
                                         related_name="string_character_schemas")


class Field(models.Model):
    class Type(models.TextChoices):
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

    field_type = models.TextField(choices=Type.choices,
                                  blank=False,
                                  null=False)
    name = models.CharField(max_length=128, blank=False, null=False)
    schema = models.ForeignKey(Schema,
                               on_delete=models.CASCADE,
                               related_name="fields")
    options = models.JSONField(blank=False, null=False)
    order = models.IntegerField(blank=False, null=False)


def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'user_{0}/datasets/{1}'.format(instance.schema.owner.id, filename)


class Dataset(TimestampedModel):
    class Status(models.IntegerChoices):
        PENDING = 0
        DONE = 1
        ERROR = 2

    schema = models.ForeignKey(Schema,
                               on_delete=models.CASCADE,
                               related_name="datasets")
    rows = models.IntegerField(blank=False, null=False)
    file = models.FileField(upload_to=user_directory_path,
                            blank=True,
                            null=True)
    status = models.IntegerField(choices=Status.choices,
                                 blank=False,
                                 null=False)
