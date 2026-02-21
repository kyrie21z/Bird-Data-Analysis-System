# 鸟类数据分析系统 - 部署指南

## 部署环境要求

### 硬件要求
- **CPU**: 2核心以上
- **内存**: 4GB RAM以上
- **存储**: 50GB可用磁盘空间
- **网络**: 内网部署，支持TCP/IP协议

### 软件环境
- **操作系统**: Windows Server 2016+/Linux Ubuntu 18.04+/CentOS 7+
- **Python**: 3.8+
- **数据库**: MySQL 8.0+ 或 SQLite 3.30+
- **Web服务器**: Nginx 1.18+ (生产环境推荐)

## 部署方式选择

### 方式一：开发环境部署（快速启动）
适用于：本地测试、开发调试

### 方式二：生产环境部署（稳定运行）
适用于：正式使用、多用户访问

## 开发环境部署

### 1. 环境准备

```bash
# 克隆项目代码
git clone [项目地址]
cd bird-analysis-system

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

### 2. 数据库配置

```bash
# 复制配置文件
cp .env.example .env

# 编辑.env文件，配置数据库连接
vim .env
```

配置示例：
```env
# SQLite开发环境（推荐）
DATABASE_URL=sqlite:///../database/bird_analysis.db

# MySQL生产环境
# DATABASE_URL=mysql+pymysql://username:password@localhost/bird_analysis?charset=utf8mb4

SECRET_KEY=your-secret-key-here-change-in-production
FLASK_ENV=development
DEBUG=True
```

### 3. 初始化数据库

```bash
# 创建数据库表并插入测试数据
python ../scripts/init_database.py
```

### 4. 启动服务

```bash
# 启动后端API服务
python run_dev.py

# 启动前端静态服务（新终端窗口）
cd ../frontend
python -m http.server 8000
```

### 5. 访问系统
- 后端API: http://localhost:5000
- 前端页面: http://localhost:8000

## 生产环境部署

### 1. 系统环境配置

#### CentOS/RHEL系统
```bash
# 更新系统
sudo yum update -y

# 安装Python 3.8+
sudo yum install python3 python3-pip python3-devel -y

# 安装MySQL
sudo yum install mysql-server -y
sudo systemctl start mysqld
sudo systemctl enable mysqld
```

#### Ubuntu/Debian系统
```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装Python 3.8+
sudo apt install python3 python3-pip python3-dev -y

# 安装MySQL
sudo apt install mysql-server -y
sudo systemctl start mysql
sudo systemctl enable mysql
```

### 2. 创建系统用户
```bash
# 创建专用用户
sudo useradd -r -s /bin/false birdanalysis
sudo mkdir -p /opt/bird-analysis-system
sudo chown birdanalysis:birdanalysis /opt/bird-analysis-system
```

### 3. 部署应用代码
```bash
# 切换到应用目录
cd /opt/bird-analysis-system

# 上传项目文件或克隆代码
# scp -r local_project/* birdanalysis@server:/opt/bird-analysis-system/

# 设置权限
sudo chown -R birdanalysis:birdanalysis /opt/bird-analysis-system
```

### 4. 配置MySQL数据库

```bash
# 登录MySQL
mysql -u root -p

# 创建数据库和用户
CREATE DATABASE bird_analysis CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'birduser'@'localhost' IDENTIFIED BY 'secure_password';
GRANT ALL PRIVILEGES ON bird_analysis.* TO 'birduser'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 5. 配置应用环境

```bash
# 切换到应用用户
sudo su - birdanalysis

# 创建虚拟环境
cd /opt/bird-analysis-system/backend
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cat > .env << EOF
DATABASE_URL=mysql+pymysql://birduser:secure_password@localhost/bird_analysis?charset=utf8mb4
SECRET_KEY=your-production-secret-key-here
FLASK_ENV=production
DEBUG=False
EOF
```

### 6. 初始化生产数据库
```bash
# 初始化数据库
python ../scripts/init_database.py

# 验证数据
python ../scripts/test_database.py
```

### 7. 配置Gunicorn（WSGI服务器）

创建Gunicorn配置文件 `deploy/gunicorn.conf.py`：
```python
bind = "127.0.0.1:5000"
workers = 4
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2
max_requests = 1000
max_requests_jitter = 100
preload_app = True
daemon = True
pidfile = "/var/run/bird-analysis.pid"
user = "birdanalysis"
group = "birdanalysis"
tmp_upload_dir = None
errorlog = "/var/log/bird-analysis/error.log"
accesslog = "/var/log/bird-analysis/access.log"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'
```

创建日志目录：
```bash
sudo mkdir -p /var/log/bird-analysis
sudo chown birdanalysis:birdanalysis /var/log/bird-analysis
```

### 8. 配置Nginx

创建Nginx配置文件 `/etc/nginx/sites-available/bird-analysis`：
```nginx
server {
    listen 80;
    server_name your-domain.com;  # 替换为实际域名
    
    # 前端静态文件
    location / {
        root /opt/bird-analysis-system/frontend;
        index index.html;
        try_files $uri $uri/ =404;
    }
    
    # API代理
    location /api/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 超时设置
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }
    
    # 日志配置
    access_log /var/log/nginx/bird-analysis.access.log;
    error_log /var/log/nginx/bird-analysis.error.log;
    
    # 安全头设置
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
}
```

启用站点：
```bash
sudo ln -s /etc/nginx/sites-available/bird-analysis /etc/nginx/sites-enabled/
sudo nginx -t  # 测试配置
sudo systemctl restart nginx
```

### 9. 配置系统服务

创建systemd服务文件 `/etc/systemd/system/bird-analysis.service`：
```ini
[Unit]
Description=Bird Analysis System
After=network.target mysql.service

[Service]
Type=forking
User=birdanalysis
Group=birdanalysis
WorkingDirectory=/opt/bird-analysis-system/backend
Environment=PATH=/opt/bird-analysis-system/backend/venv/bin
ExecStart=/opt/bird-analysis-system/backend/venv/bin/gunicorn -c deploy/gunicorn.conf.py "app:create_app()"
ExecReload=/bin/kill -s HUP $MAINPID
ExecStop=/bin/kill -s TERM $MAINPID
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

启动服务：
```bash
sudo systemctl daemon-reload
sudo systemctl enable bird-analysis
sudo systemctl start bird-analysis
sudo systemctl status bird-analysis
```

### 10. 防火墙配置

```bash
# CentOS/RHEL
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --reload

# Ubuntu/Debian
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

## 部署验证

### 1. 服务状态检查
```bash
# 检查各服务状态
sudo systemctl status bird-analysis
sudo systemctl status nginx
sudo systemctl status mysql

# 检查端口占用
netstat -tlnp | grep -E ':(80|5000)'
```

### 2. 功能测试
```bash
# 测试API接口
curl -I http://localhost/api/stats
curl http://localhost/api/species

# 测试前端页面
curl -I http://localhost/
```

### 3. 日志检查
```bash
# 应用日志
tail -f /var/log/bird-analysis/error.log

# Nginx日志
tail -f /var/log/nginx/bird-analysis.access.log
```

## 监控与维护

### 1. 健康检查脚本
创建 `/opt/bird-analysis-system/scripts/health_check.sh`：
```bash
#!/bin/bash
# 系统健康检查脚本

# 检查服务状态
SERVICES=("bird-analysis" "nginx" "mysql")
for service in "${SERVICES[@]}"; do
    if ! systemctl is-active --quiet "$service"; then
        echo "$(date): Service $service is not running" >> /var/log/bird-analysis/health.log
        systemctl start "$service"
    fi
done

# 检查API响应
if ! curl -sf http://localhost/api/stats >/dev/null; then
    echo "$(date): API health check failed" >> /var/log/bird-analysis/health.log
fi

# 检查磁盘空间
DISK_USAGE=$(df /opt | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -gt 80 ]; then
    echo "$(date): Disk usage warning: ${DISK_USAGE}%" >> /var/log/bird-analysis/health.log
fi
```

设置定时任务：
```bash
# 添加到crontab
*/5 * * * * /opt/bird-analysis-system/scripts/health_check.sh
```

### 2. 日志轮转配置
创建 `/etc/logrotate.d/bird-analysis`：
```bash
/var/log/bird-analysis/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 birdanalysis birdanalysis
    postrotate
        systemctl reload bird-analysis >/dev/null 2>&1 || true
    endscript
}
```

### 3. 备份策略
```bash
# 数据库备份脚本
#!/bin/bash
BACKUP_DIR="/backup/bird-analysis"
DATE=$(date +%Y%m%d_%H%M%S)

mysqldump -u birduser -psecure_password bird_analysis > "$BACKUP_DIR/db_backup_$DATE.sql"
tar -czf "$BACKUP_DIR/full_backup_$DATE.tar.gz" /opt/bird-analysis-system

# 保留最近7天的备份
find "$BACKUP_DIR" -name "*.sql" -mtime +7 -delete
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +7 -delete
```

## 故障排除

### 常见问题及解决方案

#### 1. 服务无法启动
```bash
# 检查详细错误信息
sudo journalctl -u bird-analysis -f

# 检查端口占用
sudo netstat -tlnp | grep :5000

# 检查权限
ls -la /opt/bird-analysis-system
```

#### 2. 数据库连接失败
```bash
# 测试数据库连接
mysql -u birduser -p -h localhost bird_analysis

# 检查MySQL服务
sudo systemctl status mysql

# 验证连接配置
cat /opt/bird-analysis-system/backend/.env
```

#### 3. 前端页面无法访问
```bash
# 检查Nginx配置
sudo nginx -t

# 检查文件权限
ls -la /opt/bird-analysis-system/frontend

# 检查防火墙
sudo iptables -L
```

#### 4. API返回500错误
```bash
# 查看应用日志
tail -f /var/log/bird-analysis/error.log

# 检查Python依赖
source /opt/bird-analysis-system/backend/venv/bin/activate
pip list
```

## 升级部署

### 1. 代码升级流程
```bash
# 停止服务
sudo systemctl stop bird-analysis

# 备份当前版本
sudo cp -r /opt/bird-analysis-system /opt/bird-analysis-system.backup.$(date +%Y%m%d)

# 部署新版本
cd /opt/bird-analysis-system
git pull origin master  # 或上传新代码

# 更新依赖
source backend/venv/bin/activate
pip install -r backend/requirements.txt

# 数据库迁移（如有）
# python backend/manage.py db upgrade

# 重启服务
sudo systemctl start bird-analysis
```

### 2. 回滚操作
```bash
# 停止服务
sudo systemctl stop bird-analysis

# 恢复备份
sudo rm -rf /opt/bird-analysis-system
sudo cp -r /opt/bird-analysis-system.backup.DATE /opt/bird-analysis-system

# 重启服务
sudo systemctl start bird-analysis
```

## 安全建议

1. **定期更新**: 及时更新系统和依赖包
2. **访问控制**: 限制内网访问，配置IP白名单
3. **SSL证书**: 生产环境建议配置HTTPS
4. **日志审计**: 定期审查访问日志
5. **备份策略**: 建立完善的数据备份机制

---
*©2025 智羽科技 | 本系统基于MySQL+Flask开发*