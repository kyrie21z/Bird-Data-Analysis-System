# -*- coding: utf-8 -*-
"""
工具函数模块
"""

from flask import jsonify
import logging
from datetime import datetime


def register_error_handlers(app):
    """注册全局错误处理器"""
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': '资源未找到'
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f'服务器内部错误: {str(error)}')
        return jsonify({
            'success': False,
            'error': '服务器内部错误'
        }), 500
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'error': '请求参数错误'
        }), 400


def setup_logging(app):
    """设置日志配置"""
    if not app.debug:
        # 生产环境日志配置
        file_handler = logging.FileHandler('logs/app.log')
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)


def format_datetime(dt, format_str='%Y-%m-%d %H:%M:%S'):
    """格式化日期时间"""
    if dt:
        return dt.strftime(format_str)
    return ''


def calculate_completeness_rate(observed_days, total_days=7):
    """计算数据完整率"""
    if total_days == 0:
        return 0
    return round((observed_days / total_days) * 100, 1)


def is_endangered_species(conservation_status):
    """判断是否为濒危物种"""
    return conservation_status in ['EN', 'CR', 'VU']


def get_confidence_level(confidence):
    """根据置信度返回等级描述"""
    if confidence is None:
        return '未知'
    elif confidence >= 0.9:
        return '高'
    elif confidence >= 0.7:
        return '中'
    else:
        return '低'


def validate_coordinates(longitude, latitude):
    """验证经纬度坐标有效性"""
    try:
        lon = float(longitude)
        lat = float(latitude)
        
        # 经度范围：-180 到 180
        # 纬度范围：-90 到 90
        if -180 <= lon <= 180 and -90 <= lat <= 90:
            return True, lon, lat
        else:
            return False, None, None
    except (ValueError, TypeError):
        return False, None, None