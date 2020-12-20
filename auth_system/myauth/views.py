import jwt
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.shortcuts import render, redirect
from django.utils.encoding import force_text, force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views import generic, View
from datetime import datetime
from rest_framework import permissions, status
from rest_framework.decorators import api_view
from rest_framework.exceptions import ValidationError
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.views import APIView

from . import text
from .models import Account
from .serializers import AccountSerializers
import bcrypt




# 로그인
class UserLoginView(APIView):
    permission_classes = [permissions.AllowAny]
    renderer_classes = (JSONRenderer, TemplateHTMLRenderer,)

    def post(self, request, *args, **kargs):
        user_id = request.POST.get('user_id').lower()
        try:
            user_obj = Account.objects.get(user_id=user_id)
        except Account.DoesNotExist:
            user_obj = None

        if user_obj is None:
            content = {'message':'해당 아이디가 존재하지 않습니다.'}
            return Response(content, template_name='myauth/login_fail.html')

        # db에 해당 아이디가 존재할 경우, 비밀번호가 일치하는지 확인, 실패할 경우
        if bcrypt.checkpw(request.POST.get('user_pw').encode('utf-8'), user_obj.user_pw.encode('utf-8')) is False:
            content = {'message':'비밀번호가 일치하지 않습니다.'}
            return Response(content, template_name='myauth/login_fail.html')


        if user_obj.is_active != 1:
            content = {'message': '이메일 인증이 완료되지 않았습니다.'}
            return Response(content, template_name='myauth/login_fail.html')


        # 비밀번호가 일치한 경우, token을 생성하여 user에게 전달
        # jwt 사용하기
        jwt_token = jwt_create(user_id)
        response = Response({
            'response': 'success',
            'message': '로그인에 성공하셨습니다!',
        }, template_name='myauth/login_success.html')
        response.set_cookie('jwttoken', jwt_token)
        return response



    def get(self, request, *args, **kwargs):
        return Response(template_name='myauth/login.html')



# 회원가입
class SignUpView(APIView):
    permission_classes = [permissions.AllowAny]
    renderer_classes = (JSONRenderer, TemplateHTMLRenderer,)

    def post(self, request, *args, **kwargs):
        #id를 소문자로 통일
        user_id = request.POST.get('user_id').lower()
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
        # db에는 salt+user_pw의 해시값이 저장되어야 함(password encryption)
        user_pw = bcrypt.hashpw(request.POST.get('user_pw').encode('utf-8'), salt)
        user_email = request.POST.get('user_email')
        is_active = 0

        user_obj = Account.objects.create(
            user_id=user_id,
            user_pw=user_pw.decode('utf-8'),
            user_email=user_email,
            salt=salt,
            is_active=is_active
        )

        # 이메일 인증 관련
        current_site = get_current_site(request)
        domain = current_site.domain
        uidb64 = urlsafe_base64_encode(force_bytes(user_obj.pk))
        token = jwt.encode({'user': user_obj.user_id}, settings.SECRET_KEY, algorithm='HS256').decode('utf-8')
        message_data = text.message(domain, uidb64, token)

        mail_title = "회원가입 이메일 인증을 완료해주세요"
        mail_to = user_obj.user_email
        email = EmailMessage(mail_title, message_data, to=[mail_to])
        email.send()

        content = {"message":"회원가입에 성공했습니다.\n이메일 인증을 완료해주세요."}
        return Response(content, template_name='myauth/signup_success.html')


    def get(self, request, *args, **kwargs):
        return Response(template_name='myauth/sign_up.html')




# 비밀번호 찾기
class FindPasswordView(APIView):
    permission_classes = [permissions.AllowAny]
    renderer_classes = (JSONRenderer, TemplateHTMLRenderer,)

    def post(self, request, *args, **kwargs):
        user_id = request.POST.get('user_id').lower()
        user_email = request.POST.get('user_email')
        try:
            user_obj = Account.objects.get(user_id=user_id, user_email=user_email)
        except Account.DoesNotExist:
            user_obj = None

        if user_obj is None:
            content = {'message': '해당 계정이 존재하지 않습니다.'}
            return Response(content, template_name='myauth/findpw_fail.html')

        current_site = get_current_site(request)
        domain = current_site.domain
        uidb64 = urlsafe_base64_encode(force_bytes(user_obj.pk))
        #token = jwt.encode({'user': user_obj.user_id}, settings.SECRET_KEY, algorithm='HS256').decode('utf-8')
        message_data = text.find_message(domain, uidb64)

        mail_title = "비밀번호 변경 메일입니다."
        mail_to = user_obj.user_email
        email = EmailMessage(mail_title, message_data, to=[mail_to])
        email.send()
        return Response(template_name='myauth/login.html')


    def get(self, request, *args, **kwargs):
        return Response(template_name='myauth/find_password.html')



# 비밀번호 변경
class ChangePasswordView(APIView):
    permission_classes = [permissions.AllowAny]
    renderer_classes = (JSONRenderer, TemplateHTMLRenderer,)
    def post(self, request, uidb64):
        password = request.data.get('password')
        check_password = request.data.get('check_password')
        if password == check_password:
            user = Account.objects.get(user_id=uidb64)
            user.user_pw = (bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())).decode()
            user.save()
            return Response({
                'response': 'success',
                'message': '비밀번호가 변경되었습니다.'
            })
        else:
            return Response({
                'response': 'error',
                'message': '입력한 비밀번호가 다릅니다.'
            })
    
    def get(self, request, *args, uidb64):
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = Account.objects.get(pk=uid)
            if user.user_id:
                context = {'uuid': user.user_id}
                return Response(context, template_name='myauth/change_password.html')

            return JsonResponse({'message': 'auth fail'}, status=400)
        except ValidationError:
            return JsonResponse({'message': 'type_error'}, status=400)
        except KeyError:
            return JsonResponse({'message': 'INVALID_KEY'}, status=400)





def jwt_create(user_id):
    date = datetime.now()
    key = settings.SECRET_KEY
    cur_time = str(date.year)+str(date.month)+str(date.day)\
               +str(date.hour)+str(date.minute)+str(date.second)
    payload = {
        "user_id": user_id,
        "current_time": cur_time,
    }
    jwt_token = jwt.encode(payload, key, algorithm='HS256').decode('utf-8')
    return jwt_token




# email 인증
class Activate(View):
    def get(self, request, uidb64, token):
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = Account.objects.get(pk=uid)
            user_dic = jwt.decode(token, settings.SECRET_KEY, algorithm='HS256')
            if user.user_id == user_dic["user"]:
                user.is_active = 1
                user.save()
                # 로그인 페이지로 이동
                return redirect("http://127.0.0.1:8000/")

            return JsonResponse({'message': 'auth fail'}, status=400)
        except ValidationError:
            return JsonResponse({'message': 'type_error'}, status=400)
        except KeyError:
            return JsonResponse({'message': 'INVALID_KEY'}, status=400)




@api_view(['GET', ])
def home(request):
    return Response(template_name='myauth/home.html')



'''
1. password를 확인할 때에는 str값으로 받아 매칭하므로 비밀번호를 데이터베이스에 저장할  decoding을 해줘야 한다.
2. postman으로 확인할 떄, request.Post['__'] 이런 식으로 쓰면 안됨. get 사용하기!
'''

