"""
Django models for the gluefun app.
"""


from django.db import models

from fields import SeparatedValuesField


TOKEN = chr(1)


class ScoredFriend(models.Model):
    """
    Model to hold all of the scoring data for a user's friend, one object per
    friend. The SeparatedValuesField is used for simplicity of storing and
    retrieving liked/disliked data in list form.
    """
    user_name = models.CharField(max_length=50)
    friend_name = models.CharField(max_length=50)
    score = models.IntegerField(default=0)
    both_liked = SeparatedValuesField(token=TOKEN, blank=True)
    both_disliked = SeparatedValuesField(token=TOKEN, blank=True)

    def __unicode__(self):
        return _get_unicode(self.user_name, self.friend_name, self.score)


def _get_unicode(*items):
    """Get a space-separated unicode string from the given items."""
    return u' '.join(map(unicode, items))
