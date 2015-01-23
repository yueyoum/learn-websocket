#! -*- coding: utf-8 -*-


import arrow

from wsproject.wsgi_websocket import WebSocketView

now = lambda : arrow.utcnow().to('Asia/Shanghai').format('HH:mm:ss')
def log(text):
    print "{0}: {1}".format(now(), text)


class Chat(WebSocketView):
    def on_connect(self):
        print "on connect"
        client_amount = self.redis.incr('demo-client-amount')
        self.send("{0} 人在线".format(client_amount))
        self.publish_global(now() + " 有人上线了")

    def on_websocket_data(self, data):
        print "websocket data:", data
        self.publish_global(data)

    def on_channel_data(self, data):
        print "channel data", data
        data = str(data['data'])
        self.send(data)

    def on_connection_lost(self):
        print "connection lost"
        self.redis.incr('demo-client-amount', -1)
        self.publish_global(now() + " 有人下线了")

