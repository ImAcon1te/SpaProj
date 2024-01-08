from django.db import models
from .validators import validate_image
from django.core.validators import FileExtensionValidator



class Comment(models.Model):
    username = models.CharField(max_length=100)
    email = models.EmailField()
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

