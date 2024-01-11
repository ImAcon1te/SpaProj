from django.db import models
from .validators import validate_image
from django.core.validators import FileExtensionValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='comment_images/', blank=True, null=True)

class Comment(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, null=True, blank=True)
    username = models.CharField(max_length=100, blank=True) # может быть пустым для анонимного комментария
    email = models.EmailField(blank=True)  # может быть пустым для анонимного комментария
    homepage = models.URLField(blank=True, null=True)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')  # ссылка на родительский комментарий
    image = models.FileField(upload_to='comment_images/',
                              null=True,
                              blank=True,
                              validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'gif', 'png', 'txt']),
                                          validate_image],)

    def __str__(self):
        return f'Comment by {self.username} on {self.created_at.strftime("%Y-%m-%d %H:%M")}'

    class Meta:
        ordering = ['-created_at']

