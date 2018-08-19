from django.shortcuts import render

# Create your views here.
#url('^image_codes/(?P<image_code_id>[\w-]+)/$',views.ImageCodeView.as_view()),
from rest_framework.views import APIView


class ImageCodeView(APIView):
    ''' 图片验证码'''
    pass