#modules
from django.conf.urls import url,include
from django.contrib import admin

#urls for project defiens all app urls
urlpatterns = [
    url(r'admin/',admin.site.urls),
    url(r'^',include('online.urls')),
    url(r'^api-auth/',include('rest_framework.urls',namespace='rest_framework')),
]
