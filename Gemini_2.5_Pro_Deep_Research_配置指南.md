# Gemini 2.5 Pro Deep Research 配置与使用指南

## 🔬 什么是Gemini Deep Research？

Gemini 2.5 Pro的Deep Research是Google最新推出的AI研究助手功能，能够：
- **自主搜索网络信息**：自动收集最新、最相关的研究资料
- **深度分析能力**：对复杂主题进行多角度、多层次的研究分析
- **结构化报告生成**：自动生成专业级的研究报告
- **引用追踪**：提供可验证的信息来源

## 🎯 核心优势

### 1. 自主研究能力
- 自动制定研究计划
- 智能搜索策略
- 多源信息整合
- 实时验证信息准确性

### 2. 深度思考模式
- 多步推理分析
- 批判性思维评估
- 假设验证机制
- 逻辑链条构建

### 3. 专业报告生成
- 学术级写作标准
- 结构化内容组织
- 完整引用体系
- 多格式输出支持

## 🛠️ 配置方案

### 方案一：Google AI Studio 直接访问（推荐）

#### 1. 获取API密钥
```bash
# 访问 https://aistudio.google.com/
# 登录Google账号
# 创建新项目
# 生成API密钥
```

#### 2. 修改配置文件
```yaml
# deer-flow-main/conf.yaml
llm:
  BASIC_MODEL:
    # Gemini 2.5 Pro Deep Research 配置
    base_url: "https://generativelanguage.googleapis.com/v1beta"
    model: "gemini-2.5-pro-latest"
    api_key: "YOUR_GOOGLE_AI_API_KEY"
    max_tokens: 32768  # 支持更长的研究报告
    temperature: 0.3   # 较低温度确保准确性
    timeout: 300       # Deep Research需要更长时间
    max_retries: 3
    request_timeout: 300
    
    # Deep Research 特有配置
    features:
      deep_research: true
      web_search: true
      citation_mode: "academic"
      research_depth: "comprehensive"
```

### 方案二：通过中转服务访问

#### 选项1：OpenRouter (当前使用)
```yaml
llm:
  BASIC_MODEL:
    base_url: "https://openrouter.ai/api/v1"
    model: "google/gemini-2.5-pro"  # 已支持Deep Research
    api_key: "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"
    max_tokens: 32768
    temperature: 0.3
    timeout: 300
    
    # 启用Deep Research功能
    extra_headers:
      "X-Enable-Deep-Research": "true"
      "X-Research-Mode": "comprehensive"
```

## 🚀 立即体验Deep Research

让我们直接测试当前系统的Deep Research能力：

### 通过laozhang.ai使用Deep Research

#### 1. 配置示例
```yaml
# deer-flow-main/conf.yaml 
llm:
  BASIC_MODEL:
    base_url: "https://api.laozhang.ai/v1"
    model: "gemini-2.5-pro"
    api_key: "YOUR_LAOZHANG_API_KEY"  # 从laozhang.ai获取
    max_tokens: 32768
    temperature: 0.3
    timeout: 300
    
    # Deep Research 专用配置
    extra_headers:
      "X-Enable-Deep-Research": "true"
      "X-Research-Mode": "comprehensive"
```

#### 2. Python代码示例
```python
import requests
import json

def deep_research_with_laozhang(topic, depth="comprehensive"):
    api_url = "https://api.laozhang.ai/v1/chat/completions"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer YOUR_LAOZHANG_API_KEY",
        "X-Enable-Deep-Research": "true",  # 启用Deep Research
        "X-Research-Mode": depth           # 设置研究深度
    }
    
    payload = {
        "model": "gemini-2.5-pro",
        "messages": [{
            "role": "user",
            "content": f"""
            [启用Deep Research模式]
            
            请对以下主题进行深度研究：
            {topic}
            
            研究要求：
            1. 自主搜索最新信息和研究
            2. 多角度分析和验证
            3. 生成结构化研究报告
            4. 提供可靠的引用来源
            
            请开始深度研究...
            """
        }],
        "temperature": 0.3,
        "max_tokens": 32768
    }
    
    response = requests.post(api_url, headers=headers, json=payload)
    return response.json()

# 使用示例
result = deep_research_with_laozhang("人工智能在医疗诊断中的最新突破")
print(result['choices'][0]['message']['content'])
```

#### 3. 立即测试
您可以立即用当前的OpenRouter配置测试Deep Research功能：

```python
# 修改您当前的提示词格式
deep_research_prompt = """
[Deep Research Mode - 深度研究模式]

主题：量子计算在密码学中的应用前景

请执行以下研究流程：
1. 🔍 自主制定研究计划和策略
2. 🌐 搜索最新相关研究和报告  
3. 🧠 多维度深度分析和推理
4. 📊 整合信息并验证来源
5. 📝 生成结构化研究报告

研究深度：comprehensive（全面深入）
时间范围：2023-2025年最新发展
引用要求：提供可验证的信息来源

开始深度研究...
"""
```

### Deep Research功能特点

#### ✅ 支持的核心功能
- **自主网络搜索**：自动搜索相关信息
- **多步推理分析**：深度思考和逻辑推理  
- **信息来源验证**：评估信息可靠性
- **结构化报告生成**：专业级研究报告
- **实时信息获取**：获取最新发展动态

#### 🎯 最佳使用场景
- 学术研究和文献综述
- 市场分析和竞争情报  
- 技术趋势研究
- 政策法规分析
- 产品比较评估

#### 💡 优化建议
- 明确指定研究深度和范围
- 提供具体的研究要求
- 设置合理的时间范围
- 要求提供引用来源

## 🚀 使用Deep Research功能

### 1. 基础研究查询
```python
# 示例：使用Deep Research进行主题研究
research_prompt = """
请使用Deep Research功能深度研究：
"2025年人工智能在医疗诊断中的最新突破"

研究要求：
1. 搜索最新的研究论文和报告
2. 分析技术发展趋势
3. 评估临床应用前景
4. 提供完整的引用来源
5. 生成结构化研究报告

请开始深度研究。
"""
```

### 2. 高级研究配置
```python
import requests

def deep_research_query(topic, research_depth="comprehensive"):
    api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro:generateContent"
    
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": "YOUR_API_KEY"
    }
    
    payload = {
        "contents": [{
            "parts": [{
                "text": f"""
                [DEEP RESEARCH MODE]
                
                研究主题: {topic}
                
                研究深度: {research_depth}
                
                执行以下研究流程：
                1. 制定研究计划
                2. 自主搜索相关信息
                3. 多角度分析验证
                4. 生成专业研究报告
                5. 提供可验证的引用来源
                
                开始深度研究...
                """
            }]
        }],
        "generationConfig": {
            "maxOutputTokens": 32768,
            "temperature": 0.3,
            "topP": 0.8
        },
        "safetySettings": [
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            }
        ],
        # 启用Deep Research功能
        "systemInstruction": {
            "parts": [{
                "text": "You are a professional research assistant with deep research capabilities. Use web search and comprehensive analysis to provide thorough, well-cited research reports."
            }]
        }
    }
    
    response = requests.post(api_url, headers=headers, json=payload)
    return response.json()
```

### 3. 集成到现有系统
```python
# 修改 deer-flow-main/src/llms/llm.py
class GeminiDeepResearchLLM:
    def __init__(self, config):
        self.config = config
        self.deep_research_enabled = config.get('features', {}).get('deep_research', False)
    
    def generate_deep_research_report(self, topic, requirements=None):
        """
        使用Gemini 2.5 Pro Deep Research生成深度研究报告
        """
        base_prompt = f"""
        [启用深度研究模式]
        
        研究主题: {topic}
        
        请执行以下研究流程：
        1. 自主制定研究计划
        2. 搜索最新相关信息
        3. 多维度深度分析
        4. 生成结构化报告
        5. 提供完整引用体系
        
        {requirements or ''}
        
        开始深度研究...
        """
        
        return self._make_api_call(base_prompt)
```

## 🎛️ 优化配置建议

### 1. 性能优化
```yaml
# 针对Deep Research的性能优化
DEEP_RESEARCH_CONFIG:
  max_research_time: 600  # 最大研究时间（秒）
  max_search_queries: 20  # 最大搜索次数
  min_source_quality: 0.8  # 最小来源质量分数
  citation_format: "APA"   # 引用格式
  report_length: "comprehensive"  # 报告详细程度
```

### 2. 成本控制
```yaml
# 成本控制配置
COST_CONTROL:
  enable_caching: true     # 启用结果缓存
  cache_duration: 24       # 缓存时长（小时）
  max_tokens_per_research: 50000  # 每次研究最大token数
  batch_research: true     # 批量研究模式
```

### 3. 质量保证
```yaml
# 质量保证配置
QUALITY_CONFIG:
  fact_checking: true      # 启用事实检查
  source_verification: true # 来源验证
  bias_detection: true     # 偏见检测
  accuracy_threshold: 0.9  # 准确性阈值
```

## 📊 实际应用示例

### 示例1：医疗AI研究
```python
research_topic = "2025年AI辅助医疗诊断的最新突破与挑战"

deep_research_result = gemini_llm.generate_deep_research_report(
    topic=research_topic,
    requirements="""
    1. 重点关注影像诊断和病理分析
    2. 分析FDA批准的最新AI医疗设备
    3. 评估临床试验数据和效果
    4. 讨论伦理和监管挑战
    5. 预测未来5年发展趋势
    """
)
```

### 示例2：技术趋势分析
```python
research_topic = "量子计算在密码学中的应用前景"

deep_research_result = gemini_llm.generate_deep_research_report(
    topic=research_topic,
    requirements="""
    1. 分析当前量子计算硬件发展
    2. 评估对现有加密算法的威胁
    3. 研究后量子密码学解决方案
    4. 分析各国政策和投资趋势
    5. 预测实用化时间表
    """
)
```

## ⚡ 快速启动

### 1. 立即体验（使用当前OpenRouter配置）
```bash
cd deer-flow-main
python -c "
from src.llms.llm import get_llm
llm = get_llm()
result = llm.generate('请使用深度研究功能分析：人工智能在教育领域的创新应用')
print(result)
"
```

### 2. 升级到官方API
```bash
# 1. 获取Google AI API密钥
# 2. 修改 conf.yaml 中的配置
# 3. 重启系统
python src/workflow.py --enable-deep-research
```

## 🔍 监控和调试

### 1. 研究质量指标
- 信息源数量和质量
- 引用准确性
- 分析深度评分
- 逻辑一致性检查

### 2. 性能监控
- 研究时间消耗
- Token使用统计
- API调用成功率
- 缓存命中率

### 3. 成本追踪
- 每次研究成本
- 月度使用统计
- 性价比分析
- 预算预警

## 📝 注意事项

1. **API限制**：Deep Research功能可能有特殊的速率限制
2. **成本控制**：深度研究消耗较多token，注意成本控制
3. **结果验证**：虽然有自动验证，仍建议人工核查重要信息
4. **网络依赖**：需要稳定的网络连接进行实时搜索

## 🎯 下一步行动

1. **立即尝试**：使用当前配置测试Deep Research功能
2. **评估效果**：对比传统方法和Deep Research的结果质量
3. **优化配置**：根据实际需求调整参数设置
4. **集成工作流**：将Deep Research集成到现有研究流程中

---

**开始您的Deep Research之旅！🚀** 