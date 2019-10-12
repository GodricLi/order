# _*_coding:utf-8 _*_
# @Author　 : Ric
from flask import Blueprint
import requests, json
from flask import request, jsonify, g
from application import app, db
from common.models.member.OauthMemberBind import OauthMemberBind
from common.models.member.Member import Member
from common.libs.Helper import get_current_time
route_api = Blueprint('api_page', __name__)


@route_api.route('/')
def index():
    return "Mina Api V1.0"


@route_api.route('/member/login', methods=['GET', 'POST'])
def login():
    res = {'code': 200, 'msg': '登录成功', 'data': {}}
    req_data = request.values
    code = req_data['code'] if 'code' in req_data else ''
    if not code or len(code) < 1:
        res['code'] = -1
        res['msg'] = '需要code'
        return jsonify(res)
    # 微信登录请求地址
    url = f'https://api.weixin.qq.com/sns/jscode2session?appid={app.config["MINA_APP"]["app_id"]}&' \
          f'secret={app.config["MINA_APP"]["app_key"]}&js_code={code}&grant_type=authorization_code'
    r = requests.get(url=url)
    wx_res = json.loads(r.text)
    app.logger.info(wx_res)
    openid = wx_res['openid'] if 'openid' in wx_res else ''
    nickname = req_data['nickName'] if 'nickName' in req_data else ''
    sex = req_data['gender'] if 'gender' in req_data else 0
    avatar = req_data['avatarUrl'] if 'avatarUrl' in req_data else ''

    bind_info = OauthMemberBind.query.filter_by(openid=openid,type=1).first()
    if not bind_info:
        model_member = Member()
        model_member.nickname = nickname
        model_member.sex=sex
        model_member.avatar = avatar
        model_member.updated_time = model_member.created_time=get_current_time()
        db.session.add(model_member)
        db.session.commit()


    return jsonify(res)
