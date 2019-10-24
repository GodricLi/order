# _*_coding:utf-8 _*_
# @Author　 : Ric
from flask import Blueprint, request, jsonify, g
from web.controllers.api import route_api
from common.models.food.Food import Food
from common.models.food.FoodCat import FoodCat
from common.models.member.MemberCart import MemberCart
from common.libs.UrlManager import UrlManager
from sqlalchemy import or_


@route_api.route('/food/index')
def food_index():
    """美食页面展示"""
    res = {'code': 200, 'msg': '操作成功', 'data': {}}
    data_cat_list = []
    cat_list = FoodCat.query.filter_by(status=1).order_by(FoodCat.weight.desc()).all()
    data_cat_list.append({
        'id': 0,
        'name': '全部'
    })
    if cat_list:
        for item in cat_list:
            data_cat_list.append({
                'id': item.id,
                'name': item.name
            })
    res['data']['cat_list'] = data_cat_list

    food_list = Food.query.filter_by(status=1).order_by(Food.total_count.desc(), Food.id.desc()).limit(3).all()
    data_food_list = []
    if food_list:
        for item in food_list:
            data_food_list.append({
                'id': item.id,
                'pic_url': UrlManager.buildImageUrl(item.main_image)
            })
    res['data']['banner_list'] = data_food_list
    return jsonify(res)


@route_api.route('/food/search')
def food_search():
    res = {'code': 200, 'msg': '操作成功', 'data': {}}
    req_data = request.values
    cat_id = int(req_data['cat_id']) if 'cat_id' in req_data else 0
    mix_kw = str(req_data['mix_kw']) if 'mix_kw' in req_data else ''
    p = int(req_data['p']) if 'p' in req_data else 1

    if p < 1:
        p = 1
    page_size = 10
    offset = (p - 1) * page_size
    query = Food.query.filter_by(status=1)
    if cat_id > 0:
        query = Food.query.filter_by(cat_id=cat_id)
    if mix_kw:
        rule = or_(Food.name.ilike(f'%{mix_kw}%'), Food.tags.ilike(f'%{mix_kw}%'))
        query = Food.query.filter_by(rule)
    food_list = query.order_by(Food.total_count.desc(), Food.id.desc()).offset(offset).limit(page_size).all()

    data_food_list = []
    if food_list:
        for item in food_list:
            data_food_list.append({
                'id': item.id,
                'name': item.name,
                'price': str(item.price),
                'min_price': str(item.price),
                'pic_url': UrlManager.buildImageUrl(item.main_image)
            })
    res['data']['list'] = data_food_list
    res['data']['has_more'] = 0 if len(data_food_list) < page_size else 1
    return jsonify(res)


@route_api.route('/food/info')
def food_info():
    """美食详情页面"""
    res = {'code': 200, 'msg': '操作成功', 'data': {}}
    req_data = request.values
    food_id = int(req_data['id']) if 'id' in req_data else 0
    food_info_obj = Food.query.filter_by(id=food_id).first()
    if not food_info_obj:
        res['code'] = -1
        res['msg'] = '美食已下架'

    member_info = g.member_info
    cart_number = 0
    if member_info:
        cart_number = MemberCart.query.filter_by(member_id=member_info.id).count()
    res['data']['info'] = {
        'id': food_info_obj.id,
        'name': food_info_obj.name,
        'summary': food_info_obj.summary,
        'total_count': food_info_obj.total_count,
        'main_image': UrlManager.buildImageUrl(food_info_obj.main_image),
        'price': str(food_info_obj.price),
        'stock': food_info_obj.stock,
        'pics': [UrlManager.buildImageUrl(food_info_obj.main_image)]
    }
    res['data']['cart_number'] = cart_number
    return jsonify(res)


@route_api.route('/food/comments')
def food_comments():
    res = {'code': 200, 'msg': '操作成功', 'data': {}}

    return jsonify(res)
