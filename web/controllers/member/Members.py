# -*- coding: utf-8 -*-
from flask import Blueprint, request, jsonify, redirect
from common.libs.Helper import ops_render, pagination
from common.models.member.Member import Member
from application import app, db
from common.libs.UrlManager import UrlManager
from common.libs.Helper import get_current_time

route_member = Blueprint('member_page', __name__)


@route_member.route("/index")
def index():
    res = {}
    req_data = request.values
    page = int(req_data['page']) if 'page' in req_data else 1
    query = Member.query
    if 'mix_kw' in req_data:
        query = Member.query.filter(Member.nickname.ilike(f"%{req_data['mix_kw']}%"))

    if 'status' in req_data:
        query = Member.query.filter(Member.status == int(req_data['status']))

    page_params = {
        'total': query.count(),
        'page_size': app.config['PAGE_SIZE'],
        'page': page,
        'display': app.config['PAGE_DISPLAY'],
        'url': request.full_path.replace(f"&p={page}", "")
    }
    pages = pagination(page_params)
    offset = (page - 1) * app.config['PAGE_SIZE']
    member_list = query.order_by(Member.id.desc()).offset(offset) \
        .limit(app.config['PAGE_SIZE']).all()
    res['list'] = member_list
    res['pages'] = pages
    res['search_on'] = req_data
    res['status_mapping'] = app.config['STATUS_MAPPING']
    res['current'] = 'index'
    return ops_render("member/index.html", res)


@route_member.route("/info")
def info():
    res = {}
    req_data = request.values
    member_id = int(req_data.get('id', 0))
    back_url = UrlManager.buildUrl('/member/index')
    if member_id < 1:
        return redirect(back_url)
    member_info = Member.query.filter_by(id=member_id).first()
    if not member_info:
        return redirect(back_url)
    res['info'] = member_info
    res['current'] = 'index'
    return ops_render("member/info.html", res)


@route_member.route("/set", methods=['GET', 'POST'])
def member_set():
    if request.method == 'GET':
        res = {}
        req_data = request.args
        member_id = int(req_data.get('id', 0))
        back_url = UrlManager.buildUrl('/member/index')
        if member_id < 1:
            return redirect(back_url)
        member_info = Member.query.filter_by(id=member_id).first()
        if not member_info:
            return redirect(back_url)
        if member_info.status != 1:
            return redirect(back_url)
        res['info'] = member_info
        res['current'] = 'index'
        return ops_render("member/set.html", res)
    res = {'code': 200, 'msg': '操作成功', 'data': {}}
    req_data = request.values
    member_id = req_data['id'] if 'id' in req_data else 0
    nickname = req_data['nickname'] if 'nickname' in req_data else ''
    if not nickname or len(nickname) < 1:
        res['code'] = -1
        res['msg'] = '用户名不规范'
        return jsonify(res)
    member_info = Member.query.filter_by(id=member_id).first()
    if not member_info:
        res['code'] = -1
        res['msg'] = '指定会员不存在'
        return jsonify(res)
    member_info.nickname = nickname
    member_info.update_time = get_current_time()
    db.session.add(member_info)
    db.session.commit()
    return jsonify(res)


@route_member.route("/comment")
def comment():
    return ops_render("member/comment.html")


@route_member.route('/ops', methods=['GET', 'POST'])
def ops():
    res = {'code': 200, 'msg': '操作成功', 'data': {}}
    req_data = request.values
    member_id = req_data['id'] if 'id' in req_data else 0
    act = req_data['act'] if 'act' in req_data else ''

    if not member_id:
        res['code'] = -1
        res['msg'] = '请选择账号'
        return jsonify(res)
    if act not in ['remove', 'recover']:
        res['code'] = -1
        res['msg'] = '操作有误'
        return jsonify(res)
    member_info = Member.query.filter_by(id=member_id).first()
    if not member_info:
        res['code'] = -1
        res['msg'] = '指定会员不存在'
        return jsonify(res)
    if act == 'remove':
        member_info.status = 0
    elif act == 'recover':
        member_info.status = 1

    member_info.update_time = get_current_time()
    db.session.add(member_info)
    db.session.commit()
    return jsonify(res)
