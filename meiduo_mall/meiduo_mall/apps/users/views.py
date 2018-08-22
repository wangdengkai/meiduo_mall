import re

from django.shortcuts import render

# Create your views here.
# url(r'^usernames/(?P<username>\w{5,20})/count/$', views.UsernameCountView.as_view()),
from rest_framework import status

from rest_framework.generics import CreateAPIView,GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from meiduo_mall.apps.verifications.serializers import CheckImageCodeSerializer
from . import serializers
from .models import  User
from .utils import get_User_by_account


class UsernameCountView(APIView):
    '''
    用户名数量
    '''

    def get(self,request,username):
        '''
        获取指定用户名数量

        '''

        count  = User.objects.filter(username=username).count()

        data = {
            'username':username,
            'count':count
        }

        return Response(data)


class MobileCountView(APIView):

    '''
    手机号数量
    '''

    def get(self,request,mobile):

        '''
        获取指定的手机号数量

        '''

        count = User.objects.filter(mobile = mobile).count()

        data = {
            'mobile':mobile,
            'count':count
        }

        return Response(data)


class UserView(CreateAPIView):
    '''
    用户注册
    传入参数，
        username,password,password2,sms_code,mobile,allow
    '''
    serializer_class = serializers.CreateUserSerializer


class SMSCodeTokenView(GenericAPIView):
    '''获取发送短信验证码的凭据'''
    serializer_class = CheckImageCodeSerializer


    def get(self,request,account):
        # 校验图片验证码
        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        # 根据account查询User对象
        user = get_User_by_account(account)
        if user is None:
            return Response({"message":"用户不存在"},status=status.HTTP_404_NOT_FOUND)
        #根据User对象的手机号，生成access——token
        access_token = user.generate_send_sms_code_token()

        #修改手机号
        print(user.mobile)
        mobile=re.sub(r'(\d{3})\d{4}(\d{4})',r'\1****\2',user.mobile)
        # mobile=re.sub(r'(\d{3})\d{4}(\d{4})',r'\1****\2','15191800620')

        print(mobile)
        return Response({
            'mobile':mobile,
            'access_token': access_token,
        })