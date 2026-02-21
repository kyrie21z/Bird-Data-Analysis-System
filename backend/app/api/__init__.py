# -*- coding: utf-8 -*-
"""
API路由蓝图初始化
"""

from flask import Blueprint

bp = Blueprint('api', __name__)

# 导入路由
from app.api import main