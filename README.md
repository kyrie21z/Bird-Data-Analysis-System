# 鸟类数据分析系统 V1.0

> 🦅 面向自然保护区巡护员和科研人员的轻量级鸟类数据分析工具

## 项目简介

鸟类数据分析系统是一套专业的鸟类观测数据管理和分析平台，帮助用户：
- **5分钟掌握区域鸟类动态** - 实时仪表盘展示关键指标
- **10秒定位观测热点** - 时空热力图可视化
- **高效管理观测记录** - 支持濒危物种标识和置信度过滤

## 核心功能

### 📊 仪表盘
- **物种丰富度**: 实时统计区域内鸟类物种数量
- **个体总数**: 累计观测到的鸟类总数量
- **濒危物种监测**: 红色高亮显示EN/CR/VU级别物种
- **数据完整率**: 近7天数据采集质量监控

### 🗺️ 时空热力图
- **多时间维度**: 支持今日/7天/30天三种时间范围
- **热点可视化**: 颜色梯度显示观测密集程度
- **平滑过渡**: 时间切换时热力图平滑动画
- **交互式地图**: 支持缩放、拖拽、悬停查看详情

### 📋 数据管理
- **观测记录管理**: 增删查改完整的观测数据
- **濒危物种标识**: 双重视觉标识（背景色+图标）
- **置信度过滤**: 自动过滤低质量识别结果
- **分页展示**: 支持大数据量的分页浏览

## 技术栈

- **后端**: Python 3.8+ + Flask 2.3 + SQLAlchemy 1.4
- **前端**: HTML5 + Bootstrap 5.3 + Leaflet.js 1.9
- **数据库**: SQLite (开发) / MySQL 8.0+ (生产)
- **缓存**: 内存缓存（统计数据5分钟，热力图1分钟）

## 快速开始

### 环境要求
- Python 3.8+
- 2GB RAM以上
- 支持现代浏览器（Chrome/Firefox/Edge）

### 1. 克隆项目
```bash
git clone <项目地址>
cd bird-analysis-system
```

### 2. 安装依赖
```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖
cd backend
pip install -r requirements.txt
```

### 3. 初始化数据库
```bash
# 使用SQLite（开发环境，无需配置MySQL）
cd ..
python scripts/init_database.py

# 或使用MySQL（生产环境）
# mysql -u root -p < database/init.sql
```

### 4. 配置环境变量
```bash
cd backend
cp .env.example .env

# 编辑.env文件（可选，默认使用SQLite）
# 如需使用MySQL，修改DATABASE_URL配置
```

### 5. 启动服务
```bash
# 终端1：启动后端API服务
cd backend
python run_dev.py

# 终端2：启动前端页面服务
cd ../frontend
python -m http.server 8000
```

### 6. 访问系统
- **仪表盘**: http://localhost:8000/index.html
- **数据管理**: http://localhost:8000/data.html
- **API接口**: http://localhost:5000/api/

## 性能优化特性

### 后端优化
- ✅ **数据库查询优化**: 热力图查询使用复合索引，避免子查询
- ✅ **内存缓存机制**: 统计数据缓存5分钟，热力图数据缓存1分钟
- ✅ **连接池管理**: 数据库连接池预检测和自动回收
- ✅ **错误重试机制**: API请求失败自动重试3次

### 前端优化
- ✅ **响应式设计**: 完美适配手机、平板、电脑
- ✅ **加载动画**: 数据加载时显示旋转动画
- ✅ **平滑过渡**: 热力图切换时透明度渐变动画
- ✅ **错误处理**: 友好的错误提示和自动重试

## 目录结构
```
bird-analysis-system/
├── backend/              # 后端代码
│   ├── app/             # Flask应用
│   │   ├── api/         # API路由
│   │   ├── models.py    # 数据模型
│   │   └── utils/       # 工具函数（缓存、错误处理）
│   ├── config.py        # 配置文件
│   ├── run_dev.py       # 开发服务器启动脚本
│   └── requirements.txt # 依赖列表
├── frontend/            # 前端页面
│   ├── index.html       # 仪表盘页面
│   ├── data.html        # 数据管理页面
│   └── assets/          # 静态资源（CSS/JS）
├── database/            # 数据库文件
│   ├── init.sql         # MySQL初始化脚本
│   └── bird_analysis.db # SQLite数据库文件
├── scripts/             # 工具脚本
│   ├── init_database.py # 数据库初始化
│   ├── test_api.py      # API测试脚本
│   └── check_data.py    # 数据检查脚本
└── docs/                # 文档资料
    ├── USER_GUIDE.md    # 用户操作手册
    ├── API_DOCUMENTATION.md # API接口文档
    └── DEPLOYMENT_GUIDE.md  # 部署指南
```

## 目录结构

```
bird-analysis-system/
├── backend/              # 后端代码
│   ├── app/             # Flask应用
│   │   ├── api/         # API路由
│   │   ├── models.py    # 数据模型
│   │   └── utils/       # 工具函数
│   ├── config.py        # 配置文件
│   ├── run_dev.py       # 启动脚本
│   └── requirements.txt # 依赖列表
├── frontend/            # 前端页面
│   ├── index.html       # 仪表盘
│   ├── data.html        # 数据管理
│   └── assets/          # 静态资源
├── database/            # 数据库脚本
│   └── init.sql         # 初始化脚本
└── docs/                # 文档
```

## API接口

### 统计数据
```
GET /api/stats
```

### 热力图数据
```
GET /api/heatmap?days=7
```

### 观测记录
```
GET /api/observations?page=1&limit=20
POST /api/observations
```

## API接口示例

### 获取统计数据
```bash
curl http://localhost:5000/api/stats
```

### 获取热力图数据
```bash
curl "http://localhost:5000/api/heatmap?days=7"
```

### 获取观测记录列表
```bash
curl "http://localhost:5000/api/observations?page=1&limit=5"
```

### 添加观测记录
```bash
curl -X POST "http://localhost:5000/api/observations" \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": 1,
    "species_id": 2,
    "count": 1,
    "confidence": 0.88
  }'
```

## 故障排除

### 🔴 后端服务无法启动

**症状**: 运行`python run_dev.py`时报错

**解决方案**:
```bash
# 1. 检查Python版本
python --version  # 需要3.8+

# 2. 检查依赖是否安装完整
pip install -r requirements.txt

# 3. 检查端口是否被占用
netstat -ano | findstr :5000
# 如果被占用，修改run_dev.py中的端口

# 4. 检查数据库文件是否存在
ls database/bird_analysis.db
# 如果不存在，运行初始化脚本
python scripts/init_database.py
```

### 🔴 前端页面显示"无法连接到服务器"

**症状**: 页面加载但数据无法显示

**解决方案**:
```bash
# 1. 确认后端服务已启动
curl http://localhost:5000/api/stats

# 2. 检查浏览器控制台错误
# F12打开开发者工具查看Console标签

# 3. 检查CORS设置
# 确认backend/config.py中CORS已启用

# 4. 检查防火墙设置
# 确保5000端口未被防火墙阻止
```

### 🔴 热力图不显示数据

**症状**: 地图正常但热力图为空

**可能原因及解决方案**:
1. **时间范围问题**: 检查观测记录时间是否在筛选范围内
2. **置信度过滤**: 检查数据置信度是否≥0.7
3. **状态过滤**: 检查记录状态是否为"confirmed"
4. **坐标问题**: 检查经纬度数据是否正确

```bash
# 检查数据库中的观测记录
python scripts/check_data.py
```

### 🔴 数据库连接失败

**症状**: API返回500错误，日志显示数据库错误

**解决方案**:
```bash
# 1. 检查数据库文件权限
ls -la database/

# 2. 重新初始化数据库
python scripts/init_database.py

# 3. 检查.env配置
cat backend/.env
# 确保DATABASE_URL配置正确
```

### 🔴 页面样式错乱

**症状**: 页面布局混乱，样式不生效

**解决方案**:
1. 清除浏览器缓存（Ctrl+Shift+Delete）
2. 检查网络连接，确保能访问CDN资源
3. 检查浏览器控制台是否有CSS加载错误

## 性能优化建议

### 数据库优化
- 定期清理过期数据
- 为常用查询字段添加索引
- 使用连接池管理数据库连接

### 缓存策略
- 统计数据每5分钟自动刷新
- 热力图数据每1分钟自动刷新
- 手动刷新：点击浏览器刷新按钮

### 前端优化
- 使用现代浏览器获得最佳体验
- 避免同时打开多个标签页
- 定期清理浏览器缓存

## 部署说明

生产环境部署详见 [DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md)

## 使用手册

详细操作指南详见 [USER_GUIDE.md](docs/USER_GUIDE.md)

## API文档

接口详细说明详见 [API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md)

## 更新日志

### V1.0 (2026-02-12)
- ✅ 初始版本发布
- ✅ 仪表盘核心功能
- ✅ 时空热力图可视化
- ✅ 数据管理功能
- ✅ 响应式设计支持
- ✅ 性能优化（缓存、查询优化）

## 技术支持

如有问题，请：
1. 查阅本文档的故障排除章节
2. 查看 [docs/](docs/) 目录下的详细文档
3. 检查应用日志文件

## 许可证

MIT License

---
*©2025 | 本系统基于MySQL+Flask开发*