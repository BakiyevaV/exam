from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from .models import ArticleImage, Articles, Emotions, EmotionImage, LikesModel, ViewsModel, SubscriptionModel, \
    IgnoreModel, MessagesSettings


class ArticleImageSerializer(serializers.ModelSerializer):
    images = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False,
        allow_empty=True
    )

    class Meta:
        model = ArticleImage
        fields = ['images']

    def create(self, validated_data):
        images_data = validated_data.get('images', [])
        article_pk = self.context.get('pk')
        article = get_object_or_404(Articles, pk=article_pk)
        images = [ArticleImage.objects.create(article=article, image=image_data) for image_data in images_data if image_data]
        return images
class ArticleSerializer(serializers.ModelSerializer):
    tags = serializers.ListField(
        child=serializers.CharField(max_length=100, allow_blank=True, allow_null=True),
        required=False,
        allow_empty=True
    )
    
    class Meta:
        model = Articles
        fields = ['id', 'title', 'content', 'category', 'tags']
    
    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        tags = validated_data['tags']
        tags = tags[0].split(",")
        validated_data['tags'] = tags
        article = Articles.objects.create(**validated_data)
        if tags:
            article.tags = tags
            article.save()
        return article


class EmotionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Emotions
        fields = ['article', 'user', 'emotion_type']

    def create(self, validated_data):
        try:
            print('create')
            return Emotions.objects.create(**validated_data)
        except IntegrityError:
            print('IntegrityError')
            Emotions.objects.filter(**validated_data).delete()
            raise serializers.ValidationError("Duplicate data. The existing record has been deleted.")

class LikesSerializer(serializers.ModelSerializer):
    class Meta:
        model = LikesModel
        fields = ['article', 'user']

class ViewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ViewsModel
        fields = ['article', 'user']
        
class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionModel
        fields = ['user', 'informator']
        
class IgnoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = IgnoreModel
        fields = ['user', 'ignored_user']

class MessagesSettingsSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = MessagesSettings
        fields = ['user', 'send_messages', 'send_notification']
        
        