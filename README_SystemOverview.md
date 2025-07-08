# DeerFlow 系统架构概览界面

## 📖 简介

这是一个精美的HTML界面，全面展示了DeerFlow智能医学AI科研规划与报告生成系统的架构、组件和功能特性。

## 🚀 快速启动

### 方法一：使用Python启动器（推荐）

```bash
# 在deer-flow-main目录下运行
python view_system_overview.py
```

启动器会自动：
- 🌐 启动本地HTTP服务器
- 🔗 自动打开浏览器访问界面
- 📱 支持移动端响应式布局

### 方法二：直接用浏览器打开

```bash
# 直接用浏览器打开HTML文件
# Windows
start system_overview.html

# macOS
open system_overview.html

# Linux
xdg-open system_overview.html
```

## 🎯 界面特色

### 🎨 精美设计
- **渐变背景**：现代化的紫色渐变设计
- **卡片布局**：清晰的组件卡片展示
- **响应式设计**：完美适配手机、平板、电脑
- **交互动效**：悬停和点击动画效果

### 📊 完整内容
- **系统统计**：8个核心组件、8个研究步骤、20个研究方向、13个调研维度
- **工作流程图**：清晰展示从Coordinator到Reporter的完整流程
- **组件详情**：每个组件的功能特点和技术亮点
- **技术架构**：完整的技术栈展示

### 🔧 核心组件介绍

#### 1. 🎯 Coordinator (协调器)
- 用户交互前端接口
- 多语言支持与智能识别
- 任务分类与路由分发

#### 2. 📋 Planner (规划器)
- 标准化8步骤研究框架
- 医学AI领域专业知识
- 自适应内容生成策略

#### 3. 🔬 Research Team (研究团队)
- Google Scholar优先搜索
- PubMed医学文献检索
- Python数据分析支持

#### 4. 📚 Researcher (研究员)
- 深度信息收集与分析
- 权威文献来源优先
- 每步骤15-30篇核心文献

#### 5. 💻 Coder (程序员)
- Python数据分析处理
- 智能错误处理机制
- 文字分析优先策略

#### 6. 📝 Reporter (报告生成器)
- 20个研究方向完整撰写
- 分批生成突破token限制
- 6-8万字高质量报告

#### 7. 🔍 Research Survey (调研分析)
- 13维度标准化调研框架
- 政策环境与趋势预测
- 伦理合规风险评估

#### 8. ⚙️ Template System (模板系统)
- Jinja2智能模板引擎
- 动态变量替换
- 多语言模板管理

## 🛠️ 技术架构展示

### AI框架
- LangGraph + LangChain
- 多模型支持 (Doubao, GPT, Claude)

### 搜索引擎
- Google Scholar (学术优先)
- PubMed (医学专业)
- Tavily (通用搜索)

### 部署架构
- FastAPI Web服务
- Graph-based工作流
- 异步任务处理

## ✨ 系统核心特色

### 🔧 突破Token限制
分批生成技术，支持生成6-8万字超长研究报告，每个研究方向3000-4000字详细分析。

### 🎯 智能搜索策略
Google Scholar优先，PubMed补充，确保获取高质量学术文献和权威医学资料。

### 📊 质量评估体系
完整的质量评估系统，实时监控生成质量，确保每个研究方向的科学严谨性。

### 🌐 多语言支持
自动语言识别，中英文无缝切换，适配全球化科研需求。

## 📱 响应式支持

界面完美支持：
- 🖥️ **桌面端**：1200px+ 宽屏显示
- 📱 **平板端**：768px-1200px 中等屏幕
- 📲 **手机端**：768px以下小屏幕

## 🎯 使用场景

### 👨‍🎓 研究人员
- 了解DeerFlow系统功能
- 学习8步骤研究框架
- 掌握智能搜索策略

### 👩‍💼 项目管理者
- 系统架构全貌了解
- 技术特性评估
- 部署需求分析

### 👨‍💻 开发者
- 技术栈详细信息
- 组件功能边界
- 扩展开发参考

## 🔧 自定义修改

### 修改样式
编辑 `system_overview.html` 中的 `<style>` 部分：

```css
/* 修改主题色 */
background: linear-gradient(135deg, #你的颜色1, #你的颜色2);

/* 修改卡片样式 */
.component-card {
    /* 你的自定义样式 */
}
```

### 添加组件
在 `components-grid` 部分添加新的组件卡片：

```html
<div class="component-card">
    <div class="component-icon">🆕</div>
    <h3 class="component-title">新组件名称</h3>
    <p class="component-description">组件描述</p>
    <ul class="features-list">
        <li>功能特点1</li>
        <li>功能特点2</li>
    </ul>
</div>
```

## 📝 版本信息

- **版本**: 1.0.0
- **创建时间**: 2024年11月
- **兼容性**: 现代浏览器 (Chrome, Firefox, Safari, Edge)
- **响应式**: 完全支持移动设备

## 🤝 贡献

如果您有改进建议或发现问题，欢迎：
1. 提交Issue反馈问题
2. 提出功能改进建议
3. 提交PR贡献代码

---

**DeerFlow** - 让AI突破token限制，生成无限长度的高质量科研内容！ 