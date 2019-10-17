# -*- coding: utf-8 -*-
from flask import Blueprint, request, jsonify, redirect
from decimal import Decimal
from application import app, db
from common.libs.Helper import ops_render, pagination
from common.models.food.Food import Food
from common.models.food.FoodCat import FoodCat
from common.libs.food.FoodService import FoodService
from common.models.food.FoodStockChangeLog import FoodStockChangeLog
from common.libs.Helper import get_current_time, get_dict_filter_field
from common.libs.UrlManager import UrlManager
from sqlalchemy import or_

route_food = Blueprint('food_page', __name__)


@route_food.route("/index")
def index():
    res = {}
    req_data = request.values
    page = int(req_data['p']) if ('p' in req_data and req_data['p']) else 1
    query = Food.query
    if 'mix_kw' in req_data:
        rule = or_(Food.name.ilike(f'%{req_data["mix_kw"]}%'),
                   Food.tags.ilike(f'%{req_data["mix_kw"]}%'))
        query = query.filter(rule)

    if 'status' in req_data and int(req_data['status']) > -1:
        query = query.filter(Food.cat_id == int(req_data['cat_id']))

    if 'cat_id' in req_data and int(req_data['cat_id']) > 0:
        query = query.filter(Food.cat_id == int(req_data['cat_id']))

    page_params = {
        'total': query.count(),
        'page_size': app.config['PAGE_SIZE'],
        'page': page,
        'display': app.config['PAGE_DISPLAY'],
        'url': request.full_path.replace("&p={}".format(page), "")
    }
    pages = pagination(page_params)
    offset = (page - 1) * app.config['PAGE_SIZE']
    food_list = query.order_by(Food.id.desc()).offset(offset).limit(app.config['PAGE_SIZE']).all()
    # 根据某个字段构造{'字段':数据库中的某条记录}
    cat_mapping = get_dict_filter_field(FoodCat, FoodCat.id, "id", [])

    res['list'] = food_list
    res['pages'] = pages
    res['search_on'] = req_data
    res['status_mapping'] = app.config['STATUS_MAPPING']
    res['current'] = 'index'
    res['cat_mapping'] = cat_mapping

    return ops_render("food/index.html", res)


@route_food.route("/info")
def info():
    res = {}
    req_data = request.args
    food_id = int(req_data.get('id', 0))
    back_url = UrlManager.buildUrl('/food/index')
    if food_id < 1:
        return redirect(back_url)

    food_info = Food.query.filter_by(id=food_id).first()
    if not food_info:
        return redirect(back_url)
    app.logger.info(food_info.main_image)

    stock_change_list = FoodStockChangeLog.query.filter(FoodStockChangeLog.food_id == food_id).order_by(
        FoodStockChangeLog.food_id.desc()).all()
    res['info'] = food_info
    res['stock_change_list'] = stock_change_list
    res['current'] = 'index'

    return ops_render("food/info.html", res)


@route_food.route("/set", methods=['GET', 'POST'])
def food_set():
    """编辑、添加美食"""
    if request.method == 'GET':
        res = {}
        req_data = request.args
        fid = int(req_data.get('id', 0))
        food_info = Food.query.filter_by(id=fid).first()
        if food_info and food_info.status != 1:
            return redirect(UrlManager.buildUrl('/food/index'))
        cat_list = FoodCat.query.all()
        res['info'] = food_info
        res['cat_list'] = cat_list
        res['current'] = 'index'
        return ops_render("food/set.html", res)

    res = {'code': 200, 'msg': '操作成功', 'data': {}}
    req_data = request.values
    fid = int(req_data['id']) if 'id' in req_data and req_data['id'] else 0
    cat_id = int(req_data['cat_id']) if 'cat_id' in req_data else 0
    name = req_data['name'] if 'name' in req_data else ''
    price = req_data['price'] if 'price' in req_data else ''
    main_image = req_data['main_image'] if 'main_image' in req_data else ''
    summary = req_data['summary'] if 'summary' in req_data else ''
    stock = int(req_data['stock']) if 'stock' in req_data else ''
    tags = req_data['tags'] if 'tags' in req_data else ''

    if cat_id < 1:
        res['code'] = -1
        res['msg'] = "请选择分类~~"
        return jsonify(res)

    if name is None or len(name) < 1:
        res['code'] = -1
        res['msg'] = "请输入符合规范的名称~~"
        return jsonify(res)

    if not price or len(price) < 1:
        res['code'] = -1
        res['msg'] = "请输入符合规范的售卖价格~~"
        return jsonify(res)

    price = Decimal(price).quantize(Decimal('0.00'))
    if price <= 0:
        res['code'] = -1
        res['msg'] = "请输入符合规范的售卖价格~~"
        return jsonify(res)

    if main_image is None or len(main_image) < 3:
        res['code'] = -1
        res['msg'] = "请上传封面图~~"
        return jsonify(res)

    if summary is None or len(summary) < 3:
        res['code'] = -1
        res['msg'] = "请输入图书描述，并不能少于10个字符~~"
        return jsonify(res)

    if stock < 1:
        res['code'] = -1
        res['msg'] = "请输入符合规范的库存量~~"
        return jsonify(res)

    if tags is None or len(tags) < 1:
        res['code'] = -1
        res['msg'] = "请输入标签，便于搜索~~"
        return jsonify(res)

    # 数据库操作
    food_info = Food.query.filter_by(id=fid).first()
    before_stock = 0
    if food_info:
        # 编辑操作
        model_food = food_info
        before_stock = model_food.stock
    else:
        model_food = Food()
        model_food.status = 1
        model_food.created_time = get_current_time()

    model_food.cat_id = cat_id
    model_food.name = name
    model_food.price = price
    model_food.summary = summary
    model_food.stock = stock
    model_food.main_image = main_image
    model_food.updated_time = get_current_time()
    model_food.tags = tags

    db.session.add(model_food)
    db.session.commit()

    FoodService.set_stock_change_log(model_food.id, int(stock) - int(before_stock), '后台修改')
    return jsonify(res)


@route_food.route("/cat")
def cat():
    res = {}
    req_data = request.values
    query = FoodCat.query

    if 'status' in req_data and int(req_data['status']) > -1:
        query = query.filter(FoodCat.status == int(req_data['status']))
    cat_list = query.order_by(FoodCat.weight.desc(), FoodCat.id.desc()).all()
    res['list'] = cat_list
    res['search_on'] = req_data
    res['status_mapping'] = app.config['STATUS_MAPPING']
    res['current'] = 'cat'
    return ops_render("food/cat.html", res)


@route_food.route("/cat-set", methods=['GET', 'POST'])
def cat_set():
    if request.method == 'GET':
        res = {}
        req_data = request.values
        uid = int(req_data.get('id', 0))
        food_info = None
        if uid:
            food_info = FoodCat.query.filter_by(id=uid).first()
        res['info'] = food_info
        return ops_render("food/cat_set.html", res)
    # POST：修改或者添加操作
    res = {'code': 200, 'msg': '操作成功', 'data': {}}
    req_data = request.values
    uid = req_data['id'] if 'id' in req_data else 0
    name = req_data['name'] if 'name' in req_data else ''
    weight = int(req_data['weight']) if ('weight' in req_data and int(req_data['weight']) > 0) else 1

    if not name or len(name) < 1:
        res['code'] = -1
        res['msg'] = '分类名不规范'
        return jsonify(res)

    food_cat_info = FoodCat.query.filter_by(id=uid).first()
    if food_cat_info:
        model_food_cat = food_cat_info
    else:
        # 查询不到说明是添加操作
        model_food_cat = FoodCat()
        model_food_cat.created_time = get_current_time()
    # 添加和修改的共用代码
    model_food_cat.name = name
    model_food_cat.weight = weight
    model_food_cat.update_time = get_current_time()
    db.session.add(model_food_cat)
    db.session.commit()
    return jsonify(res)


@route_food.route("/cat-ops", methods=['POST'])
def cat_ops():
    """美食分类的删除恢复操作"""
    request_data = request.values
    res = {'code': 200, 'msg': "操作成功", 'data': {}}

    uid = request_data['id'] if 'id' in request_data else 0
    act = request_data['act'] if 'act' in request_data else ''
    if not uid:
        res['code'] = -1
        res['msg'] = '选择的账号不存在'
        return jsonify(res)
    if act not in ['remove', 'recover']:
        res['code'] = -1
        res['msg'] = '操作有误，请重试'
        return jsonify(res)

    food_info = FoodCat.query.filter_by(id=uid).first()
    if not food_info:
        res['code'] = -1
        res['msg'] = '分类不存在'
        return jsonify(res)

    if act == "remove":
        food_info.status = 0
    elif act == "recover":
        food_info.status = 1
        food_info.update_time = get_current_time()

    db.session.add(food_info)
    db.session.commit()
    return jsonify(res)
