"""
Module to hold Celery tasks for the gluefun app.
"""


from celery import task

from models import ScoredFriend


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
    # We're only interested in movies and TV for the time being.
    objects = client.get_objects('movies')
    objects.extend(client.get_objects('tv_shows'))

    for friend in friends:
        # Skip the getglue user.
        if friend == 'getglue':
            continue
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

def liked(action):
    return action in LIKED_ACTIONS

def disliked(action):
    return action in DISLIKED_ACTIONS
