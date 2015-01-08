from django.shortcuts import render_to_response
from django.http import HttpResponse


def index(request):
    return HttpResponse("OK, You are here!")


def chat(request):
    name = request.GET.get('name', 'anonymous')

    return render_to_response(
        'chat.html',
        {
            'USER_NAME': name,
            'WEBSOCKET_URL': 'ws://' + request.get_host()
        }
    )

