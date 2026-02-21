# -*- coding: utf-8 -*-
"""
鸟类数据分析系统 Flask 应用初始化
"""

from flask import Flask, send_from_directory, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os

# 初始化扩展
db = SQLAlchemy()

def create_app(config_name='default'):
    """应用工厂函数"""
    # 获取项目根目录（backend的父目录）
    # __file__ 是 app/__init__.py，所以 dirname 是 app，再 .. 是 backend，再 .. 是项目根目录
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    
    # 配置静态文件目录（frontend）
    frontend_dir = os.path.join(base_dir, 'frontend')
    
    app = Flask(__name__, static_folder=frontend_dir, static_url_path='')
    
    # 加载配置
    app.config.from_object('config.Config')
    
    # 初始化扩展
    db.init_app(app)
    CORS(app)  # 支持跨域请求
    
    # 注册蓝图
    from app.api.main import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # 注册错误处理器
    from app.utils.errors import register_error_handlers
    register_error_handlers(app)
    
    # 添加媒体文件服务路由
    data_dir = os.path.join(base_dir, 'data')
    
    @app.route('/data/images/<path:filename>')
    def serve_image(filename):
        """提供图像文件服务"""
        return send_from_directory(os.path.join(data_dir, 'images'), filename)
    
    @app.route('/data/audios/<path:filename>')
    def serve_audio(filename):
        """提供音频文件服务"""
        return send_from_directory(os.path.join(data_dir, 'audios'), filename)
    
    # 根路由 - 返回首页
    @app.route('/')
    def index():
        """返回首页"""
        return send_file(os.path.join(frontend_dir, 'index.html'))
    
    # 其他页面路由
    @app.route('/<path:filename>.html')
    def serve_html(filename):
        """返回HTML页面"""
        return send_file(os.path.join(frontend_dir, f'{filename}.html'))
    
    return app