# _*_coding:utf-8 _*_
# @Author　 : Ric
import requests, json
from web.controllers.api import route_api
from flask import request, jsonify, g


@route_api.route('/member/login', methods=['GET', 'POST'])
def login():
    res = {'code': 200, 'msg': '登录成功', 'data': {}}
    req_data = request.values
    code = req_data['code'] if 'code' in req_data else ''
    if not code or len(code) < 1:
        res['code'] = -1
        res['msg'] = '需要code'
        return jsonify(res)
