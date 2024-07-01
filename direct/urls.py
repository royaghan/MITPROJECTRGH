from direct.views import Inbox, Directs, NewConversation, SendDirect, UserSearch
from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.urls.base import reverse_lazy
from main.views import profile


urlpatterns = [
    path('', Inbox, name='inbox'),
    path('directs/<username>', Directs, name='directs'),
    path('new/<username>', NewConversation, name='newconversation'),
    path('search/', UserSearch, name='user-search'),
    path('send/', SendDirect, name='send-direct'),

]
