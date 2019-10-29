# _*_coding:utf-8 _*_
# @Author　 : Ric
from web.controllers.api import route_api
from flask import request, jsonify, g
from common.models.food.Food import Food
from common.models.member.MemberCart import MemberCart
from application import app, db
from common.libs.member.CartService import CartService


@route_api.route('cart/index')
def cart_index():
    res = {'code': 200, 'msg': 'success', 'data': {}}
    member_info = g.member_info
    if not member_info:
        res['code'] = -1
        res['msg'] = "获取失败，伪登录~~"
        return jsonify(res)
    return jsonify(res)


@route_api.route('/cart/set', methods=['POST'])
def cart_set():
    res = {'code': 200, 'msg': 'success', 'data': {}}
    req_data = request.values
    food_id = int(req_data['id']) if 'id' in req_data else 0
    food_number = int(req_data['number']) if 'number' in req_data else 0
    if food_id < 1 or food_number < 1:
        res['code'] = -1
        res['msg'] = 'failed food or number error'
        return jsonify(res)

    member_info = g.member_info
    if not member_info:
        res['code'] = -1
        res['msg'] = 'failed member error'
        return jsonify(res)

    food_info = Food.query.filter_by(id=food_id).first()
    if not food_info:
        res['code'] = -1
        res['msg'] = 'failed food error'
        return jsonify(res)
    if food_info.stock < 1:
        res['code'] = -1
        res['msg'] = 'failed food stock error'
        return jsonify(res)
    ret = CartService.set_item(member_id=member_info.id, food_id=food_info.id, number=food_number)
    if not ret:
        res['code'] = -1
        res['msg'] = 'failed '
        return jsonify(res)
    return jsonify(res)
