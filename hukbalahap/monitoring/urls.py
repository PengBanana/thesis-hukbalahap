"""hukbalahap URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url
from .import views
from monitoring.views import AddUserView
app_name = 'monitoring'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^index/$', views.index, name='index'),
    url(r'^pool/$', views.pool, name='pool'),
    url(r'^login/$', views.login, name='login'),
    url(r'^firstLogin/$', views.firstLogin, name='firstLogin'),
    url(r'^indexOwner/$', views.indexOwner, name='indexOwner'),
    url(r'^personnel/$', views.personnel, name='personnel'),
    url(r'^profile/$', views.profile, name='profile'),
    url(r'^poolDetails/(?P<poolitem_id>[0-9]+)/$', views.poolDetails_view, name='poolDetails'),
    url(r'^searchPT/$', views.searchPT, name='searchPT'),
    url(r'^profile/(?P<item_id>[0-9]+)/$', views.profile, name='profile'),
    url(r'^addUser/$', views.addUser, name='addUser'),
    url(r'^setMaintenance/$', views.setMaintenance, name='setMaintenance'),
    url(r'^finishMaintenance/$', views.finishMaintenance, name='finishMaintenance'),
    url(r'^notFound/$', views.notFound, name='notFound'),
]
