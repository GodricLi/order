# _*_coding:utf-8 _*_
# @Author　 : Ric
from application import app
from flask import request, g, jsonify
from common.models.member.Member import Member
from common.libs.member.MemberService import MemberService
import re

"""
api认证
"""


@app.before_request
def before_request():
    ignore_urls = app.config['IGNORE_URLS']
    ignore_check_login_urls = app.config['IGNORE_CHECK_LOGIN_URLS']
    path = request.path
    if 'api' not in path:
        return
    # 如果是静态文件就不用查询用户信息
    pattern = re.compile('|'.join(ignore_check_login_urls))
    if pattern.match(path):
        return
    member_info = check_member_login()

    # 登录成功之后设置一个user_info对象全局变量
    g.member_info = None
    if member_info:
        g.member_info = member_info
    pattern = re.compile('%s' % "|".join(ignore_urls))
    if pattern.match(path):
        return
    if not member_info:
        res = {'code': -2, 'mgs': '未登录', 'data': {}}
        return jsonify(res)
    return


def check_member_login():
    """
    判断用户是否登录
    :return:
    """
    auth_cookie = request.headers.get('Authorization')
    if not auth_cookie:
        return False
    auth_info = auth_cookie.split('#')
    if len(auth_info) != 2:
        return False
    try:
        member_info = Member.query.filter_by(id=auth_info[1]).first()
    except Exception:
        return False
    if not member_info:
        return False
    if auth_info[0] != MemberService.get_member_code(member_info):
        return False
    if member_info.status != 1:
        return False
    return member_info
