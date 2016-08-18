import logging
import random
from datetime import datetime

from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import models
import modularodm.exceptions
import pytz

from osf_models.exceptions import ValidationError
from osf_models.modm_compat import to_django_query
from osf_models.utils.base import get_object_id

ALPHABET = '23456789abcdefghjkmnpqrstuvwxyz'

logger = logging.getLogger(__name__)

def generate_guid(length=5):
    while True:
        guid_id = ''.join(random.sample(ALPHABET, length))

        try:
            # is the guid in the blacklist
            BlackListGuid.objects.get(guid=guid_id)
        except BlackListGuid.DoesNotExist:
            # it's not, check and see if it's already in the database
            try:
                Guid.objects.get(guid=guid_id)
            except Guid.DoesNotExist:
                # valid and unique guid
                return guid_id


class MODMCompatibilityQuerySet(models.QuerySet):
    def sort(self, *fields):
        # Fields are passed in as e.g. [('title', 1), ('date_created', -1)]
        if isinstance(fields[0], list):
            fields = fields[0]

        def sort_key(item):
            if isinstance(item, basestring):
                return item
            elif isinstance(item, tuple):
                field_name, direction = item
                prefix = '-' if direction == -1 else ''
                return ''.join([prefix, field_name])
        sort_keys = [sort_key(each) for each in fields]
        return self.order_by(*sort_keys)

    def limit(self, n):
        return self[:n]


class BaseModel(models.Model):
    """Base model that acts makes subclasses mostly compatible with the
    modular-odm ``StoredObject`` interface.
    ."""

    objects = MODMCompatibilityQuerySet.as_manager()

    class Meta:
        abstract = True

    @classmethod
    def load(cls, data):
        try:
            if issubclass(cls, GuidMixin):
                return cls.objects.get(_guid__guid=data)
            elif issubclass(cls, ObjectIDMixin):
                return cls.objects.get(guid=data)
            return cls.objects.getQ(pk=data)
        except cls.DoesNotExist:
            return None

    @classmethod
    def find_one(cls, query):
        try:
            return cls.objects.get(to_django_query(query, model_cls=cls))
        except cls.DoesNotExist:
            raise modularodm.exceptions.NoResultsFound()
        except cls.MultipleObjectsReturned as e:
            raise modularodm.exceptions.MultipleResultsFound(*e.args)

    @classmethod
    def find(cls, query=None):
        if not query:
            return cls.objects.all()
        else:
            return cls.objects.filter(to_django_query(query, model_cls=cls))

    @classmethod
    def remove(cls, query):
        return cls.find(query).delete()

    @classmethod
    def remove_one(cls, obj):
        if obj.pk:
            return obj.delete()

    @property
    def _primary_name(self):
        return '_id'

    def save(self, *args, **kwargs):
        # Make Django validate on save (like modm)
        if not kwargs.get('force_insert') and not kwargs.get('force_update'):
            try:
                self.full_clean()
            except DjangoValidationError as err:
                raise ValidationError(*err.args)
        return super(BaseModel, self).save(*args, **kwargs)

    @classmethod
    def migrate_from_modm(cls, modm_obj):
        """
        Given a modm object, make a django object with the same local fields.

        This is a base method that may work for simple objects. It should be customized in the child class if it
        doesn't work.
        :param modm_obj:
        :return:
        """
        django_obj = cls()

        local_django_fields = set([x.name for x in django_obj._meta.get_fields() if not x.is_relation])

        intersecting_fields = set(modm_obj.to_storage().keys()).intersection(
            set(local_django_fields))

        for field in intersecting_fields:
            modm_value = getattr(modm_obj, field)
            if modm_value is None:
                continue
            if isinstance(modm_value, datetime):
                modm_value = pytz.utc.localize(modm_value)
            setattr(django_obj, field, modm_value)

        return django_obj


class ReferentDescriptor(object):
    def __init__(self, name):
        self.name = name

    def __get__(self, instance=None, owner=None):
        return instance.content_type.get_object_for_this_type(_guid_id=instance.pk)

    def __set__(self, instance, value):
        new_content_type = ContentType.objects.get_for_model(value)
        value._guid = instance
        instance.content_type = new_content_type


class ReferentField(GenericRelation):
    def contribute_to_class(self, cls, name='referent', **kwargs):
        super(ReferentField, self).contribute_to_class(cls, name)
        setattr(cls, self.name, ReferentDescriptor(self.name))


class Guid(BaseModel):
    id = models.AutoField(primary_key=True)
    guid = models.fields.CharField(max_length=255,
                                   default=generate_guid,
                                   unique=True,
                                   db_index=True)
    content_type = models.ForeignKey(ContentType, null=True)
    referent = ReferentField('self')

    # Override load in order to load by GUID
    @classmethod
    def load(cls, data):
        try:
            return cls.objects.get(guid=data)
        except cls.DoesNotExist:
            return None



class BlackListGuid(models.Model):
    id = models.AutoField(primary_key=True)
    guid = models.fields.CharField(max_length=255, unique=True, db_index=True)


def generate_guid_instance():
    # TODO For some reason guids are being created during migrations, one for every model that inherits from GuidMixin
    return Guid.objects.create().id


class PKIDStr(str):
    def __new__(self, _id, pk):
        return str.__new__(self, _id)

    def __init__(self, _id, pk):
        self.__pk = pk

    def __int__(self):
        return self.__pk


class MODMCompatibilityGuidQuerySet(MODMCompatibilityQuerySet):

    def get_by_guid(self, guid):
        return self.get(_guid__guid=guid)


class ObjectIDMixin(models.Model):
    guid = models.CharField(max_length=255,
                                  unique=True,
                                  db_index=True,
                                  default=get_object_id)

    @property
    def _object_id(self):
        return self.guid

    @property
    def _id(self):
        return PKIDStr(self._object_id, self.pk)

    _primary_key = _id

    @classmethod
    def migrate_from_modm(cls, modm_obj):
        """
        Given a modm object, make a django object with the same local fields.

        This is a base method that may work for simple objects. It should be customized in the child class if it
        doesn't work.
        :param modm_obj:
        :return:
        """
        django_obj = cls()

        local_django_fields = set([x.name for x in django_obj._meta.get_fields() if not x.is_relation])

        intersecting_fields = set(modm_obj.to_storage().keys()).intersection(
            set(local_django_fields))

        for field in intersecting_fields:
            modm_value = getattr(modm_obj, field)
            if modm_value is None:
                continue
            if isinstance(modm_value, datetime):
                modm_value = pytz.utc.localize(modm_value)
            setattr(django_obj, field, modm_value)

        return django_obj

    class Meta:
        abstract = True


class GuidMixin(models.Model):
    _guid = models.ForeignKey('Guid',
                                 default=generate_guid_instance,
                                 null=True, blank=True,
                                 # disable reverse relationships, we'll make them ourselves
                                 related_name='+')

    objects = MODMCompatibilityGuidQuerySet.as_manager()

    @property
    def guid(self):
        return self._guid.guid

    @property
    def _id(self):
        return PKIDStr(self._guid.guid, self.pk)

    @property
    def deep_url(self):
        return None

    _primary_key = _id


    def save(self, *args, **kwargs):
        # set the content type on the guid so we can reference it later
        self._guid.content_type = ContentType.objects.get_for_model(self)
        return super(GuidMixin, self).save(*args, **kwargs)

    @classmethod
    def migrate_from_modm(cls, modm_obj):
        """
        Given a modm object, make a django object with the same local fields.
        This is a base method that may work for simple things. It should be customized for complex ones.
        :param modm_obj:
        :return:
        """
        guid, created = Guid.objects.get_or_create(guid=modm_obj._id)
        if created:
            logger.debug('Created a new Guid for {}'.format(modm_obj))
        django_obj = cls()
        django_obj._guid = guid

        local_django_fields = set([x.name for x in django_obj._meta.get_fields() if not x.is_relation])

        intersecting_fields = set(modm_obj.to_storage().keys()).intersection(
            set(local_django_fields))

        for field in intersecting_fields:
            modm_value = getattr(modm_obj, field)
            if modm_value is None:
                continue
            if isinstance(modm_value, datetime):
                modm_value = pytz.utc.localize(modm_value)
            setattr(django_obj, field, modm_value)

        return django_obj

    class Meta:
        abstract = True
