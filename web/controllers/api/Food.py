# _*_coding:utf-8 _*_
# @Author　 : Ric
from flask import Blueprint, request, jsonify
from web.controllers.api import route_api


@route_api.route('/')
def food_index():
    res = {'code': 200, 'msg': '操作成功', 'data': {}}
    return jsonify(res)
