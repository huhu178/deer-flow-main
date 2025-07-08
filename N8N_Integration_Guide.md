# 🔗 Deer-Flow AI研究系统 n8n集成指南

## 📋 概述

本指南详细说明如何将Deer-Flow AI研究系统集成到n8n工作流自动化平台中，实现AI研究报告的自动化生成、管理和分发。

## 🚀 快速开始

### 1. 基础配置

在n8n中添加HTTP Request节点，配置基础参数：

```json
{
  "method": "POST",
  "url": "http://your-server:8000/api/reports/webhook/n8n",
  "headers": {
    "Content-Type": "application/json",
    "Accept": "application/json"
  }
}
```

### 2. 认证设置（可选）

如果启用了API认证，添加Header：

```json
{
  "Authorization": "Bearer YOUR_API_TOKEN"
}
```

## 🔧 API接口详解

### 📄 1. 创建报告

**用途**：生成新的AI研究报告

**n8n配置**：
```json
{
  "method": "POST",
  "url": "http://your-server:8000/api/reports/create",
  "body": {
    "report_id": "research_{{ $now.format('YYYYMMDD_HHmmss') }}",
    "content": "{{ $node.data.generated_content }}",
    "metadata": {
      "author": "AI System",
      "type": "research",
      "topic": "{{ $node.data.topic }}",
      "created_by": "n8n_workflow"
    }
  }
}
```

**返回示例**：
```json
{
  "success": true,
  "message": "报告创建成功",
  "data": {
    "id": "research_20241227_145230",
    "filename": "research_20241227_145230_20241227_145230.md",
    "size": 15420,
    "hash": "a1b2c3d4e5f6...",
    "created_time": "20241227_145230",
    "word_count": 2580,
    "char_count": 15420
  }
}
```

### 📋 2. 列出所有报告

**用途**：获取报告列表，用于监控和管理

**n8n配置**：
```json
{
  "method": "GET",
  "url": "http://your-server:8000/api/reports/list?limit=50&offset=0&format=json"
}
```

**返回示例**：
```json
{
  "success": true,
  "data": {
    "reports": [
      {
        "id": "research_20241227_145230",
        "filename": "research_20241227_145230_20241227_145230.md",
        "size": 15420,
        "created_time": "20241227_145230",
        "word_count": 2580,
        "metadata": {"type": "research", "topic": "AI Healthcare"}
      }
    ],
    "total": 1,
    "limit": 50,
    "offset": 0
  }
}
```

### 🔍 3. 搜索报告

**用途**：根据关键词搜索相关报告

**n8n配置**：
```json
{
  "method": "POST",
  "url": "http://your-server:8000/api/reports/search",
  "body": {
    "query": "{{ $node.data.search_keywords }}",
    "limit": 20
  }
}
```

### 📥 4. 获取报告内容

**用途**：获取特定报告的详细信息和内容

**n8n配置**：
```json
{
  "method": "GET",
  "url": "http://your-server:8000/api/reports/{{ $node.data.report_id }}?include_content=true"
}
```

### 📥 5. 下载报告文件

**用途**：下载报告文件到本地或发送给其他系统

**n8n配置**：
```json
{
  "method": "GET",
  "url": "http://your-server:8000/api/reports/{{ $node.data.report_id }}/download?format=md"
}
```

支持的格式：
- `md`: Markdown格式
- `json`: JSON格式（包含元数据）
- `txt`: 纯文本格式

### 📊 6. 获取统计信息

**用途**：监控报告生成情况和系统使用状态

**n8n配置**：
```json
{
  "method": "GET",
  "url": "http://your-server:8000/api/reports/stats"
}
```

**返回示例**：
```json
{
  "success": true,
  "data": {
    "total_reports": 156,
    "total_size_mb": 45.2,
    "total_words": 125000,
    "average_report_size": 290240.0,
    "daily_stats": {
      "20241227": 12,
      "20241226": 8,
      "20241225": 15
    },
    "storage_path": "./outputs/reports"
  }
}
```

### 🗑️ 7. 删除报告

**用途**：清理不需要的报告

**n8n配置**：
```json
{
  "method": "DELETE",
  "url": "http://your-server:8000/api/reports/{{ $node.data.report_id }}"
}
```

## 🔄 n8n Webhook统一接口

为了简化n8n集成，系统提供了统一的Webhook接口，支持所有操作：

**基础URL**：`http://your-server:8000/api/reports/webhook/n8n`

### 使用示例

#### 1. 创建报告
```json
{
  "action": "create",
  "data": {
    "report_id": "test_001",
    "content": "# AI研究报告\n\n这是一个测试报告...",
    "metadata": {
      "type": "test",
      "author": "n8n_bot"
    }
  }
}
```

#### 2. 获取报告
```json
{
  "action": "get",
  "data": {
    "report_id": "test_001",
    "include_content": true
  }
}
```

#### 3. 搜索报告
```json
{
  "action": "search",
  "data": {
    "query": "AI healthcare",
    "limit": 10
  }
}
```

#### 4. 列出报告
```json
{
  "action": "list",
  "data": {
    "limit": 20,
    "offset": 0
  }
}
```

#### 5. 删除报告
```json
{
  "action": "delete",
  "data": {
    "report_id": "test_001"
  }
}
```

#### 6. 获取统计
```json
{
  "action": "stats",
  "data": {}
}
```

## 🔧 n8n工作流示例

### 示例1：自动生成日报

```yaml
name: "AI研究日报生成"
trigger: "Schedule (每日上午9点)"
steps:
  1. HTTP Request - 获取昨日报告统计
     URL: GET /api/reports/stats
     
  2. 条件判断 - 检查是否有新报告
     条件: {{ $node.data.daily_stats[yesterday] > 0 }}
     
  3. HTTP Request - 搜索昨日报告
     URL: POST /api/reports/search
     Body: {"query": "{{ yesterday }}", "limit": 50}
     
  4. 数据处理 - 汇总报告信息
     处理: 提取报告标题、摘要、关键词
     
  5. HTTP Request - 创建日报
     URL: POST /api/reports/create
     Body: {"report_id": "daily_{{ yesterday }}", "content": "{{ 汇总内容 }}"}
     
  6. 邮件发送 - 发送日报
     收件人: research-team@company.com
     附件: 下载生成的日报文件
```

### 示例2：智能报告分发

```yaml
name: "智能报告分发"
trigger: "Webhook (报告创建时触发)"
steps:
  1. HTTP Request - 获取新报告
     URL: GET /api/reports/{{ $webhook.report_id }}?include_content=true
     
  2. AI分析 - 分析报告主题和重要性
     使用: OpenAI/Claude分析内容
     输出: 主题标签、重要性评分、目标受众
     
  3. 条件分支 - 根据重要性分发
     高重要性: 立即发送给高管
     中重要性: 加入周报汇总
     低重要性: 存档备查
     
  4. 多渠道发送:
     - 邮件: 发送给相关团队
     - Slack: 发布到相关频道
     - 企业微信: 推送给相关群组
     
  5. HTTP Request - 更新报告元数据
     URL: 更新分发状态和受众信息
```

### 示例3：批量报告处理

```yaml
name: "批量报告质量检查"
trigger: "Manual/Schedule"
steps:
  1. HTTP Request - 获取所有报告
     URL: GET /api/reports/list?limit=1000
     
  2. 循环处理每个报告:
     2.1. 下载报告内容
     2.2. AI质量评估（语法、结构、完整性）
     2.3. 生成质量评分
     2.4. 标记需要改进的报告
     
  3. 汇总质量报告
     创建: 质量检查总结报告
     包含: 问题报告列表、改进建议
     
  4. 自动修复 (可选)
     对于轻微问题: 自动修正格式、语法
     对于严重问题: 标记人工审核
```

## 🔐 安全配置

### 1. API密钥认证

```javascript
// n8n Custom Function节点
const apiKey = $credentials('deer_flow_api').api_key;
return {
  headers: {
    'Authorization': `Bearer ${apiKey}`,
    'Content-Type': 'application/json'
  }
};
```

### 2. IP白名单

在服务器配置中限制API访问：

```python
# app.py
ALLOWED_IPS = ['192.168.1.100', '10.0.0.50']  # n8n服务器IP

@app.middleware("http")
async def check_ip(request: Request, call_next):
    client_ip = request.client.host
    if client_ip not in ALLOWED_IPS:
        raise HTTPException(status_code=403, detail="IP not allowed")
    return await call_next(request)
```

### 3. 速率限制

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/reports/create")
@limiter.limit("10/minute")  # 每分钟最多10次请求
async def create_report(request: Request, ...):
    # 创建报告逻辑
```

## 🐛 错误处理

### 常见错误代码

- `400`: 请求参数错误
- `401`: 认证失败
- `403`: 权限不足
- `404`: 报告不存在
- `429`: 请求过于频繁
- `500`: 服务器内部错误

### n8n错误处理示例

```javascript
// Error处理节点
if ($node.data.success === false) {
  // 记录错误日志
  console.error('API调用失败:', $node.data.error);
  
  // 发送告警通知
  return {
    action: 'send_alert',
    message: `报告API调用失败: ${$node.data.error}`,
    severity: 'high'
  };
}

return $node.data;
```

## 📊 监控和日志

### 系统监控接口

```http
GET /api/reports/health
GET /api/reports/metrics
GET /api/reports/logs?level=error&limit=100
```

### n8n监控工作流

```yaml
name: "系统健康监控"
trigger: "Schedule (每5分钟)"
steps:
  1. 健康检查
     URL: GET /api/reports/health
     
  2. 性能监控
     URL: GET /api/reports/metrics
     
  3. 异常检测
     检查: 错误率、响应时间、存储空间
     
  4. 告警通知
     条件: 发现异常时触发告警
```

## 🚀 部署建议

### 1. 服务器要求

- **CPU**: 4核以上
- **内存**: 8GB以上
- **存储**: 100GB以上SSD
- **网络**: 稳定的公网IP

### 2. Docker部署

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "src.server.app:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml
version: '3.8'
services:
  deer-flow:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./outputs:/app/outputs
    environment:
      - API_KEY=your_api_key
      - DATABASE_URL=sqlite:///./reports.db
    restart: unless-stopped
```

### 3. Nginx反向代理

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location /api/reports/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 📞 技术支持

如有问题，请联系：
- **技术文档**: [项目GitHub](https://github.com/your-repo)
- **问题反馈**: 创建GitHub Issue
- **商务合作**: contact@your-company.com

---

**版本**: v1.0.0  
**更新日期**: 2024年12月27日  
**兼容性**: n8n v1.0+, Deer-Flow v2.0+ 