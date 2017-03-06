#import modules
from rest_framework import serializers
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.contrib.auth.hashers import make_password

#import models for further ModelSerializer
from django.contrib.auth.models import User
from .models import WeatherId

#LoginSerializer for login page,two feature needed for login- username,password
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=100, required=True, style={'placeholder': 'Username'})
    password = serializers.CharField(max_length=100, required=True, style={'input_type': 'Password', 'placeholder': 'Password'})

#RegisterSerializer for register page.username,email,password and confirm password is needed
#user model is used for it,that accessed by meta class,and four field of model-id,username,email,password
class RegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=100, required=True, style={'placeholder': 'Username'})
    email = serializers.EmailField(max_length=100, required=True, style={'placeholder': 'Email'})
    password = serializers.CharField(max_length=100, required=True, style={'input_type': 'password', 'placeholder': 'Password', 'id':'password'})
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')
#create function check that particular user exist or not and password validate
    def create(self, validated_data):
        username = validated_data['username']
        if User.objects.filter(username=username).count():
            error = "Username "+ username +" already exist."
            raise serializers.ValidationError(error)

        password = validated_data.pop('password', None)
        if password is not None:
            password = make_password(password, salt=None, hasher='default')
            validated_data.update({'password':password})
        else:
            validated_data.update({'password':''})
        return User.objects.create(**validated_data)

#ProfileSerializer for profie page ,accesses user database
class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=100, required=True, style={'placeholder': 'Username', 'read_only':True})
    email = serializers.EmailField(max_length=100, required=True, style={'placeholder': 'Email'})
    first_name = serializers.CharField(max_length=100, required=True, style={'placeholder': 'First name'})
    last_name = serializers.CharField(max_length=100, required=True, style={'placeholder': 'Last name'})

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name')
#update function updates chabged entries
    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.save()
        return instance


#AddCitySerializer for adding new stationId,store in weatherId model,accessing id and stationId
class AddCitySerializer(serializers.ModelSerializer):
    stationId = serializers.CharField(max_length=100, required=True, style={'placeholder': 'stationId'})

    class Meta:
        model = WeatherId
        fields = ('id', 'stationId')
