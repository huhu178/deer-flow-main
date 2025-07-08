# 🔗 n8n + Deer-Flow AI 集成使用指南

## 🚀 快速开始

### 前提条件
- ✅ 您的Deer-Flow AI系统正常运行
- ✅ 安装Node.js（从 https://nodejs.org/ 下载LTS版本）

### 一键安装n8n
1. 双击运行 `install-n8n.bat`
2. 等待安装完成
3. n8n将自动启动在 http://localhost:5678

## 🎯 使用步骤

### 步骤1：启动服务
1. **启动您的AI系统**（如果还没启动）
2. **启动n8n**：双击 `install-n8n.bat`

### 步骤2：登录n8n
1. 访问 http://localhost:5678
2. 登录信息：
   - 用户名：`admin`
   - 密码：`changeme123`

### 步骤3：创建工作流
1. 点击"New Workflow"
2. 导入模板工作流：
   - 点击"Import from File"
   - 选择 `n8n-workflow-template.json`

### 步骤4：测试工作流
1. 保存并激活工作流
2. 复制Webhook URL
3. 发送测试请求：

```bash
# 使用curl测试
curl -X POST "YOUR_WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d '{"topic": "AI在医疗领域的应用研究"}'

# 或使用PowerShell
Invoke-RestMethod -Uri "YOUR_WEBHOOK_URL" -Method POST -Body '{"topic": "AI在医疗领域的应用研究"}' -ContentType "application/json"
```

## 🔧 高级配置

### 自定义工作流
您可以创建更复杂的工作流：

#### 1. 研究报告生成工作流
- **触发器**：Webhook接收研究主题
- **处理**：调用Deer-Flow API生成报告
- **通知**：发送邮件/钉钉通知

#### 2. 批量报告处理工作流
- **触发器**：定时任务
- **处理**：批量处理多个研究主题
- **输出**：汇总报告

#### 3. 报告质量检查工作流
- **触发器**：报告创建完成
- **处理**：AI质量评估
- **输出**：质量报告

### API端点说明

您的AI系统提供以下API端点：

```
POST /api/reports/webhook/n8n
```

**请求格式**：
```json
{
  "action": "create",
  "data": {
    "report_id": "unique_id",
    "content": "报告内容",
    "metadata": {"type": "research"}
  }
}
```

**其他可用操作**：
- `action: "list"` - 获取报告列表
- `action: "get"` - 获取特定报告
- `action: "search"` - 搜索报告
- `action: "delete"` - 删除报告

## 🎨 工作流示例

### 示例1：简单研究报告生成
```
Webhook → HTTP Request (Deer-Flow API) → Email Notification
```

### 示例2：多步骤研究流程
```
Webhook → Data Validation → AI Research → Quality Check → Report Storage → Notification
```

### 示例3：定时报告汇总
```
Cron Trigger → Get Report List → Generate Summary → Send to Team
```

## 🛠️ 故障排除

### 问题1：n8n无法连接到AI系统
**解决方案**：
- 确认AI系统在 http://localhost:8000 运行
- 检查防火墙设置
- 使用 `http://localhost:8000/api/reports/health` 测试API

### 问题2：Webhook无响应
**解决方案**：
- 检查工作流是否已激活
- 确认Webhook URL正确
- 查看n8n执行日志

### 问题3：API调用失败
**解决方案**：
- 检查请求格式是否正确
- 确认Content-Type为application/json
- 查看AI系统日志

## 📊 监控和管理

### 查看执行历史
1. 在n8n界面点击"Executions"
2. 查看每次执行的详细信息
3. 调试失败的执行

### 性能监控
- 监控API响应时间
- 查看工作流执行频率
- 设置告警通知

## 🎉 成功验证

当您看到以下情况时，说明集成成功：
- ✅ n8n界面正常访问
- ✅ 工作流可以成功执行
- ✅ AI API调用返回正确结果
- ✅ 报告正常生成和存储

## 📞 获取帮助

如果遇到问题：
1. 查看n8n执行日志
2. 检查AI系统健康状态：http://localhost:8000/api/reports/health
3. 参考API文档：http://localhost:8000/docs

---

**现在您可以让团队成员通过n8n工作流来使用您的AI研究系统了！** 🚀 