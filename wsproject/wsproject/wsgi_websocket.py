"""
WSGI config for wsproject project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/dev/howto/deployment/wsgi/
"""

import gevent.monkey
gevent.monkey.patch_all()


import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wsproject.settings")

import django
django.setup()

from django.conf import settings
from django.core import urlresolvers
from django.core.handlers.wsgi import WSGIRequest

class WebSocketApplication(object):
    def __init__(self):
        pass

    def __call__(self, environ, start_response):
        import uwsgi
        uwsgi.websocket_handshake(environ['HTTP_SEC_WEBSOCKET_KEY'], environ.get('HTTP_ORIGIN', ''))

        request = WSGIRequest(environ)

        urlconf = settings.ROOT_URLCONF
        urlresolvers.set_urlconf(urlconf)
        resolver = urlresolvers.RegexURLResolver(r'^/', urlconf)

        callback, callback_args, callback_kwargs = resolver.resolve(request.path_info)
        callback(request, *callback_args, **callback_kwargs)

        # print "view finish, start_response"
        # response = http.HttpResponse()
        #
        # status_text = STATUS_CODE_TEXT.get(response.status_code, "UNKNOWN STATUS CODE")
        # status = '{0} {1}'.format(response.status_code, status_text)
        # start_response(status, response._headers.values())
        #
        # return response


application = WebSocketApplication()
