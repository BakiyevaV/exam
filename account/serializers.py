from datetime import date

from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from .models import CustomUserModel
from echoverse.models import MessagesSettings
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'password')

class CutUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username',)

class SaveUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name')

class CustUserSerializer(serializers.ModelSerializer):
    user = SaveUserSerializer()
    class Meta:
        model = CustomUserModel
        fields = ('birthdate', 'phone', 'photo', 'user')
 
class ActivateSerializer(serializers.ModelSerializer):
    user = CutUserSerializer()
    class Meta:
        model = CustomUserModel
        fields = ('is_confirmed', 'user')
class CustomUserSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    class Meta:
        model = CustomUserModel
        fields = ('birthdate', 'user')
    
    def validate(self, data):
        user_data = data.get('user')
        if user_data:
            password = user_data.get('password')
            if len(password) < 8:
                raise serializers.ValidationError({
                    'user': {
                        'password': 'Пароль должен быть не менее 8 символов.'
                    }
                })
            if not any(char.isdigit() for char in password):
                raise serializers.ValidationError({
                    'user': {
                        'password': 'Пароль должен содержать хотя бы одну цифру.'
                    }
                })
            if not any(char.isupper() for char in password):
                raise serializers.ValidationError({
                    'user': {
                        'password': 'Пароль должен содержать хотя бы одну заглавную букву.'
                    }
                })
            users1 = User.objects.filter(email=user_data.get('email'))
            if len(users1) > 0:
                raise serializers.ValidationError({
                    'user': {
                        'email': 'Пользователь с таким адресом электронной почты уже существует'
                    }
                })

        return data
    
    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user_data['password'] = make_password(user_data['password'])
        user = User.objects.create(**user_data)
        current_date = date.today()
        custom_user = CustomUserModel.objects.create(user=user, confirmation_send_date=current_date, **validated_data)
        MessagesSettings.objects.create(user=custom_user)
        return custom_user

    
    def update(self, instance, validated_data):
        pass
class UserActivationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUserModel
        fields = ['is_confirmed']
        read_only_fields = ['is_confirmed']
    
    def update(self, instance, validated_data):
        instance.is_confirmed = True
        instance.save()
        return instance