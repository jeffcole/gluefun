GlueFun
=======

GlueFun is an application that ranks how compatible you are with your friends, according to your/their likes and dislikes on the TV/movie social network GetGlue_.


Features and Examples
---------------------

- Authentication with the `GetGlue RESTful API`_.
- Interaction with the API through the Python requests_ library.
- Client class to encapsulate details of working with API entities. 
- Paging through method call results.
- Offloading a potentially long-running process to a Celery_ task queue.
- Polling the server for task results via AJAX.
- A nifty accurately-updated progress bar.
- Support for running on the Heroku_ platform.


Quick Start
-----------

To use GlueFun as a starter project for working with the GetGlue API:

#. Update ``CONSUMER_KEY`` and ``SECRET_KEY`` in ``settings.py`` with the values provided to you by GetGlue.
#. Update ``SITE_ABSOLUTE_URL`` in ``settings.py`` with a URL for your site that can be reached from the outside world (for use by the authorization callback). Might I recommend Heroku?
#. Profit!


.. _GetGlue: http://www.getglue.com
.. _GetGlue API: http://www.getglue.com/api
.. _requests: https://github.com/kennethreitz/requests
.. _Celery: http://celeryproject.org/
.. _Heroku: http://www.heroku.com
