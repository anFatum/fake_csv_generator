from django.db.models.query import QuerySet
from csv_generator.models.choices import CharacterType


class CharacterQuerySet(QuerySet):
    def column_separators(self):
        return self.filter(character_type=CharacterType.COLUMN_SEPARATOR)

    def string_characters(self):
        return self.filter(character_type=CharacterType.STRING_CHARACTER)


CharacterManager = CharacterQuerySet.as_manager
