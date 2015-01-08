#! -*- coding: utf-8 -*-

from gevent import select
import redis


r = redis.Redis()

def chat(request):
    import uwsgi

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

