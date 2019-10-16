# -*- coding: utf-8 -*-
from common.libs.Helper import ops_render
from flask import Blueprint


route_finance = Blueprint('finance_page', __name__)


@route_finance.route("/index")
def index():
    res = {}
    res['current'] = 'index'
    return ops_render("finance/index.html", res)


@route_finance.route("/pay-info")
def payInfo():
    return ops_render("finance/pay_info.html")


@route_finance.route("/account")
def account():
    return ops_render("finance/account.html")
