from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from .models import ArticleImage, Articles, Emotions, EmotionImage, LikesModel, ViewsModel, SubscriptionModel, \
    IgnoreModel, MessagesSettings, UserInquiry


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
        images = [ArticleImage.objects.get_or_create(article=article, image=image_data) for image_data in images_data if image_data]
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
        user = self.context['request'].user
        validated_data['author'] = user
        tags = validated_data.pop('tags', [])
        tags = tags[0].split(",") if tags else []
        validated_data['tags'] = tags
        article = Articles.objects.create(**validated_data)
        if tags:
            article.tags = tags
            article.save()
        return article
    
    def update(self, instance, validated_data):
        user = self.context['request'].user
        validated_data['author'] = user
        
        tags = validated_data.pop('tags', [])
        tags = tags[0].split(",") if tags else []
        
        instance.title = validated_data.get('title', instance.title)
        instance.content = validated_data.get('content', instance.content)
        instance.category = validated_data.get('category', instance.category)
        
        if tags:
            instance.tags = tags  # assuming tags is a ManyToMany field
        instance.save()
        
        return instance


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
        
class InquiriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserInquiry
        fields = [ 'subject', 'message', 'is_resolved']
    
        
        