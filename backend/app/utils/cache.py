# -*- coding: utf-8 -*-
"""
简单的内存缓存工具
用于缓存统计数据等不频繁变化的数据
"""

import time
from functools import wraps
from flask import current_app

class SimpleCache:
    """简单的内存缓存实现"""
    
    def __init__(self, default_timeout=300):
        """
        初始化缓存
        
        Args:
            default_timeout: 默认缓存时间（秒），默认5分钟
        """
        self._cache = {}
        self._timeouts = {}
        self.default_timeout = default_timeout
    
    def get(self, key):
        """
        获取缓存值
        
        Args:
            key: 缓存键
            
        Returns:
            缓存值，如果不存在或已过期则返回None
        """
        if key in self._cache:
            # 检查是否过期
            if time.time() < self._timeouts.get(key, 0):
                return self._cache[key]
            else:
                # 过期，删除缓存
                self.delete(key)
        return None
    
    def set(self, key, value, timeout=None):
        """
        设置缓存值
        
        Args:
            key: 缓存键
            value: 缓存值
            timeout: 过期时间（秒），默认使用初始化时的默认值
        """
        if timeout is None:
            timeout = self.default_timeout
        
        self._cache[key] = value
        self._timeouts[key] = time.time() + timeout
    
    def delete(self, key):
        """删除缓存"""
        self._cache.pop(key, None)
        self._timeouts.pop(key, None)
    
    def clear(self):
        """清空所有缓存"""
        self._cache.clear()
        self._timeouts.clear()
    
    def get_stats(self):
        """获取缓存统计信息"""
        total = len(self._cache)
        expired = sum(1 for key in list(self._cache.keys()) 
                     if time.time() >= self._timeouts.get(key, 0))
        return {
            'total_keys': total,
            'expired_keys': expired,
            'active_keys': total - expired
        }


# 全局缓存实例
stats_cache = SimpleCache(default_timeout=300)  # 统计数据缓存5分钟
heatmap_cache = SimpleCache(default_timeout=60)  # 热力图数据缓存1分钟


def cached(cache_instance, key_prefix, timeout=None):
    """
    缓存装饰器
    
    使用示例：
        @cached(stats_cache, 'stats')
        def get_statistics():
            # 昂贵的查询操作
            return result
    
    Args:
        cache_instance: 缓存实例
        key_prefix: 缓存键前缀
        timeout: 缓存过期时间（秒）
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 生成缓存键
            cache_key = f"{key_prefix}:{str(args)}:{str(kwargs)}"
            
            # 尝试从缓存获取
            cached_value = cache_instance.get(cache_key)
            if cached_value is not None:
                current_app.logger.debug(f"Cache hit: {cache_key}")
                return cached_value
            
            # 执行原函数
            result = f(*args, **kwargs)
            
            # 存入缓存
            cache_instance.set(cache_key, result, timeout)
            current_app.logger.debug(f"Cache set: {cache_key}")
            
            return result
        return decorated_function
    return decorator


def invalidate_cache(cache_instance, key_prefix):
    """
    使缓存失效
    
    使用示例：
        invalidate_cache(stats_cache, 'stats')
    """
    # 简单实现：清除所有以key_prefix开头的缓存
    keys_to_delete = [key for key in list(cache_instance._cache.keys()) 
                     if key.startswith(key_prefix)]
    for key in keys_to_delete:
        cache_instance.delete(key)