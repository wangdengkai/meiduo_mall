from rest_framework import serializers
from django_redis import get_redis_connection

class CheckImageCodeSerializer(serializers.Serializer):
    '''
    图片验证码序列化器
    '''

    image_code_id = serializers.UUIDField(format='hex_verbose')
    text = serializers.CharField(max_length=4,min_length=4)

    def validate(self, attrs):
        '''
        校验图片验证码是否正确
        '''
        image_code_id = attrs['image_code_id']
        text =attrs['text']
        #查询redis数据库，获取真实的验证码
        redis_conn =get_redis_connection('verify_codes')
        real_image_code = redis_conn.get('img_%s' % image_code_id )
        if real_image_code is None:
            #过期或者不存在
            raise serializers.ValidationError("图片验证码无效")


        # 对比
        real_image_code = real_image_code.decode()
        if real_image_code.lower() != text.lower():
            raise serializers.ValidationError("图片验证码错误")


        #redis中发送短信验证码的标志,send_flag《mobile> ； 1,由redis维护60s的有效期
        mobile = self.context['view'].kwargs['mobile']
        send_flag = redis_conn.get('send_flag_%s'% mobile)
        if send_flag:
            raise serializers.ValidationError("发送短信次数过于频繁")

        return attrs

