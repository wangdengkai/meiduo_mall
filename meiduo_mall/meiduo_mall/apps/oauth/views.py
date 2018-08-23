from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from rest_framework.views import APIView
from rest_framework_jwt.settings import api_settings

from .utils import OAuthQQ
from .models import OAuthQQUser
from .serializers import  OQuthQQUserSerializer

class QQAuthURLView(APIView):
    '''获取QQ登录的url'''

    def get(self,request):
        '''
        提供用于qq登录的url
        '''

        state = request.query_params.get('state')
        oauth = OAuthQQ(state=state)
        auth_url = oauth.get_auth_url()
        return Response({'auth_url':auth_url})


class QQAUthUserView(GenericAPIView):
    '''
    QQ登录的用户
    '''

    serializer_class = OQuthQQUserSerializer
    def get(self,request):
        '''
        获取登录的用户数据
        :param request:
        :return:
        '''

        code = request.query_params.get('code')
        if not code:
            return Response({'message':'缺少code'},status=status.HTTP_400_BAD_REQUEST)

        oauth  = OAuthQQ()

        #获取用户的openid
        try:
            access_token = oauth.get_access_token(code)
            openid = oauth.get_openid(access_token)
        # except QQAPIError:
        except Exception :
            return Response({'message':'QQ服务异常'},status=status.HTTP_503_SERVICE_UNAVAILABLE)

        #判断用户是否存在
        try:
            qq_user = OAuthQQUser.objects.get(openid=openid)
        except OAuthQQUser.DoesNotExist:
            #用户第一次用QQ登录
            token = oauth.generate_save_user_token(openid)
            return Response({'access_token':token})

        else:
            #找到用户，生成token
            user = qq_user.user

            jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
            jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

            payload = jwt_payload_handler(user)
            token = jwt_encode_handler(payload)

            response = Response({
                'token':token,
                'user_id':user.id,
                'username':user.username
            })

            return response

    def post(self,request):
        '''
        保存QQ登录的数据

        '''

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # 生成已登录的token
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)

        response = Response({
            'token': token,
            'user_id': user.id,
            'username': user.username
        })

        return response




