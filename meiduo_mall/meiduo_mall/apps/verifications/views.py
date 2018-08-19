from django.http import HttpResponse
from django_redis import get_redis_connection
from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView

from meiduo_mall.libs.captcha.captcha import captcha
from . import constants
from .serializers import CheckImageCodeSerializer


class ImageCodeView(APIView):


    '''
    图片验证码
    '''

    def get(self,request,image_code_id):
        '''
        获取图片验证码
        :param request: 前段发送的请求
        :param image_code_id: 图片验证码id
        :return: 图片
        '''

        #生成验证码的图片
        text,image = captcha.generate_captcha()


        redis_conn = get_redis_connection('verify_codes')
        redis_conn.setex("img_%s" %image_code_id,constants.IMAGE_CODE_REDIS_EXPIRES,text)

        # 固定返回验证码图片数据，不需要REST framework框架的Response帮助我们决定返回响应数据的格式
        # 所以此处直接使用Django原生的HttpResponse即可
        return HttpResponse(image,content_type='images/jpg')


class SMSCodeView(GenericAPIView):

    serializer_class = CheckImageCodeSerializer

    def get(self,request,mobile):

        serialize = self.get_serializer()
        serialize.is_valid(raise_exception=True)