from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
import base64
from PIL import Image
from io import BytesIO
import magic

def validate_image(value):
    if value:
        # Проверка формата файла (разрешенные: JPG, JPEG, GIF, PNG, TXT)
        allowed_formats = ['PNG image data', 'image/png',
                           'GIF image data', 'image/gif',
                           'JPEG image data', 'image/jpeg', 'image/jpg',
                           "UTF-8 Unicode text" ,'text/plain',
                           'RIFF (little-endian) data']
        mime = magic.Magic()
        file_format = mime.from_buffer(value.read(256))  # Читаем первые 1024 байта для определения типа файла
        value.seek(0)  # Возвращаем указатель чтения в начало файла после чтения байтов
        print(f'file_format = {file_format.split(",")[0]}')
        if file_format.split(',')[0] not in allowed_formats:
            raise ValidationError('Недопустимый формат файла1.')
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