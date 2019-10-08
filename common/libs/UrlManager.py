# -*- coding: utf-8 -*-
import time
from application import app


class UrlManager(object):
    def __init__(self):
        pass

    @staticmethod
    def buildUrl(path):
        return path

    @staticmethod
    def buildStaticUrl(path):
        release_version = app.config['RELEASE_VERSION']
        # 添加版本可以自动刷新js文件
        ver = f"{int(time.time())}" if not release_version else release_version
        path = "/static" + path + "?ver=" + ver
        return UrlManager.buildUrl(path)

    @staticmethod
    def buildImageUrl(path):
        """构建文件上传置服务器的路径"""
        app_config = app.config['APP']
        # 服务器域名+文件存放目录+文件名
        url = app_config['image'] + app.config['UPLOAD']['prefix_url'] + path
        return url

    @staticmethod
    def buildUploadPath():
        """无刷新图片显示路径:http://0.0.0.0:5000/static/upload/"""
        url = app.config['APP']['image'] + app.config['UPLOAD']['prefix_url']
        return url
