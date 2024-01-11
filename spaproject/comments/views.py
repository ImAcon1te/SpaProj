from django.shortcuts import render
from django.core.exceptions import ValidationError
from django.http import FileResponse, JsonResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import make_password
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers import UserProfileSerializer, CommentSerializer, UserSerializer
from .validators import validate_image
from .models import UserProfile,Comment
from captcha.models import CaptchaStore
from captcha.helpers import captcha_image_url


@api_view(['GET'])
@permission_classes([AllowAny])
def get_user_info(request):
    if request.user.is_authenticated:
        user = request.user
        return Response({'authenticated': True, 'username': user.username, 'email': user.email})
    else:
        return Response({'authenticated': False})


class CommentImageView(APIView):
    def get(self, request, filename):
        file_path = f'comment_images/{filename}'
        return FileResponse(open(file_path, 'rb'))

class AvatarImageView(APIView):
    def get(self, request, pk):
        user_profile = UserProfile.objects.get(id=pk)
        if user_profile.avatar:
            return FileResponse(user_profile.avatar.open(), content_type='image/jpeg')  # Укажите правильный content_type
        else:
            return Response(None)

def get_captcha(request):
    captcha_key = CaptchaStore.generate_key()
    image_url = captcha_image_url(captcha_key)
    captcha_text = CaptchaStore.objects.get(hashkey=captcha_key).response
    request.session['captcha_text'] = captcha_text
    request.session.save()
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
    print('entered_captcha_text=',entered_captcha_text)
    print('stored_captcha_text=',stored_captcha_text)
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

class UserProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer
    def perform_create(self, serializer):
        file = self.request.FILES.get('avatar')
        serializer.save(avatar=file)
    def perform_update(self, serializer):
        file = self.request.FILES.get('avatar')
        serializer.save(avatar=file)
        return Response(serializer.data, status=status.HTTP_200_OK)
    def get_object(self):
        user_profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return user_profile


class UserRegisterView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            password = make_password(request.data.get('password'))
            user = serializer.save(password=password)
            UserProfile.objects.create(user=user)
            response_data = {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'password':user.password,
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLoginView(APIView):
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            user_profile = UserProfile.objects.get(user=user)
            serializer = UserProfileSerializer(user_profile)
            print('*'*100)
            print({'username': user.username, 'email': user.email, 'avatar':user_profile.avatar,'id':user_profile.id})
            print('*'*100)
            return Response({'message': 'Пользователь авторизован',
                             'username': user.username,
                             'email': user.email,
                             'avatar':serializer.data['avatar'],
                             'id':user_profile.id},
                             status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Неправильная пара логин/пароль'}, status=status.HTTP_401_UNAUTHORIZED)