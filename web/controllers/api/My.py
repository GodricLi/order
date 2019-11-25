# _*_coding:utf-8 _*_
# @Author　 : Ric

from web.controllers.api import route_api
from flask import request, jsonify, g
from common.models.food.Food import Food
from common.libs.UrlManager import UrlManager

import json,datetime


@route_api.route("/my/order")
def my_order_list():
    res = {'code': 200, 'msg': '操作成功~', 'data': {}}
    return jsonify(res)
