# 鸟类数据分析系统 - API接口文档

## 概述

本文档详细说明鸟类数据分析系统的RESTful API接口规范。

### 基础信息
- **API前缀**: `/api`
- **数据格式**: JSON
- **字符编码**: UTF-8
- **响应格式**: 统一返回格式

### 统一响应格式
```json
{
  "success": true,
  "data": {},
  "meta": {}
}
```

错误响应：
```json
{
  "success": false,
  "error": "错误描述信息"
}
```

## 接口列表

### 1. 获取统计指标
**接口**: `GET /api/stats`  
**描述**: 获取系统核心统计数据

#### 请求参数
无

#### 响应示例
```json
{
  "success": true,
  "data": {
    "species_count": 5,
    "total_individuals": 31,
    "endangered_count": 2,
    "completeness_rate": 114.3,
    "change_percent": 0,
    "last_updated": "2026-02-12T02:49:20.595617"
  }
}
```

#### 字段说明
| 字段名 | 类型 | 说明 |
|--------|------|------|
| species_count | integer | 物种总数 |
| total_individuals | integer | 个体总数 |
| endangered_count | integer | 濒危物种出现次数 |
| completeness_rate | float | 近7天数据完整率(%) |
| change_percent | float | 物种数量环比变化(%) |
| last_updated | string | 最后更新时间 |

---

### 2. 获取热力图数据
**接口**: `GET /api/heatmap`  
**描述**: 获取用于热力图可视化的观测点数据

#### 请求参数
| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| days | integer | 否 | 7 | 时间范围(天) |

#### 响应示例
```json
{
  "success": true,
  "data": [
    {
      "lat": 30.26,
      "lng": 120.12,
      "count": 6
    },
    {
      "lat": 30.18,
      "lng": 118.85,
      "count": 2
    }
  ],
  "meta": {
    "days": 7,
    "min_confidence": 0.7,
    "point_count": 2
  }
}
```

#### 字段说明
| 字段名 | 类型 | 说明 |
|--------|------|------|
| lat | float | 纬度 |
| lng | float | 经度 |
| count | integer | 该点观测次数 |
| meta.days | integer | 查询时间范围 |
| meta.min_confidence | float | 最小置信度阈值 |
| meta.point_count | integer | 返回数据点数量 |

---

### 3. 获取观测记录列表
**接口**: `GET /api/observations`  
**描述**: 分页获取观测记录列表

#### 请求参数
| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| page | integer | 否 | 1 | 页码 |
| limit | integer | 否 | 20 | 每页记录数 |

#### 响应示例
```json
{
  "success": true,
  "data": {
    "observations": [
      {
        "id": 8,
        "device_id": 1,
        "species": {
          "id": 4,
          "chinese_name": "白鹭",
          "english_name": "Little Egret",
          "scientific_name": "Egretta garzetta",
          "conservation_status": "LC",
          "is_endangered": false
        },
        "count": 6,
        "observed_at": "2026-02-28T13:25:09",
        "area": {
          "id": 1,
          "name": "西溪湿地核心区",
          "habitat_type": "wetland",
          "management_unit": "杭州西溪湿地管理局"
        },
        "longitude": 30.26,
        "latitude": 120.12,
        "confidence": 0.89,
        "status": "confirmed",
        "created_at": "2026-02-12T02:48:48.391766"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 5,
      "total": 8,
      "pages": 2,
      "has_next": true,
      "has_prev": false
    }
  }
}
```

---

### 4. 创建观测记录
**接口**: `POST /api/observations`  
**描述**: 添加新的观测记录

#### 请求参数 (JSON)
```json
{
  "device_id": 1,
  "species_id": 4,
  "count": 3,
  "confidence": 0.95,
  "image_path": "/path/to/image.jpg"
}
```

#### 参数说明
| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| device_id | integer | 是 | - | 设备ID |
| species_id | integer | 是 | - | 物种ID |
| count | integer | 是 | - | 观测数量(≥1) |
| confidence | float | 否 | 0.8 | AI识别置信度 |
| image_path | string | 否 | null | 图像文件路径 |

#### 响应示例
```json
{
  "success": true,
  "data": {
    "id": 9,
    "message": "观测记录创建成功"
  }
}
```

---

### 5. 获取物种列表
**接口**: `GET /api/species`  
**描述**: 获取所有物种信息（用于下拉选择）

#### 请求参数
无

#### 响应示例
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "chinese_name": "绿头鸭",
      "english_name": "Mallard",
      "scientific_name": "Anas platyrhynchos",
      "conservation_status": "LC",
      "migration_type": "winter_visitor",
      "is_endangered": false,
      "display_text": "绿头鸭 (LC)"
    },
    {
      "id": 2,
      "chinese_name": "东方白鹳",
      "english_name": "Oriental Stork",
      "scientific_name": "Ciconia boyciana",
      "conservation_status": "EN",
      "migration_type": "passage_migrant",
      "is_endangered": true,
      "display_text": "东方白鹳 ⚠️ EN"
    }
  ]
}
```

---

### 6. 获取设备列表
**接口**: `GET /api/devices`  
**描述**: 获取活跃设备列表（用于下拉选择）

#### 请求参数
无

#### 响应示例
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "serial_number": "CAM-XIXI-001",
      "model": "TrailCam Pro",
      "area_id": 1,
      "longitude": 30.26,
      "latitude": 120.12,
      "status": "active"
    }
  ]
}
```

## 错误码说明

| HTTP状态码 | 错误类型 | 说明 |
|------------|----------|------|
| 200 | Success | 请求成功 |
| 400 | Bad Request | 请求参数错误 |
| 404 | Not Found | 资源不存在 |
| 500 | Internal Server Error | 服务器内部错误 |

## CURL使用示例

### 获取统计数据
```bash
curl -X GET "http://localhost:5000/api/stats"
```

### 获取热力图数据
```bash
curl -X GET "http://localhost:5000/api/heatmap?days=7"
```

### 获取观测记录
```bash
curl -X GET "http://localhost:5000/api/observations?page=1&limit=5"
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

### 获取物种列表
```bash
curl -X GET "http://localhost:5000/api/species"
```

## 数据过滤规则

### 置信度过滤
- 默认阈值：0.7
- 只返回置信度 ≥ 0.7 的记录
- 可在配置文件中调整

### 状态过滤
- 默认只显示 "confirmed" 状态的记录
- pending/rejected 状态记录不参与统计

### 时间过滤
- 热力图支持 1天/7天/30天 三种时间范围
- 统计数据基于近7天完整率计算

## 性能优化建议

1. **分页查询**: 大量数据时使用分页参数
2. **缓存策略**: 统计数据可适当缓存(建议5-10分钟)
3. **索引优化**: 数据库已针对常用查询建立索引
4. **批量操作**: 多条记录建议批量插入

---
*©2025 | 本系统基于MySQL+Flask开发*