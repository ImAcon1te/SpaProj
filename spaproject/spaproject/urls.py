
from django.contrib import admin
from django.urls import path, include
from comments.views import CommentImageView, AvatarImageView

urlpatterns = [
    path('api/', include('comments.urls')),
    path('admin/', admin.site.urls),
    path('comment_images/<str:filename>', CommentImageView.as_view(), name='download-file'),
    path('profile/<int:pk>', AvatarImageView.as_view(), name='avatar-download'),
    # ...
]

