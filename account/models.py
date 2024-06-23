import os
from datetime import datetime
from os.path import splitext
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.dispatch import receiver


def get_timestamp_path(instance, filename):
    return '%s%s' % (datetime.now().timestamp(), splitext(filename)[1])
# Create your models here.
def validate_file_extension(value):
    if not (value.name.endswith('.png') or value.name.endswith('.jpg') or value.name.endswith('.jpeg')):
        raise ValidationError('Недопустимый формат файла. Допускаются только .xls и .pdf файлы.')

class CustomUserModel(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE )
	phone = models.CharField(max_length=20, verbose_name='Номер телефона', null=True, blank=True)
	birthdate = models.DateField(db_index=True, verbose_name='Дата рождения')
	photo = models.ImageField(default='default.jpg', upload_to=get_timestamp_path, validators=[validate_file_extension], verbose_name='Фото')
	confirmation_send_date = models.DateField(db_index=True, verbose_name='Дата запроса подтверждения')
	is_confirmed = models.BooleanField(default=False, verbose_name='Подтверждение регистрации')
	
	def __str__(self):
		return self.user.username
	
	class Meta:
		verbose_name_plural = 'Пользователи'
		verbose_name = 'Пользователь'
		ordering = ['user']


@receiver(post_save, sender=CustomUserModel)
def send_confirmation_notification(sender, instance, **kwargs):
	if kwargs.get('created', False):
		print('Пользователь создан, но еще не подтвержден')
		return
	
	if instance.is_confirmed and not CustomUserModel.objects.filter(pk=instance.pk, is_confirmed=False).exists():
		print('Пользователь аутентифицирован и его аккаунт только что был активирован.')
