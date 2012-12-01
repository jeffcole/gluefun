"""
Local Django settings for the gluefun app.
"""


from settings import *


DATABASES = {'default': dj_database_url.config(default='sqlite:////'
                                               + os.path.join(SITE_ROOT,
                                                              'sqlite3.db'))}
