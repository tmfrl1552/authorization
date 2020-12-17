from django.shortcuts import render
from django.views import generic

# Create your views here.
from rest_framework import permissions, status
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Account
from .serializers import AccountSerializers
import bcrypt



class UserLoginView(APIView):
    permission_classes = [permissions.AllowAny]
    renderer_classes = (JSONRenderer, TemplateHTMLRenderer,)


    def post(self, request, *args, **kargs):
        user = request.POST['user_id']
        print(user)
        content = {'user_id': 'user'}
        return JsonResponse({
            'response': 'error',
            'message': 'No data found'
        })


    def get(self, request, *args, **kwargs):
        return Response(template_name='myauth/login.html')


class SignUpView(APIView):
    permission_classes = [permissions.AllowAny]
    renderer_classes = (JSONRenderer, TemplateHTMLRenderer,)

    def post(self, request, *args, **kwargs):
        #id를 소문자로 통일
        user_id = request.POST['user_id'].lower()
        try:
            user_obj = Account.objects.get(user_id=user_id)
        except Account.DoesNotExist:
            user_obj = None

        if user_obj:
            message = '동일한 아이디가 존재합니다.'
            # 동일한 id가 존재합니다.라고 알림창 띄워주기
            return Response({"message":message},template_name='myauth/signup_fail.html')

        '''여기부터 동일 id가 없을때 새로 계정 생성해주는 코드 작성'''
        salt = bcrypt.gensalt()
        #db에는 salt+user_pw의 해시값이 저장되어야 함(password encryption)
        user_pw = bcrypt.hashpw(request.POST['user_pw'].encode('utf-8'), salt)
        user_email = request.POST['user_email']
        is_active = '0'

        user_obj = Account(
            user_id=user_id,
            user_pw=user_pw,
            user_email=user_email,
            salt=salt,
            is_active=is_active
        )
        user_obj.save()
        content = {"message":"회원가입에 성공했습니다."}
        return Response(content,template_name='myauth/signup_success.html')


    def get(self, request, *args, **kwargs):
        return Response(template_name='myauth/sign_up.html')





'''user_serializer = AccountSerializers(data=request.data)
        if user_serializer.is_valid():
            return JsonResponse(user_serializer.data)'''
