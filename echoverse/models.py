from datetime import datetime
from os.path import splitext
from django.core.exceptions import ValidationError
from django.contrib.postgres.fields import ArrayField
from django.core.mail import send_mail
from django.db import models
from django.conf import settings
from django.contrib.postgres.search import SearchVector
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.contrib.auth.models import User
from django.templatetags.static import static
from django.template.loader import render_to_string

from account.models import CustomUserModel
def get_timestamp_path(instance, filename):
    return '%s%s' % (datetime.now().timestamp(), splitext(filename)[1])
# Create your models here.
def validate_file_extension(value):
    if not (value.name.endswith('.png') or value.name.endswith('.jpg') or value.name.endswith('.jpeg')):
        raise ValidationError('Недопустимый формат файла. Допускаются только .xls и .pdf файлы.')

class Categories(models.Model):
	name = models.CharField(max_length=40, db_index=True, verbose_name='Наименование категории', unique=True)
	
	def __str__(self):
		return self.name
	
	class Meta:
		verbose_name_plural = 'Категории'
		verbose_name = 'Категория'
		ordering = ['name']


class Articles(models.Model):
	title = models.CharField(max_length=200, verbose_name="Наименование публикации", unique=True)
	author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Автор")
	content = models.TextField(verbose_name="Текст публикации")
	published_date = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name="Опубликовано")
	updated = models.DateTimeField(auto_now=True, db_index=True, verbose_name="Обновлено")
	category = models.ForeignKey('Categories', on_delete=models.PROTECT, verbose_name="Категория")
	tags = ArrayField(models.CharField(max_length=100, verbose_name="Теги"), blank=True, null=True)


	def __str__(self):
		return self.title

	class Meta:
		verbose_name_plural = 'Публикации'
		verbose_name = 'Публикация'
		ordering = ['published_date']
		
		
class ArticleImage(models.Model):
	article = models.ForeignKey(Articles, related_name='images', on_delete=models.CASCADE, verbose_name="Публикация")
	image = models.ImageField(upload_to=get_timestamp_path, verbose_name="Изображение")
	
	def __str__(self):
		return f"Image for {self.article.title}"
	
	class Meta:
		verbose_name = "Изображение"
		verbose_name_plural = "Изображения"
	

class EmotionImage(models.Model):
	name = models.CharField(max_length=100, verbose_name="Название эмоции")
	image_path = models.CharField(max_length=100, verbose_name="Путь к изображению")
	
	class Meta:
		verbose_name = "Смайлы"
		verbose_name_plural = "Смайл"
	
	def __str__(self):
		return self.name


class Emotions(models.Model):
	article = models.ForeignKey('Articles', on_delete=models.CASCADE, verbose_name="Статья")
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Пользователь")
	emotion_type = models.ForeignKey('EmotionImage', on_delete=models.CASCADE, verbose_name="Тип эмоции")
	
	class Meta:
		verbose_name = "Эмоция"
		verbose_name_plural = "Эмоции"
		unique_together = ('article', 'user', 'emotion_type')
	
	def __str__(self):
		return f"{self.user} - {self.emotion_type} - {self.article}"


class LikesModel(models.Model):
	article = models.ForeignKey('Articles', on_delete=models.CASCADE, verbose_name="Статья")
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Пользователь")
	like_time = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name="Поставил лайк")
	
	class Meta:
		verbose_name = "Лайки"
		verbose_name_plural = "Лайк"
		unique_together = ('article', 'user')
	
	def __str__(self):
		return f"{self.user} - {self.article}"

class ViewsModel(models.Model):
	article = models.ForeignKey('Articles', on_delete=models.CASCADE, verbose_name="Статья")
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Пользователь")
	view_time = models.DateTimeField(auto_now=True, db_index=True, verbose_name="Просмотрено")
	
	class Meta:
		verbose_name = "Просмотры"
		verbose_name_plural = "Просмотр"
		unique_together = ('article', 'user')
	
	def __str__(self):
		return f"{self.user} - {self.article}"


class Comments(models.Model):
	parent = models.ForeignKey('self', verbose_name="Родитель", on_delete=models.SET_NULL,
							   blank=True, null=True, related_name='children')
	post = models.ForeignKey(Articles, related_name='post_comment', on_delete=models.CASCADE,
							 verbose_name='Комментарий')
	content = models.TextField('Комментарий')
	author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='comment_author', on_delete=models.CASCADE,
							   verbose_name='Автор')
	created = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name="Создано")
	updated = models.DateTimeField(auto_now=True, db_index=True, verbose_name="Обновлено")
	visibility = models.BooleanField(default=False, verbose_name="Показывать")
	
	class Meta:
		verbose_name = "Комментарии"
		verbose_name_plural = "Комментарий"
	
	def __str__(self):
		return f"{self.author} - {self.content}"


class NotificationCategories(models.Model):
	name = models.CharField(max_length=100, db_index=True, verbose_name='Наименование категории', unique=True)
	def __str__(self):
		return self.name
	class Meta:
		verbose_name_plural = 'Категории уведомлений'
		verbose_name = 'Категория уведомления'
		ordering = ['name']

class Notifications(models.Model):
	category = models.ForeignKey('NotificationCategories', default=1, on_delete=models.PROTECT, verbose_name="Категория")
	recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, verbose_name="Получатель")
	title = models.CharField(max_length=200, verbose_name="Заголовок")
	notification_text = models.TextField(verbose_name="Текст уведомления")
	send = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name="Отправлено")
	
	class Meta:
		verbose_name = "Уведомления"
		verbose_name_plural = "Уведомление"
	def __str__(self):
		return f"{self.recipient} - {self.title}"
	
class MessagesSettings(models.Model):
	user = models.OneToOneField(CustomUserModel, on_delete=models.CASCADE, verbose_name="Получатель", blank=True, null=True)
	send_messages = models.BooleanField(default=True, verbose_name="Получать сообщения")
	send_notification = models.BooleanField(default=True, verbose_name="Получать уведомления")


class SavesModel(models.Model):
	article = models.ForeignKey('Articles', on_delete=models.CASCADE, verbose_name="Статья")
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Подписчик")
	saved_time = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name="Сохранено")
	
	class Meta:
		verbose_name = "Сохранения"
		verbose_name_plural = "Сохранение"
		unique_together = ('article', 'user')
	
	def __str__(self):
		return f"{self.user} - {self.article}"


class SubscriptionModel(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Подписчик",
		related_name="subscriptions")
	informator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Информатор",
		related_name="subscribers")
	sub_time = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name="Подписался")
	
	class Meta:
		verbose_name = "Подписка"
		verbose_name_plural = "Подписки"
		unique_together = ('user', 'informator')
	
	def __str__(self):
		return f"{self.user} - {self.informator}"


class IgnoreModel(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Пользователь",
        related_name="ignoring")
    ignored_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Игнорируемый",
        related_name="ignored_by")
    ignored_time = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name="Игнорируется с")

    class Meta:
        verbose_name = "Игнорируемый пользователь"
        verbose_name_plural = "Игнорируемые пользователи"
        unique_together = ('user', 'ignored_user')

    def __str__(self):
        return f"{self.user} - {self.ignored_user}"


@receiver(post_save, sender=Articles)
def send_confirmation_notification(sender, instance, created, **kwargs):
	if created:
		author = instance.author
		subscribers = SubscriptionModel.objects.filter(informator=author)
		category = NotificationCategories.objects.get(pk=1)
		
		emails = []
		for sub in subscribers:
			settings = MessagesSettings.objects.filter(user=sub.user).first()
			if settings and settings.send_messages and sub.user.email:
				emails.append(sub.user.email)
				
		article_url = reverse("echo:article_detail", args=[instance.pk])  # или используйте метод reverse для генерации URL
		
		if emails:
			send_mail(
				subject='Новая публикация от вашего автора',
				message=f'Привет! {author.username} только что опубликовал новую статью: "<a href="{article_url}">{instance.title}</a>". Приятного чтения!',
				from_email=settings.DEFAULT_FROM_EMAIL,
				recipient_list=emails,
				fail_silently=False,
			)
		
		for sub in subscribers:
			settings = MessagesSettings.objects.filter(user=sub.user).first()
			if settings and settings.send_notification:
				Notifications.objects.create(
					category=category,
					recipient=sub.user,
					title='Новая публикация от вашего автора',
					notification_text=f'Привет! {author.username} только что опубликовал новую статью: "<a href="{article_url}">{instance.title}</a>". Приятного чтения!',
				)
			
			
@receiver(post_save, sender=LikesModel)
def send_likes_notification(sender, instance, created, **kwargs):
	if created:
		user = instance.user
		author = instance.article.author
		category = NotificationCategories.objects.get(pk=2)
		author_custom_instance = CustomUserModel.objects.get(user=author)
		author_settings = MessagesSettings.objects.get(user=author_custom_instance)

		if author_settings.send_notification:
			Notifications.objects.create(
				category=category,
				recipient=author,
				title='Вашу статью лайкнули',
				notification_text=f'Пользователь {user.username} лайкнул вашу статью "{instance.article.title}".'
			)

		if author_settings.send_messages and author_custom_instance.user.email:
			send_mail(
				subject='Вашу статью лайкнули',
				message=f'Привет! Пользователь {user.username} лайкнул вашу статью "{instance.article.title}".',
				from_email=settings.DEFAULT_FROM_EMAIL,
				recipient_list=[author_custom_instance.user.email],
				fail_silently=False,
			)
			
@receiver(post_save, sender=Emotions)
def send_emotions_notification(sender, instance, created, **kwargs):
	if created:
		user = instance.user
		author = instance.article.author
		category = NotificationCategories.objects.get(pk=3)
		author_custom_instance = CustomUserModel.objects.get(user=author)
		author_settings = MessagesSettings.objects.get(user=author_custom_instance)
		emotion_type = instance.emotion_type
		emotion_path = static(emotion_type.image_path)

		if author_settings.send_notification:
			Notifications.objects.create(
				category=category,
				recipient=author,
				title='Под вашей статьей оставили реакцию',
				notification_text=f'Пользователь {user.username} оставил реакцию <img style="width: 30px; height: 30px;" src="{ emotion_path }"> под публикацией: "{instance.article.title}".'
			)

		if author_settings.send_messages and author_custom_instance.user.email:
			context = {'user': user.username, 'article': instance.article.title, 'subject': 'Под вашей статьей оставили реакцию',
					'email_text': f'Пользователь {user.username} оставил реакцию <img style="width: 30px; height: 30px;" src="{ emotion_path }"> под публикацией: "{instance.article.title}".'  }
			letter = render_to_string('email/emotions_letter.html', context)
			send_mail(
				subject=context['subject'],
				message=letter,
				from_email=settings.DEFAULT_FROM_EMAIL,
				recipient_list=[author_custom_instance.user.email],
				html_message=letter,
				fail_silently=False,
			)
			
@receiver(post_save, sender=Comments)
def send_comments_notification(sender, instance, created, **kwargs):
	if created:
		user = instance.author
		author = instance.post.author
		category = NotificationCategories.objects.get(pk=4)
		author_custom_instance = CustomUserModel.objects.get(user=author)
		author_settings = MessagesSettings.objects.get(user=author_custom_instance)
		parent = instance.parent
		
		print(user)
		print(author)
		print(author_custom_instance)
		print(author_settings)

		if author_settings.send_notification and not parent:
			if author != user:
				Notifications.objects.create(
					category=category,
					recipient=author,
					title='Под вашей статьей оставили комментарий',
					notification_text=f'Пользователь {user.username} оставил комментарий под публикацией: "{instance.post.title}".'
				)
		elif author_settings.send_notification and parent:
			if instance.parent.author:
				Notifications.objects.create(
					category=category,
					recipient=instance.parent.author,
					title='Под вашим комментарием оставили комментарий',
					notification_text=f'Пользователь {user.username} оставил комментарий к вашему комментарию под публикацией: "{instance.post.title}".'
				)
			
			
		#
		# if author_settings.send_messages and author_custom_instance.user.email:
		# 	context = {'user': user.username, 'article': instance.article.title, 'subject': 'Под вашей статьей оставили реакцию',
		# 			'email_text': f'Пользователь {user.username} оставил реакцию <img style="width: 30px; height: 30px;" src="{ emotion_path }"> под публикацией: "{instance.article.title}".'  }
		# 	letter = render_to_string('email/emotions_letter.html', context)
		# 	send_mail(
		# 		subject=context['subject'],
		# 		message=letter,
		# 		from_email=settings.DEFAULT_FROM_EMAIL,
		# 		recipient_list=[author_custom_instance.user.email],
		# 		html_message=letter,
		# 		fail_silently=False,
		# 	)
		