# -*- coding: utf-8 -*-
"""
应用启动入口
"""

import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app import create_app, db

# 创建应用实例
app = create_app(os.getenv('FLASK_ENV', 'development'))

@app.shell_context_processor
def make_shell_context():
    """Flask shell上下文"""
    return {'db': db, 'app': app}

if __name__ == '__main__':
    # 创建日志目录
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # 运行开发服务器
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        threaded=True
    )