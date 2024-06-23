from django.urls import path, include
from rest_framework.routers import DefaultRouter

from echoverse.views import index, CreateArticleView, ArticleCreateAPIView, ArticleImageCreateAPIView, \
    ArticleDetailView, save_article, EmotionsSaveApi, LikeSaveAPIView, ViewSaveAPIView, save_comment, get_top,\
    RecentArticlesView, ByCategory, MyArticlesView, MyLikesView, MyCommentsView, SearchView, SubscriptionView, IgnoreView,\
    MyNotificationsView, SettingsApiView, SubscribesView, RecSubscribesView, BlackListView

app_name = 'echo'

router = DefaultRouter()
router.register(r'emoji', EmotionsSaveApi, basename='emoji')
urlpatterns = [
    path('', index, name='index'),
    path('create_article/', CreateArticleView.as_view(), name='create'),
    path('detail/<int:pk>/', ArticleDetailView.as_view(), name='article_detail'),
    path('save_article/<int:pk>/<int:user_id>/', save_article, name='save_article'),
    path('save_comment/<int:pk>/', save_comment, name='save_comment'),
    path('api/create_article/', ArticleCreateAPIView.as_view(), name='api_create'),
    path('api/create_image/<int:pk>/', ArticleImageCreateAPIView.as_view(), name='api_image'),
    path('api/like/<int:pk>/', LikeSaveAPIView.as_view(), name='like'),
    path('api/view/<int:pk>/', ViewSaveAPIView.as_view(), name='view'),
    path('api_router/', include(router.urls)),
    path('top20/', get_top, name='top20'),
    path('recent/', RecentArticlesView.as_view(), name='recent'),
    path('category/<int:pk>/', ByCategory.as_view(), name='by_category'),
    path('my_articles/', MyArticlesView.as_view(), name='my_articles'),
    path('my_likes/', MyLikesView.as_view(), name='my_likes'),
    path('my_comments/', MyCommentsView.as_view(), name='my_comments'),
    path('my_notifications/', MyNotificationsView.as_view(), name='my_notifications'),
    path('search/', SearchView.as_view(), name='search'),
    path('api/subscriptions/create/', SubscriptionView.as_view(), name='create_subscription'),
    path('api/ignore/create/', IgnoreView.as_view(), name='create_ignore'),
    path('api/subscriptions/delete/', SubscriptionView.as_view(), name='cancel_subscription'),
    path('api/ignore/delete/', IgnoreView.as_view(), name='cancel_ignore'),
    path('api/settings/', SettingsApiView.as_view(), name='settings'),
    path('api/subscribes/current', SubscribesView.as_view(), name='my_subscribes'),
    path('api/subscribes/recommended', RecSubscribesView.as_view(), name='rec_subscribes'),
    path('api/subscribes/black_list', BlackListView.as_view(), name='black_list'),
]