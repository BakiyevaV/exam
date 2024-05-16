import os
import json
from datetime import datetime

from django.contrib import messages

from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from rest_framework import generics, status
from rest_framework.generics import RetrieveAPIView, RetrieveUpdateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response

from .forms import UserInfoForm, CustUserInfoForm
from .models import CustomUserModel
from .serializers import UserSerializer, CustomUserSerializer, UserActivationSerializer, ActivateSerializer, \
	CustUserSerializer
from django.template.loader import render_to_string
from django.core.mail import EmailMessage, get_connection, send_mail
from django.conf import settings
from django.http import JsonResponse, HttpResponseRedirect, Http404
from django.shortcuts import redirect
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from django.http import HttpResponse
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
import logging


logger = logging.getLogger(__name__)

# Create your views here.

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

class RegisterApi(generics.CreateAPIView):
	queryset = CustomUserModel.objects.all()
	serializer_class = CustomUserSerializer

	def perform_create(self, serializer):
		user = serializer.save()
		self.send_confirmation_email(user)
	def send_confirmation_email(self, custom_user):
		user = custom_user.user
		print(user)
		context = {'user': user.username, 'pk': user.pk}
		print(context)
		print(user.email)
		letter = render_to_string('email/registration_letter.html', context)
		print(letter)
		try:
			send_mail(
				subject='Оповещение',
				message=letter,
				from_email=settings.DEFAULT_FROM_EMAIL,
				recipient_list=[user.email],
				html_message=letter,
				fail_silently=False,
			)
			print("Письмо успешно отправлено.")
		except Exception as e:
			print("Ошибка при отправке письма:", e)


class ConfirmApi(generics.RetrieveUpdateAPIView):
	queryset = CustomUserModel.objects.all()
	serializer_class = UserActivationSerializer
	permission_classes = [AllowAny]
	
	def update(self, request, *args, **kwargs):
		instance = self.get_object()
		instance.is_confirmed = True
		instance.save()
		serializer = self.get_serializer(instance)
		return JsonResponse({'success': 'Account activated'}, status=200)
	
	def get_object(self):
		user_id = self.kwargs.get('pk')
		return get_object_or_404(CustomUserModel, user__id=user_id)
	
	
def activated(request, pk):
	return render(request, 'account/activated.html')


class GetUserData(APIView):
	def post(self, request, *args, **kwargs):
		username = request.data.get('username')
		password = request.data.get('password')
		user = authenticate(username=username, password=password)
		if user:
			try:
				custom_user = user.customusermodel
				if custom_user.is_confirmed:
					serializer = CustomUserSerializer(custom_user)
					return Response({'data': serializer.data}, status=status.HTTP_200_OK)
				else:
					print('Account is not confirmed.')
					return Response({'data': 'False'}, status=status.HTTP_200_OK)
			except CustomUserModel.DoesNotExist:
				return Response({'error': 'No associated custom user data found.'}, status=status.HTTP_404_NOT_FOUND)
		else:
			return Response({'error': 'Invalid username or password.'}, status=status.HTTP_401_UNAUTHORIZED)
		
		
class DownloadPDFView(APIView):
	permission_classes = [AllowAny]

	def get(self, request):
		file_path = os.path.join('media', 'rules.pdf')
		with open(file_path, 'rb') as pdf:
			response = HttpResponse(pdf.read(), content_type='application/pdf')
			response['Content-Disposition'] = 'attachment; filename="rules.pdf"'
		return response
		
		
class AuthenticateUserView(APIView):

	def post(self, request):
		data = json.loads(request.body)
		password = data.get('password')
		username = data.get('username')
		current_user = authenticate(username=username, password=password)
		print("current_user", current_user)
		if current_user:
			return JsonResponse({'success': current_user.pk}, status=200)
		else:
			return JsonResponse({'error': 'No such User'}, status=status.HTTP_401_UNAUTHORIZED)
		
def login_view(request):
	if request.method == 'POST':
		username = request.POST.get('username')
		password = request.POST.get('password')
		if username and password:
			current_user = authenticate(username=username, password=password)
			print(current_user)
			if current_user:
				login(request, current_user)
				return redirect('echo:index')
			
			
def logout_view(request):
	print('выхожу',request.user)
	logout(request)
	return redirect('echo:index')

def get_private(request, pk):
	custom_user = get_object_or_404(CustomUserModel, user__id=pk)
	user = custom_user.user
	if request.method == 'POST':
		form1 = UserInfoForm(request.POST, instance=custom_user)
		form2 = CustUserInfoForm(request.POST, request.FILES, instance=user)
		if form1.is_valid() and form2.is_valid():
			f_name = form1.cleaned_data.get('first_name')
			l_name = form1.cleaned_data.get('last_name')
			user.first_name = f_name
			user.last_name = l_name
			user.save()
			phone = form2.cleaned_data.get('phone')
			photo = form2.cleaned_data.get('photo')
			custom_user.phone = phone
			custom_user.photo = photo
			custom_user.save()
			messages.success(request, 'Your data has been successfully saved.')
			return redirect(reverse_lazy('echo:index'))
		else:
			messages.error(request, 'There were errors in the form. Please correct them.')
			return render(request, 'account/private_info.html', {'form1': form1, 'form2': form2})
	else:
		form1 = UserInfoForm(instance=custom_user.user)
		form2 = CustUserInfoForm(instance=custom_user)
	return render(request, 'account/private_info.html', {'form1': form1, 'form2': form2, 'custom_user': custom_user,
														 'user': user})


class SaveUserInfoApi(APIView):
	serializer_class = CustUserSerializer
	parser_classes = [MultiPartParser]
	permission_classes = [IsAuthenticated]

	def get_object(self, pk):
		try:
			return CustomUserModel.objects.get(pk=pk)
		except CustomUserModel.DoesNotExist:
			raise Http404
	
	def patch(self, request, pk):
		print("Before get_object")
		instance = self.get_object(pk)
		print("After get_object:", instance)
		print("Body before parsing:", request.body)
		print("Data:", request.data)
		serializer = CustUserSerializer(instance, data=request.data, partial=True)
		if serializer.is_valid():
			serializer.save()
			return Response({'success': 'Saved'}, status=status.HTTP_200_OK)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
	

