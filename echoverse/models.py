from datetime import datetime
from os.path import splitext
from django.core.exceptions import ValidationError
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.conf import settings
from django.contrib.postgres.search import SearchVector

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



