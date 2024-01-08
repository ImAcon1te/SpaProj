from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from .models import Comment
from .serializers import CommentSerializer
from .validators import validate_image
from django.http import JsonResponse
from captcha.models import CaptchaStore
from captcha.helpers import captcha_image_url
from rest_framework.decorators import api_view
from django.core.exceptions import ValidationError
import requests
import os
from django.http import FileResponse
from rest_framework.views import APIView

class CommentImageView(APIView):
    def get(self, request, filename):
        file_path = f'comment_images/{filename}'
        return FileResponse(open(file_path, 'rb'))

def get_captcha(request):
    captcha_key = CaptchaStore.generate_key()
    image_url = captcha_image_url(captcha_key)
    #full_image_url = f'http://{request.get_host()}{image_url}'
    captcha_text = CaptchaStore.objects.get(hashkey=captcha_key).response
    request.session['captcha_text'] = captcha_text
    request.session.save()
    # удалить позже
    """
    try:
        image_response = requests.get(full_image_url)
        image_content = image_response.content
        image_path = os.path.join('captcha_images', f'{captcha_key}.png')
        with open(image_path, 'wb') as image_file:
            image_file.write(image_content)
    except requests.exceptions.RequestException as e:
        return JsonResponse({'error': str(e)})
    """
    return JsonResponse({'key': captcha_key, 'image_url': image_url})

@api_view(['POST'])
def check_captcha(request):
    entered_captcha_text = request.data.get('captcha_text')
    captcha_key = request.data.get('captcha_key')
    try:
        stored_captcha = CaptchaStore.objects.get(hashkey=captcha_key)
        stored_captcha_text = stored_captcha.response
    except CaptchaStore.DoesNotExist:
        stored_captcha_text = None
    if entered_captcha_text == stored_captcha_text:
        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False, 'error': 'Неправильная CAPTCHA'})

class CommentListCreateView(generics.ListCreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    def perform_create(self, serializer):
        # Получаем файл из запроса
        file = self.request.FILES.get('image')
        # Проверяем валидность файла
        try:
            validate_image(file)
        except ValidationError as e:
            # Не прошли валидацию
            raise serializers.ValidationError({'image': e.messages})
        # Создаем комментарий с учетом файла
        serializer.save(image=file)
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

