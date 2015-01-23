"""
WSGI config for wsproject project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/dev/howto/deployment/wsgi/
"""
import gevent.monkey
gevent.monkey.patch_all()

import redis
import uwsgi
from gevent import select

from django.conf import settings
from django.http import HttpResponse
from django.utils.decorators import classonlymethod


def _get_setting(key, default_value):
    return getattr(settings, key, default_value)

redis_client = redis.Redis(
        connection_pool=redis.ConnectionPool(
            host=_get_setting('WS_REDIS_HOST', '127.0.0.1'),
            port=_get_setting('WS_REDIS_HOST', 6379),
            db=_get_setting('WS_REDIS_DB', 0)
            )
        )

REDIS_GLOBAL_channel = _get_setting('WS_REDIS_GLOBAL_channel', 'MYchannel')
TIMEOUT = _get_setting('WS_WAIT_TIMEOUT', 10)

class WebSocketView(object):
    class WebSocketError(Exception):
        pass


    def __init__(self, request, *args, **kwargs):
        print "__init__"
        self.request = request
        self.args = args
        self.kwargs = kwargs
        self.redis = redis.Redis()
        print self.redis
        self.channel = self.redis.pubsub()
        print self.channel
        self.channel.subscribe(REDIS_GLOBAL_channel)
        print "before on_connect"
        self.on_connect()


    def publish_global(self, text):
        self.redis.publish(REDIS_GLOBAL_channel, text)

    def recv(self):
        try:
            data = uwsgi.websocket_recv_nb()
            if data:
                self.on_websocket_data(data)
        except:
            print "==== Error ===="
            import traceback
            traceback.print_exc()
            print "==== Error ===="
            raise self.WebSocketError()

    def send(self, text):
        uwsgi.websocket_send(text)

    def send_binary(self, binary_data):
        uwsgi.websocket_send_binary(binary_data)

    def on_connect(self):
        raise NotImplementedError()

    def on_connection_lost(self):
        raise NotImplementedError()

    def on_websocket_data(self, data):
        raise NotImplementedError()

    def on_channel_data(self, data):
        raise NotImplementedError()


    def run(self):
        websocket_fd = uwsgi.connection_fd()
        channel_fd = self.channel.connection._sock.fileno()

        fds = [websocket_fd, channel_fd]

        try:
            while True:
                readable, _, _ = select.select(fds, [], [], TIMEOUT)
                if not readable:
                    self.recv()
                    continue

                for rfd in readable:
                    if rfd == websocket_fd:
                        self.recv()
                    if rfd == channel_fd:
                        data = self.channel.get_message()
                        if data and data['type'] == 'message':
                            self.on_channel_data(data)
        except self.WebSocketError:
            return HttpResponse('ws ok')
        finally:
            self.channel.unsubscribe()
            self.on_connection_lost()

    @classonlymethod
    def as_view(cls):
        def wrapper(request, *args, **kwargs):
            self = cls(request, *args, **kwargs)
            return self.run()
        return wrapper




import django
from django.core.handlers.wsgi import WSGIHandler

class WebSocketApplication(WSGIHandler):
    def _fake_start_response(self, *args, **kwargs):
        pass

    def __call__(self, environ, start_response):
        uwsgi.websocket_handshake()
        print "HANDSHAKE DONE"
        return super(WebSocketApplication, self).__call__(environ, self._fake_start_response)


def get_wsgi_application():
    django.setup()
    return WebSocketApplication()

application = get_wsgi_application()


