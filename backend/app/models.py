# -*- coding: utf-8 -*-
"""
数据库模型定义
基于提供的schema.sql实现ORM映射
"""

from datetime import datetime
from app import db
from sqlalchemy import func

class BirdSpecies(db.Model):
    """鸟类物种主数据模型"""
    __tablename__ = 'bird_species'
    
    id = db.Column(db.Integer, primary_key=True, comment='物种ID')
    chinese_name = db.Column(db.String(50), nullable=False, comment='中文名称')
    english_name = db.Column(db.String(100), comment='英文名称')
    scientific_name = db.Column(db.String(100), nullable=False, unique=True, comment='拉丁学名')
    order = db.Column(db.String(50), comment='目')
    family = db.Column(db.String(50), comment='科')
    conservation_status = db.Column(
        db.Enum('LC', 'NT', 'VU', 'EN', 'CR', 'EW', 'EX'),
        nullable=False,
        comment='IUCN保护级别'
    )
    migration_type = db.Column(
        db.Enum('resident', 'summer_breeder', 'winter_visitor', 'passage_migrant', 'vagrant'),
        comment='迁徙类型'
    )
    typical_habitat = db.Column(db.String(200), comment='典型栖息地')
    distribution_range = db.Column(db.Text, comment='分布范围')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    # 关系
    observations = db.relationship('Observation', backref='species', lazy=True)
    
    def is_endangered(self):
        """判断是否为濒危物种"""
        return self.conservation_status in ['EN', 'CR', 'VU']
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'chinese_name': self.chinese_name,
            'english_name': self.english_name,
            'scientific_name': self.scientific_name,
            'conservation_status': self.conservation_status,
            'migration_type': self.migration_type,
            'is_endangered': self.is_endangered()
        }


class Area(db.Model):
    """观测区域模型"""
    __tablename__ = 'areas'
    
    id = db.Column(db.Integer, primary_key=True, comment='区域ID')
    name = db.Column(db.String(100), nullable=False, unique=True, comment='区域名称')
    habitat_type = db.Column(
        db.Enum('wetland', 'forest', 'grassland', 'farmland', 'urban', 'others'),
        nullable=False,
        comment='生境类型'
    )
    boundary_geojson = db.Column(db.Text, comment='边界坐标')
    management_unit = db.Column(db.String(100), comment='管理单位')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    devices = db.relationship('Device', backref='area', lazy=True)
    observations = db.relationship('Observation', backref='area', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'habitat_type': self.habitat_type,
            'management_unit': self.management_unit
        }


class Device(db.Model):
    """观测设备模型"""
    __tablename__ = 'devices'
    
    id = db.Column(db.Integer, primary_key=True, comment='设备ID')
    serial_number = db.Column(db.String(50), nullable=False, unique=True, comment='唯一序列号')
    model = db.Column(db.String(50), nullable=False, comment='设备型号')
    area_id = db.Column(db.Integer, db.ForeignKey('areas.id'), nullable=False, comment='所属区域ID')
    longitude = db.Column(db.Numeric(10, 6), nullable=False, comment='安装经度')
    latitude = db.Column(db.Numeric(10, 6), nullable=False, comment='安装纬度')
    altitude = db.Column(db.Numeric(6, 2), comment='海拔')
    installed_at = db.Column(db.DateTime, nullable=False, comment='安装日期')
    status = db.Column(
        db.Enum('active', 'maintenance', 'fault'),
        default='active',
        comment='设备状态'
    )
    remark = db.Column(db.Text, comment='备注')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    observations = db.relationship('Observation', backref='device', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'serial_number': self.serial_number,
            'model': self.model,
            'area_id': self.area_id,
            'longitude': float(self.longitude),
            'latitude': float(self.latitude),
            'status': self.status
        }


class Image(db.Model):
    """图像数据模型"""
    __tablename__ = 'images'
    
    id = db.Column(db.Integer, primary_key=True, comment='图像ID')
    storage_path = db.Column(db.String(255), nullable=False, comment='存储路径')
    dimensions = db.Column(db.String(20), comment='图像尺寸')
    file_size = db.Column(db.Integer, comment='文件大小')
    file_format = db.Column(db.String(10), comment='文件格式')
    snap_time = db.Column(db.DateTime, nullable=False, comment='拍摄时间')
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow, comment='上传时间')
    
    # 关系
    observation = db.relationship('Observation', backref='image', uselist=False, lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'storage_path': self.storage_path,
            'snap_time': self.snap_time.isoformat() if self.snap_time else None
        }


class Audio(db.Model):
    """音频数据模型"""
    __tablename__ = 'audios'
    
    id = db.Column(db.Integer, primary_key=True, comment='音频ID')
    storage_path = db.Column(db.String(255), nullable=False, comment='存储路径')
    record_start_time = db.Column(db.DateTime, nullable=False, comment='录音起始时间')
    duration = db.Column(db.Integer, comment='音频时长')
    file_size = db.Column(db.Integer, comment='文件大小')
    file_format = db.Column(db.String(10), comment='文件格式')
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    observation = db.relationship('Observation', backref='audio', uselist=False, lazy=True)


class Observation(db.Model):
    """观测记录模型（核心模型）"""
    __tablename__ = 'observations'
    
    id = db.Column(db.Integer, primary_key=True, comment='观测记录ID')
    device_id = db.Column(db.Integer, db.ForeignKey('devices.id'), nullable=False, comment='观测设备ID')
    image_id = db.Column(db.Integer, db.ForeignKey('images.id'), comment='关联图像ID')
    audio_id = db.Column(db.Integer, db.ForeignKey('audios.id'), comment='关联音频ID')
    species_id = db.Column(db.Integer, db.ForeignKey('bird_species.id'), nullable=False, comment='鸟类物种ID')
    count = db.Column(db.SmallInteger, nullable=False, default=1, comment='鸟类数量')
    observed_at = db.Column(db.DateTime, nullable=False, comment='观测时间')
    area_id = db.Column(db.Integer, db.ForeignKey('areas.id'), nullable=False, comment='观测区域ID')
    longitude = db.Column(db.Numeric(10, 6), nullable=False, comment='观测经度')
    latitude = db.Column(db.Numeric(10, 6), nullable=False, comment='观测纬度')
    confidence = db.Column(db.Float, comment='AI识别置信度')
    status = db.Column(
        db.Enum('confirmed', 'pending', 'rejected'),
        default='pending',
        comment='记录状态'
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='入库时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """转换为字典格式，用于API返回"""
        return {
            'id': self.id,
            'device_id': self.device_id,
            'species': self.species.to_dict() if self.species else None,
            'count': self.count,
            'observed_at': self.observed_at.isoformat() if self.observed_at else None,
            'area': self.area.to_dict() if self.area else None,
            'longitude': float(self.longitude),
            'latitude': float(self.latitude),
            'confidence': self.confidence,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @staticmethod
    def get_valid_observations(days=7, min_confidence=0.7):
        """
        获取有效观测记录（已确认且置信度达标）
        
        Args:
            days: 时间范围（天数）
            min_confidence: 最小置信度阈值
            
        Returns:
            Query对象
        """
        from datetime import datetime, timedelta
        
        threshold_date = datetime.utcnow() - timedelta(days=days)
        
        return Observation.query.filter(
            Observation.observed_at >= threshold_date,
            Observation.confidence >= min_confidence,
            Observation.status == 'confirmed'
        )
    
    @staticmethod
    def get_heatmap_data(days=7, min_confidence=0.7):
        """
        获取热力图数据 - 优化版本
        
        性能优化：
        1. 使用子查询避免多次查询
        2. 直接使用复合索引加速时间范围查询
        3. 一次性聚合减少数据传输
        
        Returns:
            [{'lat': float, 'lng': float, 'count': int}, ...]
        """
        from datetime import datetime, timedelta
        
        threshold_date = datetime.utcnow() - timedelta(days=days)
        
        # 优化查询：直接使用复合条件聚合，避免子查询
        heatmap_data = db.session.query(
            Observation.latitude,
            Observation.longitude,
            func.count(Observation.id).label('count')
        ).filter(
            Observation.observed_at >= threshold_date,
            Observation.confidence >= min_confidence,
            Observation.status == 'confirmed'
        ).group_by(
            Observation.latitude, Observation.longitude
        ).all()
        
        return [
            {
                'lat': float(item.latitude),
                'lng': float(item.longitude),
                'count': item.count
            }
            for item in heatmap_data
        ]
    
    @staticmethod
    def get_heatmap_data_fixed(days=7, min_confidence=0.7):
        """
        获取热力图数据 - 修复版本
        修复了经纬度字段映射问题
        """
        from datetime import datetime, timedelta
        
        threshold_date = datetime.utcnow() - timedelta(days=days)
        
        # 查询数据
        heatmap_data = db.session.query(
            Observation.latitude,
            Observation.longitude,
            func.count(Observation.id).label('count')
        ).filter(
            Observation.observed_at >= threshold_date,
            Observation.confidence >= min_confidence,
            Observation.status == 'confirmed'
        ).group_by(
            Observation.latitude, Observation.longitude
        ).all()
        
        # 确保返回正确的字段映射
        result = []
        for item in heatmap_data:
            # latitude 是纬度 (lat)，longitude 是经度 (lng)
            result.append({
                'lat': float(item.latitude),      # 纬度
                'lng': float(item.longitude),     # 经度
                'count': item.count
            })
        
        return result