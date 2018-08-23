from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response
from rest_framework.views import APIView


from .utils import OAuthQQ

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
