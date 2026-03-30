# -*- coding: utf-8 -*-
"""
模拟数据生成脚本
用于插入大量测试数据到鸟类数据分析系统
"""

import os
import sys
import random
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app import create_app, db
from app.models import BirdSpecies, Area, Device, Observation, Image, Audio


def generate_mock_data(num_observations=500):
    """
    生成模拟观测数据
    
    Args:
        num_observations: 要生成的观测记录数量
    """
    app = create_app()
    
    with app.app_context():
        print('=' * 50)
        print('开始生成模拟数据...')
        print('=' * 50)
        
        # 获取现有数据
        species_list = BirdSpecies.query.all()
        areas = Area.query.all()
        devices = Device.query.all()
        
        if not species_list or not areas or not devices:
            print('错误：基础数据不完整，请先运行数据库初始化脚本')
            return
        
        print(f'基础数据: {len(species_list)}个物种, {len(areas)}个区域, {len(devices)}台设备')
        
        # 生成图像数据 (每条观测配0-1张图，约70%概率有图)
        print('\n生成图像数据...')
        images_to_create = int(num_observations * 0.7)
        for i in range(images_to_create):
            # 生成时间范围：最近60天
            days_ago = random.randint(0, 60)
            hours_ago = random.randint(0, 23)
            minutes_ago = random.randint(0, 59)
            snap_time = datetime.now() - timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago)
            
            img_num = (i % 1000) + 1
            img = Image(
                storage_path=f'data/images/IMA{img_num:06d}.jpg',
                dimensions=f'{random.choice([1920, 1280, 3840])}x{random.choice([1080, 720, 2160])}',
                file_size=random.randint(500000, 5000000),
                file_format='jpg',
                snap_time=snap_time
            )
            db.session.add(img)
        
        db.session.commit()
        print(f'已创建 {images_to_create} 条图像记录')
        
        # 生成音频数据 (约30%概率有音频)
        print('生成音频数据...')
        audios_to_create = int(num_observations * 0.3)
        for i in range(audios_to_create):
            days_ago = random.randint(0, 60)
            hours_ago = random.randint(0, 23)
            record_time = datetime.now() - timedelta(days=days_ago, hours=hours_ago)
            
            audio_num = (i % 1000) + 1
            audio = Audio(
                storage_path=f'data/audios/AUD{audio_num:06d}.mp3',
                record_start_time=record_time,
                duration=random.randint(5, 120),
                file_size=random.randint(100000, 2000000),
                file_format='mp3'
            )
            db.session.add(audio)
        
        db.session.commit()
        print(f'已创建 {audios_to_create} 条音频记录')
        
        # 获取新创建的图像和音频ID
        images = Image.query.all()
        audios = Audio.query.all()
        
        # 生成观测记录
        print(f'\n生成 {num_observations} 条观测记录...')
        
        # 地理范围：杭州西溪湿地区域
        lat_min, lat_max = 30.25, 30.28
        lon_min, lon_max = 120.10, 120.18
        
        # 定义热点位置（用于产生热力图效果）
        hotspots = [
            {'lat': 30.268, 'lng': 120.065},  # 西溪湿地中心
            {'lat': 30.270, 'lng': 120.070},  # 北区
            {'lat': 30.265, 'lng': 120.075},  # 东区
            {'lat': 30.262, 'lng': 120.080},  # 南区
            {'lat': 30.275, 'lng': 120.140},  # 清凉峰方向
        ]
        hotspot_radius = 0.003  # 热点半径（约300米）
        
        created_count = 0
        
        for i in range(num_observations):
            # 随机选择物种、区域、设备
            species = random.choice(species_list)
            area = random.choice(areas)
            device = random.choice(devices)
            
            # 生成观测时间
            days_ago = random.randint(0, 60)
            hours_ago = random.randint(0, 23)
            minutes_ago = random.randint(0, 59)
            observed_at = datetime.now() - timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago)
            
            # 生成地理坐标 - 70%概率聚集在热点
            if random.random() < 0.7:
                # 选择一个热点
                hotspot = random.choice(hotspots)
                # 在热点附近随机偏移
                latitude = round(hotspot['lat'] + random.uniform(-hotspot_radius, hotspot_radius), 6)
                longitude = round(hotspot['lng'] + random.uniform(-hotspot_radius, hotspot_radius), 6)
            else:
                # 随机分布在整个区域
                latitude = round(random.uniform(lat_min, lat_max), 6)
                longitude = round(random.uniform(lon_min, lon_max), 6)
            
            # 置信度 0.65-0.98
            confidence = round(random.uniform(0.65, 0.98), 2)
            
            # 状态分布：70% confirmed, 25% pending, 5% rejected
            status_rand = random.random()
            if status_rand < 0.70:
                status = 'confirmed'
            elif status_rand < 0.95:
                status = 'pending'
            else:
                status = 'rejected'
            
            # 鸟类数量 1-10
            count = random.randint(1, 10)
            
            # 关联图像（约70%概率）
            image_id = None
            if random.random() < 0.7 and images:
                image_id = random.choice(images).id
            
            # 关联音频（约30%概率）
            audio_id = None
            if random.random() < 0.3 and audios:
                audio_id = random.choice(audios).id
            
            # 创建观测记录
            observation = Observation(
                device_id=device.id,
                image_id=image_id,
                audio_id=audio_id,
                species_id=species.id,
                count=count,
                observed_at=observed_at,
                area_id=area.id,
                longitude=longitude,
                latitude=latitude,
                confidence=confidence,
                status=status
            )
            db.session.add(observation)
            
            # 每100条提交一次
            if (i + 1) % 100 == 0:
                db.session.commit()
                print(f'  已完成 {i + 1}/{num_observations} 条...')
        
        # 最后提交剩余数据
        db.session.commit()
        
        print('\n' + '=' * 50)
        print('数据生成完成！')
        print('=' * 50)
        
        # 打印统计信息
        print('\n=== 最终数据库状态 ===')
        print(f'鸟类物种: {BirdSpecies.query.count()} 条')
        print(f'区域: {Area.query.count()} 条')
        print(f'设备: {Device.query.count()} 条')
        print(f'图像: {Image.query.count()} 条')
        print(f'音频: {Audio.query.count()} 条')
        print(f'观测记录: {Observation.query.count()} 条')
        
        # 统计濒危物种观测数
        endangered_count = Observation.query.join(BirdSpecies).filter(
            BirdSpecies.conservation_status.in_(['EN', 'CR', 'VU'])
        ).count()
        print(f'\n濒危物种观测记录: {endangered_count} 条')
        
        # 状态分布
        confirmed = Observation.query.filter_by(status='confirmed').count()
        pending = Observation.query.filter_by(status='pending').count()
        rejected = Observation.query.filter_by(status='rejected').count()
        print(f'状态分布: confirmed={confirmed}, pending={pending}, rejected={rejected}')


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='生成模拟观测数据')
    parser.add_argument('-n', '--number', type=int, default=500, 
                        help='要生成的观测记录数量 (默认: 500)')
    args = parser.parse_args()
    
    generate_mock_data(args.number)
