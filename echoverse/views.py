from datetime import timedelta
from django.db.models import Q, F
from django.contrib.postgres.search import TrigramSimilarity

from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.db.models.functions import Greatest
from django.forms import inlineformset_factory
from django.http import HttpResponseRedirect
from django.utils import timezone
from django.shortcuts import render, redirect,get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, FormView, DetailView, ListView, UpdateView
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from echoverse.forms import ArticleForm, ImageForm, CommentForm, SavesForm
from echoverse.models import Articles, EmotionImage, Emotions, LikesModel, ViewsModel, Comments, SavesModel, Categories, \
    SubscriptionModel, IgnoreModel, Notifications, MessagesSettings, UserInquiry, ArticleImage
from .serializers import ArticleSerializer, ArticleImageSerializer, EmotionsSerializer, LikesSerializer, \
    ViewsSerializer, SubscriptionSerializer, IgnoreSerializer, MessagesSettingsSerializer, InquiriesSerializer
from django.db.models import Count
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from account.models import CustomUserModel
from django.contrib.auth.mixins import UserPassesTestMixin


def index(request):
    if request.user.is_authenticated:
        ignored_authors_ids = IgnoreModel.objects.filter(
            user=request.user
        ).values_list('ignored_user_id', flat=True)
        
        article_list = Articles.objects.exclude(
            author_id__in=ignored_authors_ids
        ).annotate(
            comments_count=Count('post_comment', distinct=True),
            views_count=Count('views', distinct=True)
        )
    else:
        article_list = Articles.objects.annotate(
            comments_count=Count('post_comment'),
            views_count=Count('views')
        )
    emojies = EmotionImage.objects.all()

    if request.user.is_authenticated:
        likes = LikesModel.objects.filter(user=request.user).values_list('article_id', flat=True)
        liked_articles = set(likes)
        saves = SavesModel.objects.filter(user=request.user).values_list('article_id', flat=True)
        saved_articles = set(saves)
        subscriptions_list = SubscriptionModel.objects.filter(user=request.user).values_list('informator', flat=True)
        subscriptions = set(subscriptions_list)
        ignore_list = IgnoreModel.objects.filter(user=request.user).values_list('ignored_user', flat=True)
        ignores = set(ignore_list)
    else:
        liked_articles = set()
        saved_articles = set()
        subscriptions = set()
        ignores = set()

    emotions_count = {}
    for article in article_list:
        emotions_count[article.id] = {}
        for emoji in emojies:
            count = Emotions.objects.filter(article=article, emotion_type=emoji).count()
            emotions_count[article.id][emoji.name] = count
    
    paginator = Paginator(article_list, 6)
    page = request.GET.get('page')
    pages_num = range(1, paginator.num_pages + 1)
    try:
        articles = paginator.page(page)
    except PageNotAnInteger:
        articles = paginator.page(1)
    except EmptyPage:
        articles = paginator.page(paginator.num_pages)
    
    
    context = {
        'is_authenticated': request.user.is_authenticated,
        'articles': articles,
        'emojies': emojies,
        'emotions_count': emotions_count,
        'liked_articles': liked_articles,
        'saved_articles': saved_articles,
        'pages_num': pages_num,
        'subscriptions': subscriptions,
        'ignores': ignores,
    }
    return render(request, 'echo/index.html', context)
    
    
class CreateArticleView(FormView):
    model = Articles
    form_class = ArticleForm
    template_name = 'echo/create_article.html'
    success_url = reverse_lazy('echo:index')
    print('CreateArticleView')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'image_form' not in context:
            context['image_form'] = ImageForm()
        return context
    
    # def post(self, request, *args, **kwargs):
    #     self.object = None
    #     form = self.get_form()
    #     image_form = ImageForm(request.POST, request.FILES)
    #     if form.is_valid() and image_form.is_valid():
    #         return self.form_valid(form, image_form)
    #     else:
    #         return self.form_invalid(form, image_form)
    #
    # def form_valid(self, form, image_form):
    #     self.object = form.save()
    #     image_form.instance.article = self.object
    #     image_form.save()
    #     return redirect(self.get_success_url())
    #
    # def form_invalid(self, form, image_form):
    #     return self.render_to_response(self.get_context_data(form=form, image_form=image_form))


class UpdateArticleView(UpdateView):
    model = Articles
    form_class = ArticleForm
    template_name = 'echo/update.html'
    success_url = reverse_lazy('echo:my_articles')
    print('UpdateArticleView')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'image_form' not in context:
            context['image_form'] = ImageForm()
        article = self.get_object()
        context['tags'] = article.tags
        context['images'] = ArticleImage.objects.filter(article=article)
        print('images', context['images'])
        return context
    
    def get_object(self, queryset=None):
        pk = self.kwargs.get('pk')
        return get_object_or_404(Articles, pk=pk)
        
    
    
class ArticleCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, format=None):
        serializer = ArticleSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            article = serializer.save()
            response_serializer = ArticleSerializer(article)
            
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, pk, format=None):
        article = get_object_or_404(Articles, pk=pk)
        print(article)
        serializer = ArticleSerializer(article, data=request.data, context={'request': request})
        if serializer.is_valid():
            article = serializer.save()
            response_serializer = ArticleSerializer(article)
            return Response(response_serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def delete(self, request, pk, format=None):
        article = get_object_or_404(Articles, pk=pk)
        article.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class ArticleImageCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk, format=None):
        serializer = ArticleImageSerializer(data=request.data, context={'request': request, 'pk': pk})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ArticleDetailView(DetailView):
    model = Articles
    template_name = 'echo/detail.html'
    
    def get_queryset(self):
        pk = self.kwargs.get('pk')
        return Articles.objects.filter(pk=self.kwargs.get('pk')).prefetch_related('post_comment__children')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        article = context['object']
        images = article.images.all()  # Используем related_name 'images'
        emojies = EmotionImage.objects.all()
        emotions_count = {}
        for emoji in emojies:
            count = Emotions.objects.filter(article=article, emotion_type=emoji).count()
            emotions_count[emoji.name] = count
        
        if self.request.user.is_authenticated:
            likes = LikesModel.objects.filter(user=self.request.user, article=article).exists()
        else:
            likes = False
            
        if self.request.user.is_authenticated:
            saves = SavesModel.objects.filter(user=self.request.user, article=article).exists()
        else:
            saves = False
            
        views = ViewsModel.objects.filter(article=article).count()
        comments = Comments.objects.filter(post=article)
        comments_count = Comments.objects.filter(post=article).count()
        context['emojies'] = emojies
        context['emotions_count'] = emotions_count
        context['is_liked'] = likes
        context['is_saved'] = saves
        context['views'] = views
        context['comments'] = comments
        context['comments_count'] = comments_count
        context['images'] = images
        print(images)
        return context
def save_article(request, pk, user_id):
    if request.method == 'POST':
        data = request.POST.copy()
        data['article'] = pk
        data['user'] = user_id
        form = SavesForm(data)
        if form.is_valid():
            form.save()
            next_url = request.GET.get('next', reverse_lazy('echo:article_detail', kwargs={'pk': pk}))
            return HttpResponseRedirect(next_url)
        else:
            print.error(form.errors)
    next_url = request.GET.get('next', reverse_lazy('echo:article_detail', kwargs={'pk': pk}))
    return HttpResponseRedirect(next_url)


class EmotionsSaveApi(ModelViewSet):
    queryset = Emotions.objects.all()
    serializer_class = EmotionsSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        data_list = request.data.get('data')
        results = []
        for data in data_list:
            data['user'] = request.user.pk
            try:
                elem = Emotions.objects.get(article=data['article'], user=data['user'],
                                            emotion_type=data['emotion_type'])
            except Emotions.DoesNotExist:
                elem = None
            if elem:
                elem.delete()
                return Response({'message': 'Emotion entry deleted.'}, status=status.HTTP_200_OK)
            serializer = self.get_serializer(data=data)
            if serializer.is_valid():
                try:
                    self.perform_create(serializer)
                    results.append(serializer.data)
                except serializer.ValidationError as e:
                    return Response({"error": str(e)}, status=status.HTTP_409_CONFLICT)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(results, status=status.HTTP_201_CREATED)


class LikeSaveAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk, format=None):
        user = request.user
        try:
            like = LikesModel.objects.get(article_id=pk, user=user)
            like.delete()
            return Response({'message': f'Like on article {pk} by user {user.pk} deleted.'},
                            status=status.HTTP_200_OK)
        except LikesModel.DoesNotExist:
            like = LikesModel.objects.create(article_id=pk, user=user)
            return Response({'message': f'Like on article {pk} by user {user.pk} created.'},
                            status=status.HTTP_201_CREATED)


class ViewSaveAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk, format=None):
        user = request.user
        view, created = ViewsModel.objects.get_or_create(article_id=pk, user=user)  # Используйте get_or_create для избежания дублирования
        serializer = ViewsSerializer(view)  # Создайте экземпляр сериализатора правильно
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def get(self, request, pk, format=None):
        user = request.user
        try:
            view = ViewsModel.objects.get(article_id=pk, user=user)
            serializer = ViewsSerializer(view)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ViewsModel.DoesNotExist:
            return Response({'message': 'true'}, status=status.HTTP_200_OK)
        
        
def save_comment(request, pk):
    if request.method == 'POST':
        data = request.POST.copy()
        data['post'] = pk
        data['author'] = request.user.pk
        form = CommentForm(data)
        if form.is_valid():
            form.save()
            return redirect(reverse_lazy('echo:article_detail', kwargs={'pk': pk}))
        else:
            print(form.errors)
    return redirect(reverse_lazy('echo:article_detail', kwargs={'pk': pk}))
    
def get_top(request):
    articles = Articles.objects.annotate(
        like_count=Count('likes'),
        comments_count=Count('post_comment'),
        views_count=Count('views')).filter(like_count__gt=0).order_by('-like_count')[:20]
    emojies = EmotionImage.objects.all()
    
    if request.user.is_authenticated:
        likes = LikesModel.objects.filter(user=request.user).values_list('article_id', flat=True)
        print('likes', likes)
        liked_articles = set(likes)
        saves = SavesModel.objects.filter(user=request.user).values_list('article_id', flat=True)
        saved_articles = set(saves)
        print('liked_articles',liked_articles)
    else:
        liked_articles = set()
        saved_articles = set()
        print('empty set')
        
    emotions_count = {}
    
    for article in articles:
        emotions_count[article.id] = {}
        for emoji in emojies:
            count = Emotions.objects.filter(article=article, emotion_type=emoji).count()
            emotions_count[article.id][emoji.name] = count
    paginator = Paginator(articles, 10)
    page = request.GET.get('page')
    pages_num = range(1, paginator.num_pages + 1)
    try:
        articles = paginator.page(page)
    except PageNotAnInteger:
        articles = paginator.page(1)
    except EmptyPage:
        articles = paginator.page(paginator.num_pages)
    
    context = {
        'is_authenticated': request.user.is_authenticated,
        'articles': articles,
        'emojies': emojies,
        'emotions_count': emotions_count,
        'liked_articles': liked_articles,
        'saved_articles': saved_articles,
        'pages_num': pages_num,
        'page_title': f"20 публикаций, понравившихся наибольшему количеству пользователей:"
    }
    print(context)
    return render(request, 'echo/index.html', context)


class RecentArticlesView(ListView):
    model = Articles
    template_name = 'echo/index.html'
    context_object_name = 'articles'
    paginate_by = 1
    
    def get_queryset(self):
        now = timezone.now()
        twelve_hours_ago = now - timedelta(hours=12)
        queryset = Articles.objects.annotate(
            like_count=Count('likes'),
            comments_count=Count('post_comment'),
            views_count=Count('views')).filter(updated__gte=twelve_hours_ago).order_by('-updated')
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        articles = context['articles']
        emojies = EmotionImage.objects.all()
        if self.request.user.is_authenticated:
            likes = LikesModel.objects.filter(user=self.request.user).values_list('article_id', flat=True)
            print('likes', likes)
            liked_articles = set(likes)
            saves = SavesModel.objects.filter(user=self.request.user).values_list('article_id', flat=True)
            saved_articles = set(saves)
            print('liked_articles', liked_articles)
        else:
            liked_articles = set()
            saved_articles = set()
            print('empty set')
        
        emotions_count = {}
        
        for article in articles:
            emotions_count[article.id] = {}
            for emoji in emojies:
                count = Emotions.objects.filter(article=article, emotion_type=emoji).count()
                emotions_count[article.id][emoji.name] = count
        
        context.update({
            'is_authenticated': self.request.user.is_authenticated,
            'emojies': emojies,
            'emotions_count': emotions_count,
            'liked_articles': liked_articles,
            'saved_articles': saved_articles,
            'page_title': f"Публикации созданные в течение последних 12 часов:"
        })
        return context


class ByCategory(ListView):
    model = Articles
    template_name = 'echo/index.html'
    context_object_name = 'articles'
    paginate_by = 10
    
    def get_queryset(self):
        category_id = self.kwargs['pk']
        queryset = Articles.objects.annotate(
            like_count=Count('likes'),
            comments_count=Count('post_comment'),
            views_count=Count('views')).filter(category_id=category_id).order_by('-updated')
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_id = self.kwargs['pk']
        if self.request.user.is_authenticated:
            likes = LikesModel.objects.filter(user=self.request.user).values_list('article_id', flat=True)
            context['liked_articles'] = set(likes)
            saves = SavesModel.objects.filter(user=self.request.user).values_list('article_id', flat=True)
            context['saved_articles'] = set(saves)
        else:
            context['liked_articles'] = set()
            context['saved_articles'] = set()
        
        emojies = EmotionImage.objects.all()
        emotions_count = {}
        for article in context['articles']:
            emotions_count[article.id] = {}
            for emoji in emojies:
                count = Emotions.objects.filter(article=article, emotion_type=emoji).count()
                emotions_count[article.id][emoji.name] = count
        
        context['emojies'] = emojies
        context['emotions_count'] = emotions_count
        context['is_authenticated'] = self.request.user.is_authenticated
        context['category'] = Categories.objects.get(pk=category_id)
        context['page_title'] = f"Категория: {Categories.objects.get(pk=category_id)}"
        return context
    
    
class MyArticlesView(ListView):
    model = Articles
    template_name = 'echo/my_articles.html'
    context_object_name = 'articles'
    
    def get_queryset(self):
        queryset = Articles.objects.annotate(
            like_count=Count('likes'),
            comments_count=Count('post_comment'),
            views_count=Count('views')).filter(author=self.request.user).order_by('-updated')
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            likes = LikesModel.objects.filter(user=self.request.user).values_list('article_id', flat=True)
            context['liked_articles'] = set(likes)
        
        emojies = EmotionImage.objects.all()
        emotions_count = {}
        for article in context['articles']:
            emotions_count[article.id] = {}
            for emoji in emojies:
                count = Emotions.objects.filter(article=article, emotion_type=emoji).count()
                emotions_count[article.id][emoji.name] = count
        
        context['emojies'] = emojies
        context['emotions_count'] = emotions_count
        context['is_authenticated'] = self.request.user.is_authenticated
        return context

class MyLikesView(ListView):
    model = Articles
    template_name = 'echo/my_likes.html'
    context_object_name = 'articles'
    
    def get_queryset(self):
        liked_articles_ids = LikesModel.objects.filter(user=self.request.user).values_list('article_id', flat=True)
        queryset = Articles.objects.filter(id__in=liked_articles_ids).annotate(
            like_count=Count('likes'),
            comments_count=Count('post_comment'),
            views_count=Count('views'),
            liked_time=F('likes__like_time')
        ).order_by('-updated')
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            likes = LikesModel.objects.filter(user=self.request.user).values_list('article_id', flat=True)
            context['liked_articles'] = set(likes)
        
        emojies = EmotionImage.objects.all()
        emotions_count = {}
        for article in context['articles']:
            emotions_count[article.id] = {}
            for emoji in emojies:
                count = Emotions.objects.filter(article=article, emotion_type=emoji).count()
                emotions_count[article.id][emoji.name] = count
        
        context['emojies'] = emojies
        context['emotions_count'] = emotions_count
        context['is_authenticated'] = self.request.user.is_authenticated
        return context


class MySavesView(ListView):
    model = Articles
    template_name = 'echo/my_saved.html'
    context_object_name = 'articles'
    
    def get_queryset(self):
        saved_articles_ids = SavesModel.objects.filter(user=self.request.user).values_list('article_id', flat=True)
        queryset = Articles.objects.filter(id__in=saved_articles_ids).annotate(
            like_count=Count('likes'),
            comments_count=Count('post_comment'),
            views_count=Count('views'),
            saved_time=F('saves__saved_time')
        ).order_by('-updated')
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            saves = SavesModel.objects.filter(user=self.request.user).values_list('article_id', flat=True)
            context['saved_articles'] = set(saves)
        
        emojies = EmotionImage.objects.all()
        emotions_count = {}
        for article in context['articles']:
            emotions_count[article.id] = {}
            for emoji in emojies:
                count = Emotions.objects.filter(article=article, emotion_type=emoji).count()
                emotions_count[article.id][emoji.name] = count
        
        context['emojies'] = emojies
        context['emotions_count'] = emotions_count
        context['is_authenticated'] = self.request.user.is_authenticated
        return context

class MyCommentsView(ListView):
    model = Comments
    template_name = 'echo/my_comments.html'
    context_object_name = 'comments'
    
    def get_queryset(self):
        queryset = Comments.objects.filter(author=self.request.user).order_by('-updated')
        return queryset


class MyNotificationsView(ListView):
    model = Notifications
    template_name = 'echo/my_notifications.html'
    context_object_name = 'notifications'
    
    def get_queryset(self):
        queryset = Notifications.objects.filter(recipient=self.request.user).order_by('send')
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            user = CustomUserModel.objects.get(user=self.request.user)
            context['settings'] = MessagesSettings.objects.get(user=user)
            print('context', context['settings'])
        return context


class SearchView(ListView):
    model = Articles
    template_name = 'echo/index.html'
    context_object_name = 'articles'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('search')
        
        if query:
            # Использование RawSQL для поиска в ArrayField
            queryset = Articles.objects.annotate(
                similarity=Greatest(
                    TrigramSimilarity('title', query),
                    TrigramSimilarity('content', query)
                )
            ).filter(
                Q(title__icontains=query) |
                Q(content__icontains=query) |
                Q(tags__contains=[query]) |
                Q(id__in=Articles.objects.filter(tags__contains=[query]).values('id'))
            ).order_by('-similarity')[:10]
            
            print('Query:', query)
            print('QuerySet:', queryset.query)
            print('Results:', list(queryset))
        
        return queryset


class SearchByTagView(ListView):
    model = Articles
    template_name = 'echo/index.html'
    context_object_name = 'articles'
    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('search')
        
        if query:
            queryset = Articles.objects.filter(
                Q(tags__contains=[query])
            )
        
        return queryset
    
    
class SubscriptionView(APIView):
    queryset = SubscriptionModel.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        serializer = SubscriptionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, *args, **kwargs):
        user = request.data.get('user')
        informator = request.data.get('informator')
        subscription = SubscriptionModel.objects.get(user=user, informator=informator)
        if not subscription:
            return Response({'error': 'Отсутствует такая подписка'}, status=status.HTTP_400_BAD_REQUEST)
        subscription.delete()
        return Response({'success': 'Подписка удалена'}, status=status.HTTP_204_NO_CONTENT)


class IgnoreView(APIView):
    queryset = IgnoreModel.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        serializer = IgnoreSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, *args, **kwargs):
        user = request.data.get('user')
        ignored_user = request.data.get('ignored_user')
        ignore = IgnoreModel.objects.get(user=user, ignored_user=ignored_user)
        if not ignore:
            return Response({'error': 'Отсутствует такая подписка'}, status=status.HTTP_400_BAD_REQUEST)
        ignore.delete()
        return Response({'success': 'Подписка удалена'}, status=status.HTTP_204_NO_CONTENT)
    
    
class SettingsApiView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = CustomUserModel.objects.get(user=self.request.user)
        try:
            settings = MessagesSettings.objects.get(user=user)
        except MessagesSettings.DoesNotExist:
            return Response({'error': 'Settings not found for this user'}, status=status.HTTP_404_NOT_FOUND)

        serializer = MessagesSettingsSerializer(settings, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SubscribesView(ListView):
    model = SubscriptionModel
    template_name = 'echo/subscribes.html'
    context_object_name = 'subscribes'
    
    def get_queryset(self):
        queryset = SubscriptionModel.objects.filter(user=self.request.user).order_by('sub_time')
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sub_type'] = 'current'
        return context
    

class RecSubscribesView(ListView):
    model = SubscriptionModel
    template_name = 'echo/subscribes.html'
    context_object_name = 'subscribes'
    
    def get_queryset(self):
        current_subscriptions = SubscriptionModel.objects.filter(user=self.request.user).values_list('informator', flat=True)
        queryset = CustomUserModel.objects.exclude(user__in=current_subscriptions).exclude(user=self.request.user)
        print(queryset)
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sub_type'] = 'recommended'
        return context
    
class BlackListView(ListView):
    model = IgnoreModel
    template_name = 'echo/subscribes.html'
    context_object_name = 'ignores'
    
    def get_queryset(self):
        queryset = IgnoreModel.objects.filter(user=self.request.user)
        print(queryset)
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sub_type'] = 'black_list'
        return context
    
class StaffHandlingView(ListView):
    model = UserInquiry
    template_name = 'echo/staff_page.html'
    context_object_name = 'inquiries'
    
    def get_queryset(self):
        queryset = self.model.objects.filter(is_resolved = False)
        print(queryset)
        return queryset
    

class StaffSendMail(UserPassesTestMixin, CreateView):
    model = Notifications
    fields = ['category', 'recipient', 'title', 'notification_text']
    template_name = 'echo/staff_send_mail.html'
    # success_url = reverse_lazy('echo:for_staff')
    
    def test_func(self):
        return self.request.user.is_staff
    
    def form_valid(self, form):
        form.instance.sender = self.request.user
        return super().form_valid(form)

        
class InquirySaveAPIView(APIView):
    model = UserInquiry
    permission_classes = [IsAuthenticated]
    def post(self, request, format=None):
        serializer = InquiriesSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            inquiry = serializer.save(user=request.user)
            response_serializer = InquiriesSerializer(inquiry)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        
    def patch(self, request, pk, format=None):
        try:
            inquiry = UserInquiry.objects.get(pk=pk)
            inquiry.is_resolved = True
            inquiry.save()
            return Response({"detail": "Status updated successfully"}, status=status.HTTP_200_OK)
        except UserInquiry.DoesNotExist:
            return Response({"detail": "Inquiry not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)