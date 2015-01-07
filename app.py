# -*- coding: utf-8 -*-
"""
Author:        Wang Chao <yueyoum@gmail.com>
Filename:      app.py
Date created:  2015-01-07 17:11:43
Description:

"""
import uwsgi


def application(env, start_response):
    print "start websocket handshake"
    uwsgi.websocket_handshake()
    print "success websocket handshake"
    while True:
        msg = uwsgi.websocket_recv()
        print "Got:", msg
        uwsgi.websocket_send(msg)



