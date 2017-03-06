#modules
from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns

#import views for providing exact classes for url
from online import views

#list of url's
urlpatterns = [
	url(r'^$', views.Home.as_view(), name='home'),
	url(r'^register/$', views.Register.as_view(), name='register'),
	url(r'^login/$', views.Login.as_view(), name='login'),
	url(r'^profile/$', views.Profile.as_view(), name='profile'),
	url(r'^logout/$', views.Logout.as_view(), name='logout'),
	url(r'^AddCity/$', views.AddCity.as_view(), name='AddCity'),
	]

urlpatterns = format_suffix_patterns(urlpatterns)
# (u?P<pk>[0-9]+)/
