"""
Django model fields for the gluefun app.
"""


from django.db import models


class SeparatedValuesField(models.TextField):
    """
    This field provides easy storing/retrieving of lists of strings in a single
    database field, for when using foreign keys to a another model would be
    overkill.

    To use, simply assign a list of strings to the field. On save, the list
    will be automatically joined into a single sting, delimited by the 'token'
    kwarg passed to the constructor. On reading out the field, it will be
    similarly split out into a list again.

    From: http://justcramer.com/2008/08/08/custom-fields-in-django/

    Django 1.4 fix from:
    https://groups.google.com/forum/?fromgroups=#!topic/django-users/Z_AXgg2GCqs
    """
    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        self.token = kwargs.pop('token', ',')
        super(SeparatedValuesField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        if not value: return
        if isinstance(value, list):
            return value
        return value.split(self.token)

    def get_db_prep_value(self, value, connection=None, prepared=None):
        if value:
            assert(isinstance(value, list) or isinstance(value, tuple))
            prepped_value = self.token.join([unicode(s) for s in value])
        else:
            prepped_value = u''
        return (super(SeparatedValuesField, self)
                .get_db_prep_value(prepped_value,
                                   connection=connection,
                                   prepared=prepared))

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self.get_db_prep_value(value)
