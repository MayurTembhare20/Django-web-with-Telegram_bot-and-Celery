from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from myapp.serializers import SendPasswordResetEmailSerializer, UserChangePasswordSerializer, UserLoginSerializer, UserPasswordResetSerializer, UserProfileSerializer, UserRegistrationSerializer
from django.contrib.auth import authenticate
from myapp.renderers import UserRenderer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.authentication import BasicAuthentication,SessionAuthentication
from rest_framework.permissions import IsAuthenticated,AllowAny, IsAdminUser,IsAuthenticatedOrReadOnly,DjangoModelPermissions,DjangoModelPermissionsOrAnonReadOnly
from myapp.models import User

# Generate Token Manually
def get_tokens_for_user(user):
  refresh = RefreshToken.for_user(user)
  return {
      'refresh': str(refresh),
      'access': str(refresh.access_token),
  }

class UserRegistrationView(APIView):
  renderer_classes = [UserRenderer]
  def post(self, request, format=None):
    serializer = UserRegistrationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    token = get_tokens_for_user(user)
    return Response({'token':token, 'msg':'Registration Successful'}, status=status.HTTP_201_CREATED)

class UserLoginView(APIView):
  renderer_classes = [UserRenderer]
  def post(self, request, format=None):
    serializer = UserLoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = serializer.data.get('email')
    password = serializer.data.get('password')
    user = authenticate(email=email, password=password)
    if user is not None:
      token = get_tokens_for_user(user)
      return Response({'token':token, 'msg':'Login Success'}, status=status.HTTP_200_OK)
    else:
      return Response({'errors':{'non_field_errors':['Email or Password is not Valid']}}, status=status.HTTP_404_NOT_FOUND)

class UserProfileView(APIView):
  renderer_classes = [UserRenderer]
  permission_classes = [IsAuthenticated]
  def get(self, request, format=None):
    serializer = UserProfileSerializer(request.user)
    return Response(serializer.data, status=status.HTTP_200_OK)

class UserChangePasswordView(APIView):
  renderer_classes = [UserRenderer]
  permission_classes = [IsAuthenticated]
  def post(self, request, format=None):
    serializer = UserChangePasswordSerializer(data=request.data, context={'user':request.user})
    serializer.is_valid(raise_exception=True)
    return Response({'msg':'Password Changed Successfully'}, status=status.HTTP_200_OK)

class SendPasswordResetEmailView(APIView):
  renderer_classes = [UserRenderer]
  def post(self, request, format=None):
    serializer = SendPasswordResetEmailSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    return Response({'msg':'Password Reset link send. Please check your Email'}, status=status.HTTP_200_OK)

class UserPasswordResetView(APIView):
  renderer_classes = [UserRenderer]
  def post(self, request, uid, token, format=None):
    serializer = UserPasswordResetSerializer(data=request.data, context={'uid':uid, 'token':token})
    serializer.is_valid(raise_exception=True)
    return Response({'msg':'Password Reset Successfully'}, status=status.HTTP_200_OK)


 # ModelSerializer
from rest_framework.viewsets import ViewSet
from .serializers import DataModelSerializer
from rest_framework.generics import get_object_or_404

class DataViewsetAPI(ViewSet):
    authentication_classes=[BasicAuthentication]
    permission_classes=[IsAuthenticated]

    serializer_class= DataModelSerializer
    queryset= User.objects.all()

    def list(self,request):
        # fetch list object
        serializer=self.serializer_class(self.queryset,many=True)
        return Response(serializer.data)
    
    def retrieve(self,request,pk=None):
        # fetch single object
        datas=get_object_or_404(self.queryset,pk=pk)
        serializer=self.serializer_class(datas)
        return Response(serializer.data)
    
    def create(self,request):
        serializer=self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        # create() of DataModelSerializer
        serializer.save()   
        return Response(serializer.data)
    
    def update(self,request,pk=None):
        datas=get_object_or_404(self.queryset,pk=pk)
        serializer=self.serializer_class(datas,data=request.data)
        serializer.is_valid(raise_exception=True)
        # update() of DataModelSerializer
        serializer.save()   
        return Response(serializer.data)
    
    def partial_update(self,request,pk=None):
        datas=get_object_or_404(self.queryset,pk=pk)
        serializer=self.serializer_class(datas, data=request.data,partial=True)
        serializer.is_valid(raise_exception=True)
        # update() of DataModelSerializer
        serializer.save()   
        return Response(serializer.data)
    
    def destroy(self,request,pk=None):
        datas= get_object_or_404(self.queryset,pk=pk)
        datas.delete()
        return Response('deleted')
    

from rest_framework import viewsets
from .serializers import DataModelSerializer
from rest_framework.filters import SearchFilter,OrderingFilter

class DataModelViewsetAPI(viewsets.ModelViewSet):
    
    authentication_classes=[SessionAuthentication]
    permission_classes=[IsAuthenticated]

    serializer_class= DataModelSerializer
    queryset = User.objects.all()
    filter_backends=[SearchFilter,OrderingFilter]
    search_fields=['first_name']
    Ordering_fields=['id','first_name','last_name']


# for celery email
from celery.schedules import crontab
from django.http.response import HttpResponse
from django.shortcuts import render
from .share_task import test_func
from .tasks import send_mail_func
from django_celery_beat.models import PeriodicTask, CrontabSchedule

def test(request):
    test_func.delay()
    return HttpResponse("Done")

def send_mail_to_all(request):
    send_mail_func.delay()
    return HttpResponse("Sent")

def schedule_mail(request):
    schedule, created = CrontabSchedule.objects.get_or_create(hour = 1, minute = 34)
    task = PeriodicTask.objects.create(crontab=schedule, name="schedule_mail_task_"+"5", task='send_mail_app.tasks.send_mail_func')#, args = json.dumps([[2,3]]))
    return HttpResponse("Done")

