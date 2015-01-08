from django.conf.urls import include, url
from django.contrib import admin

import apps.index.views
import apps_websocket.chat.views

urlpatterns = [
    # Examples:
    # url(r'^$', 'wsproject.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),

    url(r'^$', apps.index.views.index),
    url(r'^chat/$', apps.index.views.chat),
    url(r'^ws/chat/$', apps_websocket.chat.views.chat),

]
