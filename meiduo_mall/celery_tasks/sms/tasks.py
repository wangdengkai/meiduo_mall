import logging

from celery_tasks.main import app

from meiduo_mall.libs.yuntongxun.sms import CCP

logger = logging.getLogger('django')

#验证码短信模板
SMS_CODE_TEMP_ID = 1

@app.task(name = 'sends_sms_code')
def send_sms_code(mobile,code,expires):
    '''
    发送短信验证码
    :param mobile:手机号
    :param code: 验证码
    :param expires: 有效期
    :return: None
    '''
    logging.info('-----------------------------------')
    logging.info(code)
    logging.info('-----------------------------------')
    try:
        ccp =CCP()
        # result = ccp.send_template_sms(mobile,[code,expires],SMS_CODE_TEMP_ID)
        result = 0
    except Exception as e:
        logger.error("发送短信验证码【异常】：%s,message:%s ]" %(mobile,e))

    else:
        if result == 0:
            logger.info("发送短信【正常】【mobile:%s]" % mobile)

        else:
            logging.info('-----------------------------------')
            logging.info(code)
            logging.info('-----------------------------------')
            logger.warning('result%s'%result)
            logger.warning("发送短信验证码【失败】【mobile:%s ]" % mobile)




