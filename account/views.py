from django.shortcuts import render,redirect
from rest_framework.views import APIView
from .serializers import RegistrationSerializer , ActivationSerializer,UserSerializer,RegistrationPhoneSerializer,UpdateUserSerializer
from .send_email import send_confirmation_email,send_confirmation_password
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView , get_object_or_404,ListAPIView
from django.contrib.auth import get_user_model,authenticate, login
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import permissions
from rest_framework_simplejwt.tokens import RefreshToken
from django.views import View
from rest_framework import status
from django.http import HttpResponseRedirect
from django.urls import reverse
from rest_framework.permissions import IsAuthenticated
from django.core.mail import send_mail
from drf_yasg.utils import swagger_auto_schema 
User = get_user_model()
from shop_ada.tasks import send_activation_sms_task,send_confirmation_email_task,send_confirmation_password_task,sender_order_notification_task
# Create your views here.
# class RegistrationView(APIView):
#     @swagger_auto_schema(request_body=RegistrationSerializer)
#     def post(self, request):
#         serializer = RegistrationSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         user = serializer.save()
#         if user:
#             try:
#                 send_confirmation_email(user.email , user.activation_code)
#             except:
#                 return Response({'message': "Зарегистрировался  но на почту код не отправился ",'data':serializer.data}, status=201)
#         return Response(serializer.data, status=201)

class ActivationView(GenericAPIView):
    serializer_class = ActivationSerializer

    def get(self, request):
        code = request.GET.get('u')
        user = get_object_or_404(User, activation_code=code)
        user.is_active = True
        user.save()
        return Response('Успешно активирован',status=200)
    
    def post(self,request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception = True)
        serializer.save()
        return Response('Успешно активирован',status = 200)
        




class UpdatePasswordView(APIView):
    @swagger_auto_schema(request_body=UpdateUserSerializer)
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Пожалуйста, укажите имейл'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'Пользователь с указанным имейлом не найден'}, status=status.HTTP_404_NOT_FOUND)
        password_change_code = user.create_password_change_code()
        user.password_change_code = password_change_code
        user.save()
        send_confirmation_password(user.email,password_change_code)

        # send_mail(
        #     'Подтвердите ваше изменение',
        #     f'Ваш код подтверждение: {password_change_code}',
        #     'Book_Store@gmail.com',
        #     [user.email],
        #     fail_silently=False,
        # )

        return Response({"message": "Код подтверждение отправлен!."}, status=status.HTTP_200_OK)
    @swagger_auto_schema(request_body=UpdateUserSerializer)
    def put(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Пожалуйста, укажите имейл'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'Пользователь с указанным имейлом не найден'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = UpdateUserSerializer(user, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Password updated successfully"}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class LoginView(TokenObtainPairView):
    permission_classes = (permissions.AllowAny,)

class UserListView(ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAdminUser,)



class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data['refresh']
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'message':'logout successful'}, status=200)
        except Exception as e:
            return Response({'error': 'Invalid token'},status=400)
        
# class LoginView(View):
#     templates_name = 'login.html'

#     def get(self,request):
#         return render(request, self.templates_name)
    
#     def post(self, request):
#         email = request.POST.get('email')
#         password = request.POST.get('password')
        
#         if not email or not password:
#             return render(request, self.templates_name, {'error':'Email and password are required'})
#         user = authenticate(request, email=email,password = password)
#         if user:
#             login(request, user)
#             token_view = TokenObtainPairView.as_view()
#             token_response = token_view(request)

#             if token_response.status_code==status.HTTP_200_OK:
#                 return HttpResponseRedirect(reverse('dashboard')+f'?token={token_response.data["access"]}')
#         else:
#             return render(request, self.templates_name,{'error':'Invalid data'})
#         return render(request, self.templates_name)
    

class DashboardView(View):
    templates_name = 'dashboard.html'

    def get(self, request):
        return render(request, self.templates_name)
    
    def post(self, request):
        action = request.POST.get('action',None)

        if action == 'login':
            return redirect('login')
        elif action == 'register':
            return redirect('registration')
        else:
            return render(request, self.templates_name,{'error':'Invalid action'})
        

class RegistrationView(APIView):
    templates_name = 'registration.html'
    
    def get(self, request):
        return render(request, self.templates_name)

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            if user:
                try:
                    send_confirmation_email_task.delay(user.email,user.activation_code)
                    return redirect('activation')
                except:
                    return Response({'message': "Зарегистрировался  но на почту код не отправился ",'data':serializer.data}, status=201)
            return Response({'message':'User registred successfully'},status=201)
        else:
            return render(request, self.templates_name,{'error':serializer.errors})
        
        
def activation_view(request):
    return render(request, 'activation.html')


class RegistrationPhoneView(APIView):
    @swagger_auto_schema(request_body=RegistrationPhoneSerializer)
    def post(self, request):
        data = request.data
        serializer = RegistrationPhoneSerializer(data = data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response('Успешно зарегистрирован',status=201)
        