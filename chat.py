#! -*- coding: utf-8 -*-
#!./uwsgi --http-socket :9090 --async 100 ...
# same chat example but using uwsgi async api
# for pypy + continulets just run:
# uwsgi --http-socket :9090 --pypy-home /opt/pypy --pypy-wsgi-file tests/websockets_chat_async.py --pypy-eval "uwsgi_pypy_setup_continulets()" --async 100

import gevent.monkey
gevent.monkey.patch_all()

from gevent.queue import Queue
from gevent import select

import uwsgi
import redis


with open("chat_index.html") as f:
    html = f.read()


r = redis.StrictRedis(host='localhost', port=6379, db=0)


def application(env, sr):
    ws_scheme = 'ws'
    if 'HTTPS' in env or env['wsgi.url_scheme'] == 'https':
        ws_scheme = 'wss'

    if env['PATH_INFO'] == '/':
        sr('200 OK', [('Content-Type','text/html')])
        output = html % (ws_scheme, env['HTTP_HOST'])
        return output

    elif env['PATH_INFO'] == '/favicon.ico':
        return ""

    elif env['PATH_INFO'] == '/demo/':
        uwsgi.websocket_handshake(env['HTTP_SEC_WEBSOCKET_KEY'], env.get('HTTP_ORIGIN', ''))

        client_amount = r.incr('demo-client-amount')
        uwsgi.websocket_send("{0} 人在线".format(client_amount))

        channel = r.pubsub()
        channel.subscribe('demo')

        websocket_fd = uwsgi.connection_fd()
        redis_fd = channel.connection._sock.fileno()


        try:
            while True:
                print 'before select'
                rable, wable, xable = select.select([websocket_fd, redis_fd], [], [], timeout=4)
                print 'after select'

                if not rable:
                    uwsgi.websocket_recv_nb()
                    print "Just ping/pong"
                    continue

                for rfd in rable:
                    if rfd == websocket_fd:
                        data = uwsgi.websocket_recv_nb()
                        if data:
                            print "WebSocket:", data
                            r.publish('demo', data)

                    elif rfd == redis_fd:
                        print "start get_message"
                        msg = channel.get_message()
                        if msg:
                            print "Channel:", msg
                            uwsgi.websocket_send(str(msg['data']))
        except Exception as e:
            print "==== Error ===="
            print e
        finally:
            r.incr('demo-client-amount', -1)
            r.publish('demo', '有人下线')
            channel.unsubscribe('demo')



