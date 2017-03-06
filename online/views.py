#modules
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.views import APIView
from django.views.decorators.csrf import csrf_exempt
from django.core.context_processors import csrf
from django.contrib import auth
from django.contrib.auth.hashers import check_password, make_password
import json
import urllib2
from datetime import date,datetime, timedelta as td
import os
import time

#serializers for different classes
from online.serializers import RegisterSerializer, LoginSerializer, ProfileSerializer,AddCitySerializer
#model imprting
from django.contrib.auth.models import User
from .models import WeatherId
#fusiond charts
from .fusioncharts import FusionCharts


#function for wondergroung api calling takes input stationId,category,startdate,enddate
#returns error if particuler stationId is not present otherwise proiding list of label and values
def api_call(city_name,category,querydate,enddate):
    API_KEY = "d61f28010262580e"
    country = "India"
    city = city_name
    value_api_list = []
    label_api_list = []
    date_list= map(int,querydate.split("-"))
    enddate_list=map(int,enddate.split("-"))
    d1 = date(date_list[0],date_list[1],date_list[2])
    d2 = date(enddate_list[0],enddate_list[1],enddate_list[2])
    delta = d2 - d1
    for i in range(delta.days + 1):
        his_date=(d1 + td(days=i)).strftime("%Y%m%d")
        req_url = "http://api.wunderground.com/api/"+API_KEY+"/history_" +his_date+ "/q/pws:" + city +".json"
        url_open = urllib2.urlopen(req_url)
        weather  = json.load(url_open)
        try:
            if weather["response"]["error"]["type"] == "Station:OFFLINE":
                print "yes1"
                return value_api_list,label_api_list
        except:
            pass
        print "yes2"
        prev_entries = 0
        total_entries = len(weather["history"]["observations"])
        present_entries = total_entries - prev_entries
        prev_entries = total_entries
        for i in range(present_entries):
            value_api_list.append(str(weather["history"]["observations"][i][category]))
            month = str(weather["history"]["observations"][i]["date"]["mon"])
            mday = str(weather["history"]["observations"][i]["date"]["mday"])
            hour =   str(weather["history"]["observations"][i]["date"]["hour"])
            minute = str(weather["history"]["observations"][i]["date"]["min"])
            label =  mday + "/" + month + " " + hour + ":" + minute
            label_api_list.append(label)
    return value_api_list,label_api_list

#function makes graph for api data,takes city_name,category,startdate,enddate
#if stationId is not present returns error otherwise object of graph
def make_graph(city_name,category,date,enddate):
    value_api_list,label_api_list = api_call(city_name,category,date,enddate)
    if len(value_api_list) == 0:
        return "Data is not available for particular stationId"
    datasource = {}
    if category == "tempm":
        category = "temparature"
        numbersuffix =  "C"
    elif category == "wspdm":
        category = "Wind speed"
        numbersuffix =  "KPH"
    else:
        category = "humidity"
        numbersuffix =  "GWM/M^3"

    datasource["chart"] = {
       "caption": "weather graph","subcaption": category,"xaxisname": "time",
        "yaxisname": category,"numbersuffix": numbersuffix,"theme": "zune"}
    label_list = []
    for i in label_api_list:
        label_list.append({"label":i})
    datasource["categories"] = [{ "category": label_list }]
    value_list = []
    for i in value_api_list:
        value_list.append({"value":i})
    datasource["dataset"] = [{ "seriesname": category,"renderas": "area","showvalues": "0","data": value_list}]
    mscombi2dChart = FusionCharts("mscombi2d", "ex3", "100%", 400, "chart-1", "json", datasource)
    return mscombi2dChart

#class for home page tamplate home.html
#get function for get request
#post for post request
class Home(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'home.html'

    def get(self,request,format=None):
        user = request.user
        cities = WeatherId.objects.all().values_list('stationId')
        list_of_city = []
        for i in cities:
            list_of_city.append(str("".join(i)))
        i = datetime.now()
        todayDate= str(i)[:11]
        return Response({'list_of_city':list_of_city,'todayDate':todayDate})

    def post(self,request,format = None):
        city_name = request.data['city_name']
        category = request.data['category']
        date = request.data['date']
        enddate = request.data['enddate']
        cities = WeatherId.objects.all().values_list('stationId')
        list_of_city = []
        for i in cities:
            list_of_city.append(str("".join(i)))
        mscombi2dChart = make_graph(city_name,category,date,enddate)
        i = datetime.now()
        todayDate = str(i)[:11]
        if mscombi2dChart == "Data is not available for particular stationId":
             return Response({'isError' : mscombi2dChart,'list_of_city':list_of_city,'todayDate':todayDate})
        return Response({'output' : mscombi2dChart.render(),'list_of_city':list_of_city,'graph':"graph",'todayDate':todayDate})
#class for register page ,template register.html
class Register(APIView):
	renderer_classes = [TemplateHTMLRenderer]
	template_name = 'register.html'

	def get(self, request, format=None):
		if request.user.is_authenticated():
			return redirect('home')
		else:
			serializer = RegisterSerializer()
			return Response({'serializer':serializer,'title':'Register'})
#for post request,checks user exist or not if exist show error otherwise save into database
	def post(self, request, format=None):
		username = request.data['username']
		if User.objects.filter(username=username).count():
			serializer = RegisterSerializer()
			error = "username '"+ username +"' already exist."
			return Response({'serializer':serializer,'error':error,'title':'Register'})
		else:
			serializer = RegisterSerializer(data=request.data)
			if not serializer.is_valid():
				return Response({'serializer':serializer, 'title':'Register'})
			serializer.save()
			return redirect('login')

#class for login page.template-login.html
class Login(APIView):
	renderer_classes = [TemplateHTMLRenderer]
	template_name = 'login.html'

	def get(self, request, format=None):
		if request.user.is_authenticated():
			return redirect('home')
		else:
			serializer = LoginSerializer()
			send = {'serializer':serializer,'title':'Login'}
			send.update(csrf(request))
			return Response(send)

	def post(self, request, format=None):
		username = request.data.get('username', '')
		password = request.data.get('password', '')
		user = auth.authenticate(username=username, password=password)
		if user is not None:
			auth.login(request, user)
			return redirect('home')
		else:
			serializer = LoginSerializer(data=request.data)
			if not serializer.is_valid():
				return Response({'serializer':serializer,'title':'Login'})
			send = {'serializer':serializer,'error':'username or password is incorrect.','title':'Login'}
			send.update(csrf(request))
			return Response(send)

#class for profile page,template-profile.html
class Profile(APIView):
	renderer_classes = [TemplateHTMLRenderer]
	template_name = 'profile.html'

	def get_objects(self, pk):
		try:
			return User.objects.get(id=pk)
		except User.DoesNotExist:
			raise Http404

	def get(self, request, format=None):
		if request.user.is_authenticated():
			user = self.get_objects(request.user.id)
			serializer = ProfileSerializer(user)
			return Response({'serializer':serializer, 'user':user, 'title': 'Profile'})
		else:
			return redirect('home')
#post funtion updates changes
	def post(self, request, format=None):
		user = self.get_objects(request.user.id)
		serializer = ProfileSerializer(user, data=request.data)
		if not serializer.is_valid():
			return Response({'serializer':serializer, 'user':user, 'title': 'Profile'})
		serializer.save()
		user = self.get_objects(request.user.id)
		serializer = ProfileSerializer(user)
		return Response({'serializer':serializer, 'user':user, 'title': 'Profile'})


#class for logout and redirect to home page
class Logout(APIView):
	renderer_classes = [TemplateHTMLRenderer]
	template_name = 'logout.html'

	def get(self, request, format=None):
		if request.user.is_authenticated():
			auth.logout(request)
			return redirect ('home')
		else:
			return redirect('home')

#class for addcity,template- addcity.html
class AddCity(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'AddCity.html'

    def get(self, request, format=None):
        serializer = AddCitySerializer
        return Response({'serializer':serializer,'title':'AddCity'})
#saves the new stationid into databse id present shows message that stationId present otherwise success message
    def post(self, request, format=None):
        city_name = request.data["stationId"]
        if WeatherId.objects.filter(stationId=city_name).count():
            serializer = AddCitySerializer()
            error = "cityname'"+ city_name +"' already exist."
            return Response({'serializer':serializer,'error':error,'title':'AddCity'})
        else:
            serializer = AddCitySerializer(data=request.data)
            print serializer
            if serializer.is_valid():
                serializer.save()
            serializer = AddCitySerializer
            success_message = "cityname'"+ city_name +"' created."
            print success_message
            return Response({'serializer':serializer,'success_message':success_message,'title':'AddCity'})
