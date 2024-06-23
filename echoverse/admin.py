from django.contrib import admin
from .models import Categories, Articles, EmotionImage, Emotions, NotificationCategories, Notifications

# Register your models here.
admin.site.register(Categories)
admin.site.register(Articles)
admin.site.register(EmotionImage)
admin.site.register(Emotions)
admin.site.register(NotificationCategories)
admin.site.register(Notifications)