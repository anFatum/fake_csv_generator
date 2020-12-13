from django.contrib.auth import get_user_model
from django.db import models

from csv_generator.models.abc import TimestampedModel
from csv_generator.models.choices import CharacterType, FieldType, DatasetStatus
from csv_generator.querysets import CharacterManager
from csv_generator.utils import user_directory_path

User = get_user_model()


class Character(models.Model):
    objects = CharacterManager()
    character = models.CharField(max_length=1, blank=False, null=False)
    character_name = models.CharField(max_length=128, blank=False, null=False)
    character_type = models.IntegerField(choices=CharacterType.choices, blank=False, null=False)

    def __str__(self):
        return f"{self.character_name} ({self.character})"


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
    field_type = models.TextField(choices=FieldType.choices,
                                  blank=False,
                                  null=False)
    name = models.CharField(max_length=128, blank=False, null=False)
    schema = models.ForeignKey(Schema,
                               on_delete=models.CASCADE,
                               related_name="fields")
    options = models.JSONField(blank=True, null=True)
    order = models.IntegerField(blank=False, null=False)


class Dataset(TimestampedModel):
    schema = models.ForeignKey(Schema,
                               on_delete=models.CASCADE,
                               related_name="datasets")
    rows = models.IntegerField(blank=False, null=False)
    file = models.FileField(upload_to=user_directory_path,
                            blank=True,
                            null=True)
    status = models.IntegerField(choices=DatasetStatus.choices,
                                 blank=False,
                                 null=False)
