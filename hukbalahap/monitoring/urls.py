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
from django.conf.urls import handler404
from django.conf.urls.static import static
app_name = 'monitoring'

urlpatterns = [
    url(r'^login/$', views.login, name='login'),
    url(r'^logout_view/$', views.logout_view, name='logout_view'),
    url(r'^$', views.index, name='index'),
    url(r'^index/$', views.index, name='index'),
    url(r'^personnel/$', views.personnel, name='personnel'),
    url(r'^profile/$', views.profile, name='profile'),
    url(r'^editDetails/$', views.editDetails, name='editDetails'),
    url(r'^poolDetails/(?P<poolitem_id>[0-9]+)/$', views.poolDetails_view, name='poolDetails'),
    url(r'^searchPT/$', views.searchPT, name='searchPT'),
    url(r'^profile/(?P<item_id>[0-9]+)/$', views.profile, name='profile'),
    url(r'^addUser/$', views.addUser, name='addUser'),
    url(r'^viewMaintenance/$', views.viewMaintenance, name='viewMaintenance'),
    url(r'^setMaintenance/$', views.setMaintenance, name='setMaintenance'),
    url(r'^submitMaintenanceRequest/$', views.submitMaintenanceRequest, name='submitMaintenanceRequest'),
    url(r'^finishMaintenance/$', views.finishMaintenance, name='finishMaintenance'),
    url(r'^notFound/$', views.notFound, name='notFound'),
    url(r'^filterPoolStat/$', views.filterPoolStat, name='filterPoolStat'),
    url(r'^setMaintenanceCompute/$', views.setMaintenanceCompute, name='setMaintenanceCompute'),
    url(r'^maintenanceDetails/$', views.maintenanceDetails, name='maintenanceDetails'),
    url(r'^maintenanceDetailsChemicals/$', views.maintenanceDetailsChemicals, name='maintenanceDetailsChemicals'),
]
