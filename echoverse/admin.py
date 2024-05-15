from django.contrib import admin
from .models import Categories, Articles, EmotionImage, Emotions

# Register your models here.
admin.site.register(Categories)
admin.site.register(Articles)
admin.site.register(EmotionImage)
admin.site.register(Emotions)