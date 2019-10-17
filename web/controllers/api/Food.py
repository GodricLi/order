# _*_coding:utf-8 _*_
# @Author　 : Ric
from flask import Blueprint, request, jsonify
from web.controllers.api import route_api
from common.models.food.Food import Food
from common.models.food.FoodCat import FoodCat
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
