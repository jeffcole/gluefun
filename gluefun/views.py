"""
Django views for the gluefun app.
"""


import json
import logging
import pprint

from urlparse import urljoin

from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponse
from django.shortcuts import redirect, render
from django.template import RequestContext
from django.template.loader import render_to_string

import settings

from glueclient import GlueClient
from models import ScoredFriend, TaskCompletion
from tasks import compute_friend_scores


logger = logging.getLogger('gluefun.custom')
pp = pprint.PrettyPrinter(indent=4)


def login(request):
    """
    Login view to create the client to GetGlue, get a request token, and
    redirect to their authorization URL.
    """
    if request.method == 'POST':
        client = GlueClient()
        request_token = client.get_request_token()
        request.session['request_token'] = request_token
        callback_url = urljoin(settings.SITE_ABSOLUTE_URL, reverse(home))
        return redirect(client.get_authorization_url(request_token,
                                                     callback_url))
    return render(request, 'login.html')

def home(request):
    """
    GetGlue redirects to this view after attempting to authorize the user.
    We then try to retrieve an access token with the previously granted request
    token so that we can make further requests. If authorization was not
    successful, we redirect back to the login view. If it was successful, we
    store the client object and user name in the session and render the home
    template.

    Once the user posts back to this view, it kicks off the task to run the
    scoring computation for the user, and redirects to the results view where
    the user waits for the task to complete.
    """
    if 'request_token' in request.session:
        if request.method == 'GET':
            client = GlueClient()
            client.retrieve_access_token(request.session['request_token'])
            if not client.user_id: # Authorization was not successful.
                return redirect(login)
            request.session['glue_client'] = client
            request.session['user_name'] = client.user_id
        else:
            client = request.session['glue_client']
            result = compute_friend_scores.delay(client)
            request.session['task_id'] = result.id

            return redirect(results)

        return render(request, 'home.html')
    raise Http404

def results(request):
    """
    This view handles AJAX requests for results. On each such request, the
    TaskCompletion model is queried for the percent completion so that the user
    can monitor progress. Once the task has finished, the ScoredFriend model is
    queried for the results and they are rendered to the user.

    If the request isn't an AJAX request, simply render the results template.
    """
    if request.is_ajax():
        user_name = request.session.get('user_name', None)
        task_id = request.session.get('task_id', None)
        if user_name and task_id:
            try:
                task_completion = (TaskCompletion.objects.get(task_id=task_id)
                                   .percent_complete)
            except TaskCompletion.DoesNotExist:
                task_completion = 0
            
            html = None
            if task_completion == 100:
                ranked_friends = (ScoredFriend.objects
                                  .filter(user_name=user_name).order_by('-score'))
                html = render_to_string('results_table.html',
                                        {'ranked_friends': ranked_friends},
                                        context_instance=RequestContext(request))
            data = {'task_completion': task_completion, 'html': html}
            return HttpResponse(json.dumps(data),
                                content_type='application/json')

        raise Http404

    if 'user_name' in request.session:
        return render(request, 'results.html')
    
    raise Http404
