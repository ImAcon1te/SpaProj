from django.urls import path
from .views import CommentListCreateView, CommentDetailView, get_captcha, check_captcha, CommentImageView
from django.urls import path, include
urlpatterns = [
    path('comments/', CommentListCreateView.as_view(), name='comment-list-create'),
    path('comments/<int:pk>/', CommentDetailView.as_view(), name='comment-detail'),
    path('generate-captcha/', get_captcha, name='generate-captcha'),
    path('сheck-captcha/', check_captcha, name='сheck-captcha'),
    path('comment_images/<str:filename>', CommentImageView.as_view(), name='download-file'),
    path('captcha/', include('captcha.urls')),
]