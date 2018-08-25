import re

from django.contrib.auth.backends import ModelBackend

from .models import User
def jwt_response_payload_handler(token,user=None,request=None):
    '''
    自定义jst认证返回数据
    '''
    return {
        'token':token,
        'user_id':user.id,
        'username':user.username,
    }


def get_User_by_account(account):
    '''
    根据账号信息查找用户对象
    :param account:可以是手机号，用户名
    :return User对象，None
    '''
    try:

        #判断account是否时手机号
        if re.match(r'^1[3-9]\d{9}$',account):
            #如果是手机号，根据手机号查询
            user=User.objects.get(mobile=account)
        else:
            #否则分局suername查询
            user=User.objects.get(username=account)
    except Exception:
        return None
    else:
        return user

class UsernameMobileAuthBackend(ModelBackend):
    '''
    自定义的认证方法后端
    '''

    def authenticate(self, request, username=None, password=None, **kwargs):
        #根据username查询用户对象，username肯能是用户名，也可能是手机号
        user = get_User_by_account(username)

        #如果用户对象存在调用checkpasswor方法检查密码
        if user is not None and user.check_password(password):
            #验证成功，返回对象
            return user

