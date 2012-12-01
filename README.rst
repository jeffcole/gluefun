GlueFun
=======

GlueFun is a starter project for working with the `GetGlue API`_ in Django. It uses requests_ and xmltodict_ to get up and going in a flash.


Features and Examples
---------------------

- Authentication with the GetGlue API.
- Client class to encapsulate details of working with API entities. 
- Paging through method call results.
- Offloading a potentially long-running process to a Celery_ task queue.
- Polling the server for task results via AJAX.
- Support for running on the Heroku_ platform.


Quick Start
-----------

#. Update ``CONSUMER_KEY`` and ``SECRET_KEY`` in ``settings.py`` with the values provided to you by GetGlue.
#. Update ``SITE_ABSOLUTE_URL`` in ``settings.py`` with a URL for your site that can be reached from the outside world (for use by the authorization callback). Might I recommend Heroku?
#. Profit!


.. _GetGlue API: http://www.getglue.com
.. _requests: https://github.com/kennethreitz/requests
.. _xmltodict: https://github.com/martinblech/xmltodict
.. _Celery: http://celeryproject.org/
.. _Heroku: http://www.heroku.com
