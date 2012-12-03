"""
Module to hold Celery tasks for the gluefun app.
"""


# This allows division to output floats by default.
from __future__ import division

import logging

from celery import task

from models import ScoredFriend, TaskCompletion


logger = logging.getLogger('gluefun.custom')

LIKED_ACTIONS = ('Checkin', 'Favorited', 'Liked', 'Saved')
DISLIKED_ACTIONS = ('Disliked', 'Unwanted')
ACTIONS = LIKED_ACTIONS + DISLIKED_ACTIONS


@task()
def compute_friend_scores(client):
    """
    This task performs the work of making requests for data to GetGlue via the
    pre-authorized GlueClient (client) parameter,  scoring each of the user's
    friends according to a comparison of their likes and dislikes, and saving
    the scored data in ScoredFriend objects.
    """
    friends = client.get_friends()
    friends.remove(u'getglue')
    # We're only interested in movies and TV for the time being.
    objects = client.get_objects('movies')
    objects.extend(client.get_objects('tv_shows'))
    completion = TaskCompletion.objects.create(
        task_id=compute_friend_scores.request.id)
    total_friends = len(friends)
    if total_friends == 0:
        completion.percent_complete = 100
        completion.save()

    for friend_count, friend in enumerate(friends):
        score = 0
        both_liked, both_disliked, object_titles = [], [], []
        for obj in objects:
            try:
                my_action = obj['action']
                if my_action not in ACTIONS:
                    continue
                object_key = obj['objectKey']
                object_title = obj['title']
                """
                Maintain a list of object titles, and only query each friend
                for each object once. Objects can appear more than once due to
                the different action types (Liked, Checkin, etc.).
                """
                if object_title not in object_titles:
                    friend_action = client.get_user_object_action(friend,
                                                                  object_key)
                    if friend_action:
                        # User judgement agrees with friend (liked or disliked).
                        if (liked(my_action) and liked(friend_action) or
                            disliked(my_action) and disliked(friend_action)):
                            score += 1
                            both_liked.append(obj['title'])
                        # User judgment is opposite of friend.
                        else:
                            score -= 1
                            both_disliked.append(obj['title'])
                    object_titles.append(object_title)
            except KeyError:
                pass
        """
        We maintain a single object per user/friend combination. An alternative
        would be to create new objects for each task run.
        """
        scored_friend, created = ScoredFriend.objects.get_or_create(
            user_name=client.user_id,
            friend_name=friend)
        scored_friend.score = score
        scored_friend.both_liked = both_liked
        scored_friend.both_disliked = both_disliked
        scored_friend.save()
        # Update task completion.
        percent_complete = int(((friend_count + 1) / total_friends) * 100)
        completion.percent_complete = percent_complete
        completion.save()

def liked(action):
    return action in LIKED_ACTIONS

def disliked(action):
    return action in DISLIKED_ACTIONS
