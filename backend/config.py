# -*- coding: utf-8 -*-
"""
应用配置文件
"""

import os
from datetime import timedelta

class Config:
    """基础配置类"""
    
    # 基础配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'bird-analysis-secret-key-change-in-production'
    
    # 数据库配置
    # 获取项目根目录（backend的父目录）
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    # 构建数据库路径 - SQLite URI 使用四个斜杠表示绝对路径
    # 注意：Windows 路径中的空格不需要 URL 编码，SQLAlchemy 会正确处理
    db_path = os.path.join(BASE_DIR, 'database', 'bird_analysis.db')
    # 使用四个斜杠的绝对路径格式（Windows）
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get('DATABASE_URL') or 
        'sqlite:///' + db_path
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,  # 连接池预检测
        'pool_recycle': 3600,   # 连接回收时间
        'echo': False           # 是否输出SQL语句（开发时可设为True）
    }
    
    # 应用配置
    APP_NAME = '鸟类数据分析系统'
    VERSION = '1.0'
    
    # API配置
    API_PREFIX = '/api'
    JSON_SORT_KEYS = False  # 保持JSON字段顺序
    
    # 文件上传配置
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB最大文件大小
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
    
    # 数据过滤配置
    MIN_CONFIDENCE_THRESHOLD = 0.7  # 最小置信度阈值
    DEFAULT_TIME_RANGE_DAYS = 7     # 默认时间范围
    
    # 分页配置
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100
    
    @staticmethod
    def init_app(app):
        """初始化应用"""
        # 确保上传目录存在
        if not os.path.exists(Config.UPLOAD_FOLDER):
            os.makedirs(Config.UPLOAD_FOLDER)


class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    SQLALCHEMY_ECHO = True  # 输出SQL语句便于调试


class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    SQLALCHEMY_ECHO = False


class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


# 配置字典
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}