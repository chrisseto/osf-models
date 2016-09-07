from django.db import models
from django.utils import timezone
from osf_models.models.base import BaseModel, ObjectIDMixin


class AlternativeCitation(ObjectIDMixin, BaseModel):
    # TODO DELETE ME POST MIGRATION
    modm_model_path = 'website.project.model.AlternativeCitation'
    modm_query = None
    # /TODO DELETE ME POST MIGRATION
    name = models.CharField(max_length=256)
    text = models.CharField(max_length=2048)

    def to_json(self):
        return {
            'id': self._id,
            'name': self.name,
            'text': self.text
        }


class CitationStyle(ObjectIDMixin, BaseModel):
    """Persistent representation of a CSL style.

    These are parsed from .csl files, so that metadata fields can be indexed.
    """

    # TODO DELETE ME POST MIGRATION
    modm_model_path = 'website.citations.models.CitationStyle'
    modm_query = None
    # /TODO DELETE ME POST MIGRATION

    # The name of the citation file, sans extension
    _id = models.CharField(max_length=255, db_index=True)

    # The full title of the style
    title = models.CharField(max_length=255)

    # Datetime the file was last parsed
    date_parsed = models.DateTimeField(default=timezone.now)

    short_title = models.CharField(max_length=2048)
    summary = models.CharField(max_length=4200)  # longest value was 3,812 8/23/2016

    def to_json(self):
        return {
            'id': self._id,
            'title': self.title,
            'short_title': self.short_title,
            'summary': self.summary,
        }
