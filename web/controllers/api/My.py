# _*_coding:utf-8 _*_
# @Author　 : Ric

from web.controllers.api import route_api
from flask import request, jsonify, g


@route_api.route("/my/order")
def my_order_list():
    res = {'code': 200, 'msg': '操作成功~', 'data': {}}
    return jsonify(res)
