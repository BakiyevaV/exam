from django import forms
from django.forms import ModelForm
from django.contrib.auth.models import User
from account.models import CustomUserModel

class UserInfoForm(ModelForm):
	class Meta:
		model = User
		fields = ('first_name', 'last_name')


class CustUserInfoForm(ModelForm):
	class Meta:
		model = CustomUserModel
		fields = ('phone', 'photo')
		widgets = {
			'birthdate': forms.DateInput(attrs={'type': 'date'})
		}
		

	
		