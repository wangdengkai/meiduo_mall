import random

from celery_tasks.sms import tasks as sms_tasks
from django.http import HttpResponse
from django_redis import get_redis_connection
from meiduo_mall.libs.captcha.captcha import captcha
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from meiduo_mall.libs.yuntongxun.sms import CCP
from users.models import User

from celery_tasks.sms.tasks import send_sms_code
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

        serialize = self.get_serializer(data=request.query_params)
        serialize.is_valid(raise_exception=True)

        #生成短信验证码
        sms_code = '%06d' % random.randint(0,999999)

        #保存短信验证码与发送记录
        redis_conn = get_redis_connection('verify_codes')
        # redis_conn.setex('sms_%s' %mobile,constants.SMS_CODE_REDIS_EXPIRES,sms_code)
        # redis_conn.setex('send_flas_%s'%mobile,constants.SEND_SMS_CODE_INTERVAL,1)
        #使用redis的pipeline管道一次执行多个命令
        pl = redis_conn.pipeline()
        pl.setex('sms_%s' % mobile,constants.SMS_CODE_REDIS_EXPIRES,sms_code)
        pl.setex('send_flag_%s' %mobile,constants.SEND_SMS_CODE_INTERVAL,1)
        #让管道执行命令
        pl.execute()

        #发送短信
        # ccp =CCP()
        # tims = str(constants.SMS_CODE_REDIS_EXPIRES / 60)
        # try:
        #     result = ccp.send_template_sms(mobile,[sms_code,tims],constants.SMS_CODE_TEMP_ID)
        #     print(result)
        # except Exception as e:
        #     print(e)
        # # 使用celery发布异步任务

        sms_tasks.send_sms_code.delay(mobile,sms_code,constants.SMS_CODE_REDIS_EXPIRES / 60)

        return Response({'message':'OK'})
        # pl = redis_conn.pipeline()
        #
        # pl.setex('sms_%s' % mobile,constants.SMS_CODE_REDIS_EXPIRES,sms_code)
        #
        # pl.setex('send_flag_%s' %mobile,constants.SEND_SMS_CODE_INTERVAL,1)
        #
        #
        # pl.execute()

        # #发送短信验证码
        # sms_code_expires = str(constants.SMS_CODE_REDIS_EXPIRES//60)
        # ccp = CCP()
        # ccp.send_template_sms(mobile,[code,expires],SMS_CODE_TEMP_ID)
        #
        # return Response({'message':'ok'})

        # #异步发送短信验证码
        # sms_code_expires = str(constants.SMS_CODE_REDIS_EXPIRES // 60)
        # sms_tasks.send_sms_code.delay(mobile,sms_code_expires)
        #
        # return Response({"message":"OK"})


class SMSCodeByTokenView(APIView):
    '''
    短信验证码发送，根据Token
    '''
    def get(self,request):
        #验证access_Token
        access_token = request.query_params.get('access_token')
        if not access_token:
            return Response({'message':'缺少accesstoken'},status=status.HTTP_400_BAD_REQUEST)
        mobile = User.check_send_sms_code_token(access_token)
        if not mobile:
            return Response({'message':'access token 无效'},status=status.HTTP_400_BAD_REQUEST)

        #判断是否在60秒内
        redis_conn = get_redis_connection('verify_codes')
        send_flag = redis_conn.get('send_flag_%s' % mobile)
        if send_flag:
            return Response({'message':'请求次数过于频繁'},status=status.HTTP_429_TOO_MANY_REQUESTS)


        #生成短信验证码
        sms_code = '%06d'%random.randint(0,999999)

        #保存短信验证码和发送记录
        pl = redis_conn.pipeline()
        pl.setex('sms_%s' % mobile,constants.SMS_CODE_REDIS_EXPIRES,sms_code)
        pl.setex('send_flag_%s' %mobile,constants.SEND_SMS_CODE_INTERVAL,1)
        #发送短信验证码
        pl.execute()

        sms_tasks.send_sms_code.delay(mobile,sms_code,constants.SMS_CODE_REDIS_EXPIRES/60)
        return Response({'message':'ok'},status=status.HTTP_200_OK)

