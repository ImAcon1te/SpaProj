from rest_framework import serializers
from .models import Comment
from PIL import Image
import magic
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'username', 'email', 'homepage', 'text', 'created_at', 'parent', 'image']
        extra_kwargs = {
            'parent': {'required': False}
        }
        read_only_fields = ['id', 'created_at']
        def validate_image(value):
            print('я в сериализаторе')
            # Проверка формата файла (разрешенные: JPG, JPEG, GIF, PNG, TXT)
            allowed_formats = ['image/jpeg', 'image/gif', 'image/png', 'text/plain']
            mime = magic.Magic()
            file_format = mime.from_buffer(value.read(1024))  # Читаем первые 1024 байта для определения типа файла
            value.seek(0)  # Возвращаем указатель чтения в начало файла после чтения байтов
            if file_format not in allowed_formats:
                raise ValidationError('Недопустимый формат файла.')
            if file_format == 'text/plain':
                # Проверка размера файла (не более 100 кБ)
                max_size = 100 * 1024  # 100 кБ в байтах
                if value.size > max_size:
                    raise ValidationError('Размер файла не должен превышать 100 кБ.')
            elif file_format.startswith('image/'):
                # Проверка размеров изображения (не более 320x240)
                max_width = 320
                max_height = 240
                with Image.open(value) as img:
                    width, height = img.size
                    if width > max_width or height > max_height:
                        img.thumbnail((max_width, max_height))
                        img.save(value.path)