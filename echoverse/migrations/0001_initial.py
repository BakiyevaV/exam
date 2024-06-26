# Generated by Django 5.0.5 on 2024-06-16 14:53

import django.contrib.postgres.fields
import django.db.models.deletion
import echoverse.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('account', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Categories',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=40, unique=True, verbose_name='Наименование категории')),
            ],
            options={
                'verbose_name': 'Категория',
                'verbose_name_plural': 'Категории',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='EmotionImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Название эмоции')),
                ('image_path', models.CharField(max_length=100, verbose_name='Путь к изображению')),
            ],
            options={
                'verbose_name': 'Смайлы',
                'verbose_name_plural': 'Смайл',
            },
        ),
        migrations.CreateModel(
            name='NotificationCategories',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=100, unique=True, verbose_name='Наименование категории')),
            ],
            options={
                'verbose_name': 'Категория уведомления',
                'verbose_name_plural': 'Категории уведомлений',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Articles',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, unique=True, verbose_name='Наименование публикации')),
                ('content', models.TextField(verbose_name='Текст публикации')),
                ('published_date', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Опубликовано')),
                ('updated', models.DateTimeField(auto_now=True, db_index=True, verbose_name='Обновлено')),
                ('tags', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=100, verbose_name='Теги'), blank=True, null=True, size=None)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Автор')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='echoverse.categories', verbose_name='Категория')),
            ],
            options={
                'verbose_name': 'Публикация',
                'verbose_name_plural': 'Публикации',
                'ordering': ['published_date'],
            },
        ),
        migrations.CreateModel(
            name='ArticleImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to=echoverse.models.get_timestamp_path, verbose_name='Изображение')),
                ('article', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='echoverse.articles', verbose_name='Публикация')),
            ],
            options={
                'verbose_name': 'Изображение',
                'verbose_name_plural': 'Изображения',
            },
        ),
        migrations.CreateModel(
            name='Comments',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField(verbose_name='Комментарий')),
                ('created', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Создано')),
                ('updated', models.DateTimeField(auto_now=True, db_index=True, verbose_name='Обновлено')),
                ('visibility', models.BooleanField(default=False, verbose_name='Показывать')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comment_author', to=settings.AUTH_USER_MODEL, verbose_name='Автор')),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='children', to='echoverse.comments', verbose_name='Родитель')),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='post_comment', to='echoverse.articles', verbose_name='Комментарий')),
            ],
            options={
                'verbose_name': 'Комментарии',
                'verbose_name_plural': 'Комментарий',
            },
        ),
        migrations.CreateModel(
            name='MessagesSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('send_messages', models.BooleanField(default=True, verbose_name='Получать сообщения')),
                ('send_notification', models.BooleanField(default=True, verbose_name='Получать уведомления')),
                ('user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='account.customusermodel', verbose_name='Получатель')),
            ],
        ),
        migrations.CreateModel(
            name='Notifications',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='Заголовок')),
                ('notification_text', models.TextField(verbose_name='Текст уведомления')),
                ('send', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Отправлено')),
                ('category', models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, to='echoverse.notificationcategories', verbose_name='Категория')),
                ('recipient', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL, verbose_name='Получатель')),
            ],
            options={
                'verbose_name': 'Уведомления',
                'verbose_name_plural': 'Уведомление',
            },
        ),
        migrations.CreateModel(
            name='Emotions',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('article', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='echoverse.articles', verbose_name='Статья')),
                ('emotion_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='echoverse.emotionimage', verbose_name='Тип эмоции')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Эмоция',
                'verbose_name_plural': 'Эмоции',
                'unique_together': {('article', 'user', 'emotion_type')},
            },
        ),
        migrations.CreateModel(
            name='IgnoreModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ignored_time', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Игнорируется с')),
                ('ignored_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ignored_by', to=settings.AUTH_USER_MODEL, verbose_name='Игнорируемый')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ignoring', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Игнорируемый пользователь',
                'verbose_name_plural': 'Игнорируемые пользователи',
                'unique_together': {('user', 'ignored_user')},
            },
        ),
        migrations.CreateModel(
            name='LikesModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('like_time', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Поставил лайк')),
                ('article', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='echoverse.articles', verbose_name='Статья')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Лайки',
                'verbose_name_plural': 'Лайк',
                'unique_together': {('article', 'user')},
            },
        ),
        migrations.CreateModel(
            name='SavesModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('saved_time', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Сохранено')),
                ('article', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='echoverse.articles', verbose_name='Статья')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Подписчик')),
            ],
            options={
                'verbose_name': 'Сохранения',
                'verbose_name_plural': 'Сохранение',
                'unique_together': {('article', 'user')},
            },
        ),
        migrations.CreateModel(
            name='SubscriptionModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sub_time', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Подписался')),
                ('informator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subscribers', to=settings.AUTH_USER_MODEL, verbose_name='Информатор')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subscriptions', to=settings.AUTH_USER_MODEL, verbose_name='Подписчик')),
            ],
            options={
                'verbose_name': 'Подписка',
                'verbose_name_plural': 'Подписки',
                'unique_together': {('user', 'informator')},
            },
        ),
        migrations.CreateModel(
            name='ViewsModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('view_time', models.DateTimeField(auto_now=True, db_index=True, verbose_name='Просмотрено')),
                ('article', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='echoverse.articles', verbose_name='Статья')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Просмотры',
                'verbose_name_plural': 'Просмотр',
                'unique_together': {('article', 'user')},
            },
        ),
    ]
