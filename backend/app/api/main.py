# -*- coding: utf-8 -*-
"""
主要API路由
实现统计、热力图、观测记录等核心接口
"""

from flask import jsonify, request, current_app
from app.api import bp
from app import db
from app.models import BirdSpecies, Area, Device, Observation, Image
from app.utils.cache import stats_cache, heatmap_cache, cached, invalidate_cache
from sqlalchemy import func
from datetime import datetime, timedelta
import os


# 缓存键常量
CACHE_KEY_STATS = 'api:stats'
CACHE_KEY_HEATMAP = 'api:heatmap'


@bp.route('/stats')
def get_statistics():
    """
    获取系统统计数据（带缓存优化）
    返回：物种数量、个体总数、濒危物种次数、数据完整率
    
    性能优化：
    1. 使用内存缓存，5分钟过期
    2. 缓存键包含时间戳（按分钟取整），确保数据及时更新
    """
    try:
        # 生成缓存键（按5分钟取整，确保缓存一致性）
        cache_key = f"{CACHE_KEY_STATS}:{datetime.utcnow().strftime('%Y%m%d%H%M')[:-1]}"
        
        # 尝试从缓存获取
        cached_result = stats_cache.get(cache_key)
        if cached_result is not None:
            current_app.logger.debug(f"统计数据缓存命中: {cache_key}")
            return cached_result
        
        # 基础统计数据
        species_count = BirdSpecies.query.count()
        
        # 个体总数（只统计已确认的记录）
        total_individuals = db.session.query(func.sum(Observation.count)).filter(
            Observation.status == 'confirmed'
        ).scalar() or 0
        
        # 濒危物种出现次数（优化：使用JOIN和IN查询）
        endangered_count = db.session.query(func.count(Observation.id)).join(
            BirdSpecies, Observation.species_id == BirdSpecies.id
        ).filter(
            BirdSpecies.conservation_status.in_(['EN', 'CR', 'VU']),
            Observation.status == 'confirmed'
        ).scalar() or 0
        
        # 近7天数据完整率计算
        # 修正：使用正确的日期去重方式
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        total_days = 7
        
        # 查询近7天内有观测数据的 distinct 日期（使用 SQLite 的 date 函数）
        observed_days_result = db.session.query(
            func.count(func.distinct(func.strftime('%Y-%m-%d', Observation.observed_at)))
        ).filter(
            Observation.observed_at >= seven_days_ago,
            Observation.status == 'confirmed'
        ).scalar()
        
        observed_days = observed_days_result or 0
        # 确保完整率不超过100%
        completeness_rate = min(round((observed_days / total_days) * 100, 1), 100.0)
        
        # 计算环比变化（与上周相比）
        two_weeks_ago = datetime.utcnow() - timedelta(days=14)
        last_week_species = db.session.query(func.count(func.distinct(Observation.species_id))).filter(
            Observation.observed_at >= two_weeks_ago,
            Observation.observed_at < seven_days_ago,
            Observation.status == 'confirmed'
        ).scalar() or 0
        
        # 环比变化百分比
        if last_week_species > 0:
            change_percent = round(((species_count - last_week_species) / last_week_species) * 100, 1)
        else:
            change_percent = 0
        
        result = jsonify({
            'success': True,
            'data': {
                'species_count': species_count,
                'total_individuals': int(total_individuals),
                'endangered_count': endangered_count,
                'completeness_rate': completeness_rate,
                'change_percent': change_percent,
                'last_updated': datetime.utcnow().isoformat(),
                'cached': False  # 标识数据是否来自缓存
            }
        })
        
        # 存入缓存（5分钟）
        stats_cache.set(cache_key, result, timeout=300)
        current_app.logger.debug(f"统计数据已缓存: {cache_key}")
        
        return result
        
    except Exception as e:
        current_app.logger.error(f"获取统计数据失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': '获取统计数据失败',
            'message': '服务器内部错误，请稍后重试'
        }), 500


@bp.route('/heatmap')
def get_heatmap_data():
    """
    获取热力图数据（带缓存优化）
    参数：
        days: 时间范围（默认7天）
    
    性能优化：
    1. 使用内存缓存，1分钟过期
    2. 相同参数的请求直接返回缓存数据
    """
    try:
        # 获取参数
        days = request.args.get('days', type=int, default=current_app.config['DEFAULT_TIME_RANGE_DAYS'])
        
        # 参数验证
        if days not in [1, 7, 30]:
            days = 7
        
        # 生成缓存键
        cache_key = f"{CACHE_KEY_HEATMAP}:{days}"
        
        # 尝试从缓存获取
        cached_result = heatmap_cache.get(cache_key)
        if cached_result is not None:
            current_app.logger.debug(f"热力图数据缓存命中: {cache_key}")
            return cached_result
            
        # 获取热力图数据（使用优化后的查询方法）
        heatmap_data = Observation.get_heatmap_data(
            days=days,
            min_confidence=current_app.config['MIN_CONFIDENCE_THRESHOLD']
        )
        
        result = jsonify({
            'success': True,
            'data': heatmap_data,
            'meta': {
                'days': days,
                'min_confidence': current_app.config['MIN_CONFIDENCE_THRESHOLD'],
                'point_count': len(heatmap_data),
                'cached': False
            }
        })
        
        # 存入缓存（1分钟）
        heatmap_cache.set(cache_key, result, timeout=60)
        current_app.logger.debug(f"热力图数据已缓存: {cache_key}")
        
        return result
        
    except Exception as e:
        current_app.logger.error(f"获取热力图数据失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': '获取热力图数据失败',
            'message': '服务器内部错误，请稍后重试'
        }), 500


@bp.route('/observations')
def get_observations():
    """
    获取观测记录列表（分页）
    参数：
        page: 页码（默认1）
        limit: 每页数量（默认20）
        device_id: 设备ID筛选（可选）
        species_id: 物种ID筛选（可选）
        area_id: 区域ID筛选（可选）
        endangered: 只显示濒危物种（可选，true/false）
    """
    try:
        # 获取分页参数
        page = request.args.get('page', type=int, default=1)
        limit = request.args.get('limit', type=int, default=current_app.config['DEFAULT_PAGE_SIZE'])
        device_id = request.args.get('device_id', type=int, default=None)
        species_id = request.args.get('species_id', type=int, default=None)
        area_id = request.args.get('area_id', type=int, default=None)
        endangered = request.args.get('endangered', type=str, default=None)

        # 参数验证
        if limit > current_app.config['MAX_PAGE_SIZE']:
            limit = current_app.config['MAX_PAGE_SIZE']

        # 查询观测记录（按时间倒序）
        query = Observation.query.filter(
            Observation.status == 'confirmed'
        )

        # 如果有device_id筛选条件
        if device_id:
            query = query.filter(Observation.device_id == device_id)

        # 如果有species_id筛选条件
        if species_id:
            query = query.filter(Observation.species_id == species_id)

        # 如果有area_id筛选条件
        if area_id:
            query = query.filter(Observation.area_id == area_id)

        # 如果只显示濒危物种
        if endangered == 'true':
            query = query.join(
                BirdSpecies, Observation.species_id == BirdSpecies.id
            ).filter(
                BirdSpecies.conservation_status.in_(['EN', 'CR', 'VU'])
            )

        query = query.order_by(Observation.observed_at.desc())

        # 分页
        pagination = query.paginate(
            page=page,
            per_page=limit,
            error_out=False
        )

        # 转换为字典格式
        observations = [obs.to_dict() for obs in pagination.items]

        return jsonify({
            'success': True,
            'data': {
                'observations': observations,
                'pagination': {
                    'page': page,
                    'limit': limit,
                    'total': pagination.total,
                    'pages': pagination.pages,
                    'has_next': pagination.has_next,
                    'has_prev': pagination.has_prev
                }
            }
        })

    except Exception as e:
        current_app.logger.error(f"获取观测记录失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': '获取观测记录失败'
        }), 500


@bp.route('/observations', methods=['POST'])
def create_observation():
    """
    创建新的观测记录
    请求体应包含：
    {
        "device_id": 1,
        "species_id": 2,
        "count": 1,
        "image_path": "/path/to/image.jpg",  # 可选
        "confidence": 0.95  # 可选，默认0.8
    }
    """
    try:
        data = request.get_json()
        
        # 必填字段验证
        required_fields = ['device_id', 'species_id', 'count']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({
                    'success': False,
                    'error': f'缺少必要字段: {field}'
                }), 400
        
        # 验证设备是否存在
        device = Device.query.get(data['device_id'])
        if not device:
            return jsonify({
                'success': False,
                'error': '设备不存在'
            }), 404
            
        # 验证物种是否存在
        species = BirdSpecies.query.get(data['species_id'])
        if not species:
            return jsonify({
                'success': False,
                'error': '物种不存在'
            }), 404
            
        # 验证数量
        count = int(data['count'])
        if count <= 0:
            return jsonify({
                'success': False,
                'error': '数量必须大于0'
            }), 400
            
        # 创建图像记录（如果提供了图像路径）
        image_id = None
        if 'image_path' in data and data['image_path']:
            # 这里简化处理，实际应该处理文件上传
            image = Image(
                storage_path=data['image_path'],
                snap_time=datetime.utcnow()  # 简化处理，实际应该从图像EXIF获取
            )
            db.session.add(image)
            db.session.flush()  # 获取image.id
            image_id = image.id
        
        # 创建观测记录
        observation = Observation(
            device_id=data['device_id'],
            image_id=image_id,
            species_id=data['species_id'],
            count=count,
            observed_at=datetime.utcnow(),  # 简化处理
            area_id=device.area_id,
            longitude=device.longitude,
            latitude=device.latitude,
            confidence=float(data.get('confidence', 0.8)),
            status='pending'  # 默认待确认
        )
        
        db.session.add(observation)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': {
                'id': observation.id,
                'message': '观测记录创建成功'
            }
        }), 201
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': '数据格式错误'
        }), 400
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"创建观测记录失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': '创建观测记录失败'
        }), 500


@bp.route('/species')
def get_species_list():
    """
    获取物种列表（用于下拉框）
    """
    try:
        species_list = BirdSpecies.query.all()
        result = []
        
        for species in species_list:
            species_dict = species.to_dict()
            # 添加显示文本（包含保护级别标识）
            if species.is_endangered():
                species_dict['display_text'] = f"{species.chinese_name} ⚠️ {species.conservation_status}"
            else:
                species_dict['display_text'] = f"{species.chinese_name} ({species.conservation_status})"
                
            result.append(species_dict)
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        current_app.logger.error(f"获取物种列表失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': '获取物种列表失败'
        }), 500


@bp.route('/species/<int:species_id>')
def get_species_detail(species_id):
    """
    获取单个物种详情
    """
    try:
        species = BirdSpecies.query.get(species_id)
        
        if not species:
            return jsonify({
                'success': False,
                'error': '物种不存在'
            }), 404
        
        return jsonify({
            'success': True,
            'data': species.to_dict()
        })
        
    except Exception as e:
        current_app.logger.error(f"获取物种详情失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': '获取物种详情失败'
        }), 500


@bp.route('/devices')
def get_devices_list():
    """
    获取设备列表（用于下拉框）
    """
    try:
        devices = Device.query.filter(Device.status == 'active').all()
        result = [device.to_dict() for device in devices]
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        current_app.logger.error(f"获取设备列表失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': '获取设备列表失败'
        }), 500


@bp.route('/devices/<int:device_id>')
def get_device_detail(device_id):
    """
    获取单个设备详情
    """
    try:
        device = Device.query.get(device_id)

        if not device:
            return jsonify({
                'success': False,
                'error': '设备不存在'
            }), 404

        return jsonify({
            'success': True,
            'data': device.to_dict()
        })

    except Exception as e:
        current_app.logger.error(f"获取设备详情失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': '获取设备详情失败'
        }), 500


@bp.route('/areas/<int:area_id>')
def get_area_detail(area_id):
    """
    获取单个区域详情
    """
    try:
        area = Area.query.get(area_id)

        if not area:
            return jsonify({
                'success': False,
                'error': '区域不存在'
            }), 404

        # 获取该区域的观测统计
        stats = db.session.query(
            func.count(Observation.id).label('observation_count'),
            func.sum(Observation.count).label('individual_count'),
            func.count(func.distinct(Observation.species_id)).label('species_count')
        ).filter(
            Observation.area_id == area_id,
            Observation.status == 'confirmed'
        ).first()

        area_data = area.to_dict()
        area_data['stats'] = {
            'observation_count': stats.observation_count or 0,
            'individual_count': int(stats.individual_count or 0),
            'species_count': stats.species_count or 0
        }

        return jsonify({
            'success': True,
            'data': area_data
        })

    except Exception as e:
        current_app.logger.error(f"获取区域详情失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': '获取区域详情失败'
        }), 500


@bp.route('/stats/species-distribution')
def get_species_distribution():
    """
    获取物种分布数据（用于饼图）
    返回各物种的观测次数占比
    """
    try:
        # 查询各物种的观测次数
        distribution = db.session.query(
            BirdSpecies.id,
            BirdSpecies.chinese_name,
            BirdSpecies.conservation_status,
            func.count(Observation.id).label('count')
        ).join(
            Observation, Observation.species_id == BirdSpecies.id
        ).filter(
            Observation.status == 'confirmed'
        ).group_by(
            BirdSpecies.id, BirdSpecies.chinese_name, BirdSpecies.conservation_status
        ).all()
        
        # 整理数据
        data = []
        total = sum([d.count for d in distribution])
        for item in distribution:
            # 根据保护级别设置颜色
            color = '#27ae60'  # 默认绿色
            if item.conservation_status in ['EN', 'CR']:
                color = '#e74c3c'  # 红色-极危/濒危
            elif item.conservation_status == 'VU':
                color = '#f39c12'  # 橙色-易危
            elif item.conservation_status == 'NT':
                color = '#3498db'  # 蓝色-近危
            
            data.append({
                'species_id': item.id,
                'name': item.chinese_name,
                'value': item.count,
                'percentage': round(item.count / total * 100, 1) if total > 0 else 0,
                'conservation_status': item.conservation_status,
                'color': color
            })
        
        # 按观测次数排序
        data.sort(key=lambda x: x['value'], reverse=True)
        
        return jsonify({
            'success': True,
            'data': data,
            'meta': {
                'total_observations': total,
                'species_count': len(data)
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"获取物种分布数据失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': '获取物种分布数据失败'
        }), 500


@bp.route('/stats/trend')
def get_trend_data():
    """
    获取观测趋势数据（用于折线图）
    返回近N天的每日观测次数
    """
    try:
        days = request.args.get('days', type=int, default=7)
        if days not in [7, 14, 30]:
            days = 7
        
        # 查询每日观测次数
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # 使用SQLite的date函数按日期分组
        daily_data = db.session.query(
            func.strftime('%Y-%m-%d', Observation.observed_at).label('date'),
            func.count(Observation.id).label('count'),
            func.sum(Observation.count).label('individuals')
        ).filter(
            Observation.observed_at >= start_date,
            Observation.status == 'confirmed'
        ).group_by(
            func.strftime('%Y-%m-%d', Observation.observed_at)
        ).order_by(
            func.strftime('%Y-%m-%d', Observation.observed_at)
        ).all()
        
        # 转换为日期格式
        dates = []
        counts = []
        individuals = []
        
        for item in daily_data:
            dates.append(item.date)
            counts.append(item.count)
            individuals.append(int(item.individuals or 0))
        
        # 如果没有数据，生成模拟数据（用于演示）
        if not dates:
            from datetime import date as date_type
            for i in range(days - 1, -1, -1):
                d = date_type.today() - timedelta(days=i)
                dates.append(d.strftime('%Y-%m-%d'))
                counts.append(0)
                individuals.append(0)
        
        return jsonify({
            'success': True,
            'data': {
                'dates': dates,
                'observation_counts': counts,
                'individual_counts': individuals
            },
            'meta': {
                'days': days,
                'total_observations': sum(counts),
                'total_individuals': sum(individuals)
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"获取趋势数据失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': '获取趋势数据失败'
        }), 500


@bp.route('/stats/area-distribution')
def get_area_distribution():
    """
    获取区域分布数据（用于柱状图）
    返回各区域的观测次数
    """
    try:
        # 查询各区域的观测次数
        distribution = db.session.query(
            Area.id,
            Area.name,
            Area.habitat_type,
            func.count(Observation.id).label('count'),
            func.sum(Observation.count).label('individuals')
        ).join(
            Observation, Observation.area_id == Area.id
        ).filter(
            Observation.status == 'confirmed'
        ).group_by(
            Area.id, Area.name, Area.habitat_type
        ).all()

        # 整理数据
        data = []
        for item in distribution:
            # 根据生境类型设置颜色
            color = '#3498db'  # 默认蓝色
            habitat_colors = {
                'wetland': '#3498db',    # 蓝色-湿地
                'forest': '#27ae60',     # 绿色-森林
                'grassland': '#f1c40f',  # 黄色-草地
                'farmland': '#e67e22',   # 橙色-农田
                'urban': '#9b59b6',      # 紫色-城市
                'others': '#95a5a6'      # 灰色-其他
            }
            color = habitat_colors.get(item.habitat_type, '#95a5a6')

            habitat_names = {
                'wetland': '湿地',
                'forest': '森林',
                'grassland': '草地',
                'farmland': '农田',
                'urban': '城市',
                'others': '其他'
            }

            data.append({
                'area_id': item.id,
                'name': item.name,
                'habitat_type': habitat_names.get(item.habitat_type, item.habitat_type),
                'count': item.count,
                'individuals': int(item.individuals or 0),
                'color': color
            })

        # 按观测次数排序
        data.sort(key=lambda x: x['count'], reverse=True)

        return jsonify({
            'success': True,
            'data': data,
            'meta': {
                'total_observations': sum([d['count'] for d in data]),
                'area_count': len(data)
            }
        })

    except Exception as e:
        current_app.logger.error(f"获取区域分布数据失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': '获取区域分布数据失败'
        }), 500


@bp.route('/observations/<int:id>')
def get_observation_detail(id):
    """
    获取观测记录详情
    返回单条观测记录的完整信息
    """
    try:
        observation = Observation.query.get(id)
        
        if not observation:
            return jsonify({
                'success': False,
                'error': '观测记录不存在'
            }), 404
        
        # 辅助函数：将相对路径转换为完整URL
        def get_full_url(storage_path):
            if not storage_path:
                return None
            # 将反斜杠替换为正斜杠，并确保路径以/开头
            path = storage_path.replace('\\', '/')
            if not path.startswith('/'):
                path = '/' + path
            return path
        
        # 构建完整详情
        detail = {
            'id': observation.id,
            'observed_at': observation.observed_at.isoformat() if observation.observed_at else None,
            'count': observation.count,
            'confidence': observation.confidence,
            'status': observation.status,
            'longitude': float(observation.longitude),
            'latitude': float(observation.latitude),
            'created_at': observation.created_at.isoformat() if observation.created_at else None,
            # 物种信息
            'species': observation.species.to_dict() if observation.species else None,
            # 区域信息
            'area': observation.area.to_dict() if observation.area else None,
            # 设备信息
            'device': {
                'id': observation.device.id,
                'serial_number': observation.device.serial_number,
                'model': observation.device.model,
                'status': observation.device.status
            } if observation.device else None,
            # 图像信息 - 转换为完整URL
            'image': {
                'id': observation.image.id,
                'storage_path': get_full_url(observation.image.storage_path),
                'snap_time': observation.image.snap_time.isoformat() if observation.image.snap_time else None
            } if observation.image else None,
            # 音频信息 - 转换为完整URL
            'audio': {
                'id': observation.audio.id,
                'storage_path': get_full_url(observation.audio.storage_path),
                'duration': observation.audio.duration
            } if observation.audio else None
        }
        
        # 添加物种扩展信息
        if observation.species:
            detail['species']['is_endangered'] = observation.species.is_endangered()
            detail['species']['conservation_status_text'] = {
                'LC': '无危',
                'NT': '近危',
                'VU': '易危',
                'EN': '濒危',
                'CR': '极危',
                'EW': '野外灭绝',
                'EX': '灭绝'
            }.get(observation.species.conservation_status, observation.species.conservation_status)
            
            # 迁徙类型
            migration_types = {
                'resident': '留鸟',
                'summer_breeder': '夏候鸟',
                'winter_visitor': '冬候鸟',
                'passage_migrant': '旅鸟',
                'vagrant': '迷鸟'
            }
            detail['species']['migration_type_text'] = migration_types.get(
                observation.species.migration_type, 
                observation.species.migration_type or '未知'
            )
        
        return jsonify({
            'success': True,
            'data': detail
        })
        
    except Exception as e:
        current_app.logger.error(f"获取观测记录详情失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': '获取观测记录详情失败'
        }), 500


@bp.route('/devices/with-stats')
def get_devices_with_stats():
    """
    获取设备列表及其观测统计数据
    用于热力图上的设备位置标记和统计
    """
    try:
        # 获取时间范围参数
        days = request.args.get('days', type=int, default=7)
        if days not in [1, 7, 14, 30]:
            days = 7
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # 获取所有活跃设备
        devices = Device.query.filter(Device.status == 'active').all()
        
        result = []
        for device in devices:
            # 查询该设备的观测统计
            stats = db.session.query(
                func.count(Observation.id).label('total_count'),
                func.sum(Observation.count).label('total_individuals')
            ).filter(
                Observation.device_id == device.id,
                Observation.observed_at >= start_date,
                Observation.status == 'confirmed'
            ).first()
            
            # 按物种统计
            species_stats = db.session.query(
                BirdSpecies.chinese_name,
                func.count(Observation.id).label('count')
            ).join(
                Observation, Observation.species_id == BirdSpecies.id
            ).filter(
                Observation.device_id == device.id,
                Observation.observed_at >= start_date,
                Observation.status == 'confirmed'
            ).group_by(
                BirdSpecies.id, BirdSpecies.chinese_name
            ).all()
            
            species_list = [{'name': s.chinese_name, 'count': s.count} for s in species_stats]
            
            result.append({
                'id': device.id,
                'serial_number': device.serial_number,
                'model': device.model,
                'longitude': float(device.longitude),
                'latitude': float(device.latitude),
                'area_name': device.area.name if device.area else None,
                'stats': {
                    'observation_count': stats.total_count or 0,
                    'individual_count': int(stats.total_individuals or 0)
                },
                'species_list': species_list
            })
        
        return jsonify({
            'success': True,
            'data': result,
            'meta': {
                'days': days,
                'device_count': len(result)
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"获取设备统计失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': '获取设备统计失败'
        }), 500


@bp.route('/observations/by-device/<int:device_id>')
def get_observations_by_device(device_id):
    """
    获取指定设备的观测记录列表
    """
    try:
        page = request.args.get('page', type=int, default=1)
        limit = request.args.get('limit', type=int, default=20)
        
        if limit > 100:
            limit = 100
        
        query = Observation.query.filter(
            Observation.device_id == device_id
        ).order_by(Observation.observed_at.desc())
        
        pagination = query.paginate(
            page=page,
            per_page=limit,
            error_out=False
        )
        
        observations = [obs.to_dict() for obs in pagination.items]
        
        # 获取设备信息
        device = Device.query.get(device_id)
        device_info = None
        if device:
            device_info = {
                'id': device.id,
                'serial_number': device.serial_number,
                'model': device.model,
                'area_name': device.area.name if device.area else None
            }
        
        return jsonify({
            'success': True,
            'data': {
                'observations': observations,
                'device': device_info,
                'pagination': {
                    'page': page,
                    'limit': limit,
                    'total': pagination.total,
                    'pages': pagination.pages,
                    'has_next': pagination.has_next,
                    'has_prev': pagination.has_prev
                }
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"获取设备观测记录失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': '获取设备观测记录失败'
        }), 500