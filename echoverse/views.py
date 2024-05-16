from datetime import timedelta

from django.contrib.postgres.search import SearchVector, SearchQuery
from django.http import HttpResponseRedirect
from django.utils import timezone
from django.shortcuts import render, redirect,get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, FormView, DetailView, ListView
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from echoverse.forms import ArticleForm, ImageForm, CommentForm, SavesForm
from echoverse.models import Articles, EmotionImage, Emotions, LikesModel, ViewsModel, Comments, SavesModel, Categories, \
    SubscriptionModel, IgnoreModel
from .serializers import ArticleSerializer, ArticleImageSerializer, EmotionsSerializer, LikesSerializer, \
    ViewsSerializer, SubscriptionSerializer, IgnoreSerializer
from django.db.models import Count
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def index(request):
    if request.user.is_authenticated:
        ignored_authors_ids = IgnoreModel.objects.filter(
            user=request.user
        ).values_list('ignored_user_id', flat=True)
        
        article_list = Articles.objects.exclude(
            author_id__in=ignored_authors_ids
        ).annotate(
            comments_count=Count('post_comment', distinct=True),
            views_count=Count('viewsmodel', distinct=True)
        )
    else:
        article_list = Articles.objects.annotate(
            comments_count=Count('post_comment'),
            views_count=Count('viewsmodel')
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
    
    paginator = Paginator(article_list, 10)
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
    #     print('Успешно')
    #     return redirect(self.get_success_url())
    #
    # def form_invalid(self, form, image_form):
    #     return self.render_to_response(self.get_context_data(form=form, image_form=image_form))
    
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
        print(Articles.objects.filter(pk=pk))
        return Articles.objects.filter(pk=self.kwargs.get('pk')).prefetch_related('post_comment__children')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        article = context['object']
        print(article)
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
        print('emotions_count', emotions_count)
        context['emojies'] = emojies
        context['emotions_count'] = emotions_count
        context['is_liked'] = likes
        context['is_saved'] = saves
        context['views'] = views
        context['comments'] = comments
        context['comments_count'] = comments_count
        return context
def save_article(request, pk, user_id):
    print(request.method)
    if request.method == 'POST':
        data = request.POST.copy()
        print('data',data)
        data['article'] = pk
        data['user'] = user_id
        form = SavesForm(data)
        if form.is_valid():
            form.save()
            next_url = request.GET.get('next', reverse_lazy('echo:article_detail', kwargs={'pk': pk}))
            return HttpResponseRedirect(next_url)
        else:
            print("Form is not valid")
            print(form.errors)  # Логируем ошибки формы для дополнительной отладки
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
            print('data')
            data['user'] = request.user.pk
            try:
                elem = Emotions.objects.get(article=data['article'], user=data['user'],
                                            emotion_type=data['emotion_type'])
                print('Existing element:', elem)
            except Emotions.DoesNotExist:
                print('No existing element found.')
                elem = None
            if elem:
                elem.delete()
                return Response({'message': 'Emotion entry deleted.'}, status=status.HTTP_200_OK)
            serializer = self.get_serializer(data=data)
            if serializer.is_valid():
                print('is_valid')
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
            print("like.delete()")
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
            print("Form is not valid")
            print(form.errors)
    return redirect(reverse_lazy('echo:article_detail', kwargs={'pk': pk}))
    
def get_top(request):
    articles = Articles.objects.annotate(
        like_count=Count('likesmodel'),
        comments_count=Count('post_comment'),
        views_count=Count('viewsmodel')).filter(like_count__gt=0).order_by('-like_count')[:20]
    emojies = EmotionImage.objects.all()
    likes = LikesModel.objects.filter(user=request.user).values_list('article_id', flat=True)
    liked_articles = set(likes)
    saves = SavesModel.objects.filter(user=request.user).values_list('article_id', flat=True)
    saved_articles = set(saves)
    
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
            like_count=Count('likesmodel'),
            comments_count=Count('post_comment'),
            views_count=Count('viewsmodel')).filter(updated__gte=twelve_hours_ago).order_by('-updated')
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        articles = context['articles']
        emojies = EmotionImage.objects.all()
        likes = LikesModel.objects.filter(user=self.request.user).values_list('article_id', flat=True)
        liked_articles = set(likes)
        saves = SavesModel.objects.filter(user=self.request.user).values_list('article_id', flat=True)
        saved_articles = set(saves)
        
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
        print("context",context)
        return context


class ByCategory(ListView):
    model = Articles
    template_name = 'echo/index.html'
    context_object_name = 'articles'
    paginate_by = 10
    
    def get_queryset(self):
        category_id = self.kwargs['pk']
        queryset = Articles.objects.annotate(
            like_count=Count('likesmodel'),
            comments_count=Count('post_comment'),
            views_count=Count('viewsmodel')).filter(category_id=category_id).order_by('-updated')
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_id = self.kwargs['pk']
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
        context['category'] = Categories.objects.get(pk=category_id)
        context['page_title'] = f"Категория: {Categories.objects.get(pk=category_id)}"
        return context
    
    
class MyArticlesView(ListView):
    model = Articles
    template_name = 'echo/my_articles.html'
    context_object_name = 'articles'
    
    def get_queryset(self):
        queryset = Articles.objects.annotate(
            like_count=Count('likesmodel'),
            comments_count=Count('post_comment'),
            views_count=Count('viewsmodel')).filter(author=self.request.user).order_by('-updated')
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
        queryset = Articles.objects.annotate(
            like_count=Count('likesmodel'),
            comments_count=Count('post_comment'),
            views_count=Count('viewsmodel')).filter(id__in=liked_articles_ids).order_by('-updated')
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

class MyCommentsView(ListView):
    model = Comments
    template_name = 'echo/my_comments.html'
    context_object_name = 'comments'
    
    def get_queryset(self):
        queryset = Comments.objects.filter(author=self.request.user).order_by('-updated')
        return queryset


class SearchView(ListView):
    model = Articles
    template_name = 'echo/index.html'
    context_object_name = 'articles'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('search')
        print(query)

        if query:
            search_query = SearchQuery(query, search_type='plain')
            search_vector = SearchVector('author__username', 'title', 'content', 'category__name', 'tags')
            queryset = queryset.annotate(
                search=search_vector
            ).filter(search=search_query)
        print(queryset)
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
        print(user)
        print(ignored_user)
        ignore = IgnoreModel.objects.get(user=user, ignored_user=ignored_user)
        print(ignore)
        if not ignore:
            return Response({'error': 'Отсутствует такая подписка'}, status=status.HTTP_400_BAD_REQUEST)
        ignore.delete()
        return Response({'success': 'Подписка удалена'}, status=status.HTTP_204_NO_CONTENT)
    
    


    