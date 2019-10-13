# _*_coding:utf-8 _*_
# @Author　 : Ric
import hashlib, requests, random, string, json
from application import app


class MemberService:
    """
    处理用户使用微信登录，获取openid，生成加密字符串
    """

    @staticmethod
    def get_member_code(member_info=None):
        m = hashlib.md5()
        s = f'{member_info.id}-{member_info.salt}-{member_info.status}'
        m.update(s.encode('utf-8'))
        return m.hexdigest()

    @staticmethod
    def get_salt(length=16):
        key_list = [random.choice((string.ascii_letters + string.digits)) for _i in range(length)]
        return "".join(key_list)

    @staticmethod
    def get_wechat_openid(code):
        # 微信登录获取openid请求地址
        url = f'https://api.weixin.qq.com/sns/jscode2session?appid={app.config["MINA_APP"]["app_id"]}&' \
              f'secret={app.config["MINA_APP"]["app_key"]}&js_code={code}&grant_type=authorization_code'
        r = requests.get(url=url)
        wx_res = json.loads(r.text)
        openid = None
        if 'openid' in wx_res:
            openid = wx_res['openid']
        return openid
