from django.shortcuts import render
from django.views import generic

# Create your views here.
from rest_framework import permissions, status
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.views import APIView


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
        return JsonResponse({'message': 'sign_up'})

    def get(self, request, *args, **kwargs):
        return Response(template_name='myauth/sign_up.html')
