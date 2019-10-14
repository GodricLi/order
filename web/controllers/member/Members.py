# -*- coding: utf-8 -*-
from flask import Blueprint, request, jsonify, redirect
from common.libs.Helper import ops_render, pagination
from common.models.member.Member import Member
from application import app, db

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

    return ops_render("member/info.html")


@route_member.route("/set")
def set():
    return ops_render("member/set.html")


@route_member.route("/comment")
def comment():
    return ops_render("member/comment.html")
