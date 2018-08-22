from django.contrib.auth.models import AbstractUser
from django.db import models
from itsdangerous import TimedJSONWebSignatureSerializer as TJWSSerializer, BadData
from django.conf import settings

from . import constants


# Create your models here.

class User(AbstractUser):
    '''用户模型类'''

    mobile = models.CharField(max_length=11,unique=True,verbose_name='手机号')


    class Meta:
        db_table = 'tb_users'
        verbose_name = '用户'
        verbose_name_plural = verbose_name


    def generate_send_sms_code_token(self):
        '''
        生成发送短信验证码的access_token
        :return: access_token
        '''
        # 创建itesdangerous模型的专函工具
        serializer = TJWSSerializer(settings.SECRET_KEY,constants.SEND_SMS_CODE_EXPIRES)
        data = {
            'mobile':self.mobile
        }

        token = serializer.dumps(data)

        return token.decode()

    @staticmethod
    def check_send_sms_code_token(token):
        '''
        检验发送短信验证码的token
        :param token: 短信验证码的token
        :return: None,mobile
        '''
        serializer = TJWSSerializer(settings.SECRET_KEY,expires_in=constants.SEND_SMS_CODE_EXPIRES)

        try:
            data = serializer.loads(token)
        except BadData:
            return None
        else:
            return data.get('mobile')
