# _*_coding:utf-8 _*_
# @Author　 : Ric
from flask import Blueprint
import requests, json
from flask import request, jsonify, g
from application import app, db
from common.models.member.OauthMemberBind import OauthMemberBind
from common.models.member.Member import Member
from common.libs.Helper import get_current_time
from common.libs.member.MemberService import MemberService

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
    openid = MemberService.get_wechat_openid(code)
    nickname = req_data['nickName'] if 'nickName' in req_data else ''
    sex = req_data['gender'] if 'gender' in req_data else 0
    avatar = req_data['avatarUrl'] if 'avatarUrl' in req_data else ''

    # 根据openid查询用户是否已经绑定注册过
    bind_info = OauthMemberBind.query.filter_by(openid=openid, type=1).first()
    if not bind_info:
        model_member = Member()
        model_member.nickname = nickname
        model_member.sex = sex
        model_member.avatar = avatar
        model_member.updated_time = model_member.created_time = get_current_time()
        model_member.salt = MemberService.get_salt()
        db.session.add(model_member)
        db.session.commit()

        model_bind = OauthMemberBind()
        model_bind.member_id = model_member.id
        model_bind.type = 1
        model_bind.openid = openid
        model_bind.extra = ''
        model_bind.updated_time = model_bind.created_time = get_current_time()
        db.session.add(model_bind)
        db.session.commit()

        bind_info = model_bind
    # 登录成功后设置一个token返回
    member_info = Member.query.filter_by(id=bind_info.member_id).first()
    res['data']['token'] = f'{MemberService.get_member_code(member_info)}#{member_info.id}'
    return jsonify(res)


@route_api.route('/member/check_reg', methods=['GET', 'POST'])
def check_reg():
    """判断token检测微信用户是否登录过"""
    res = {'code': 200, 'msg': '成功', 'data': {}}
    req_data = request.values
    code = req_data['code'] if 'code' in req_data else ''
    if not code or len(code) < 1:
        res['code'] = -1
        res['msg'] = 'code error'
        return jsonify(res)

    openid = MemberService.get_wechat_openid(code)
    if not openid:
        res['code'] = -1
        res['msg'] = 'no openid'
        return jsonify(res)

    bind_info = OauthMemberBind.query.filter_by(openid=openid, type=1).first()
    if not bind_info:
        res['code'] = -1
        res['msg'] = '未绑定'
        return jsonify(res)

    member_info = Member.query.filter_by(id=bind_info.member_id).first()
    if not member_info:
        res['code'] = -1
        res['msg'] = '未查询到账户信息'
        return jsonify(res)

    token = f"{MemberService.get_member_code(member_info)}#{member_info.id}"
    res['data']['token'] = token
    return jsonify(res)
