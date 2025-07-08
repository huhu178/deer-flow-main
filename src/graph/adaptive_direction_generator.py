#!/usr/bin/env python3
"""
自适应研究方向生成器
让大模型自主决定框架结构，而不是被固定的6部分限制
"""

from typing import List, Dict, Any
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class AdaptiveDirectionGenerator:
    """自适应研究方向生成器 - 让AI自主决定最佳框架"""
    
    def __init__(self, llm, model_name="adaptive", output_dir="./outputs/adaptive"):
        self.llm = llm
        self.model_name = model_name
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_adaptive_direction(self, direction_title: str, research_context: str, direction_number: int) -> Dict[str, Any]:
        """
        生成自适应的研究方向 - 让AI自主决定结构
        """
        
        adaptive_prompt = f"""# 自适应研究方向生成任务

## 研究背景
{research_context}

## 当前任务  
为研究方向 "{direction_title}" 生成详细内容

## 🎯 核心要求

**您是研究专家，请自主决定最适合这个研究方向的内容结构！**

### 基本原则：
1. **内容完整性**：确保涵盖该研究方向的所有重要方面
2. **逻辑清晰性**：结构合理，层次分明  
3. **科学严谨性**：基于扎实的科学依据
4. **创新突破性**：体现颠覆性创新潜力
5. **实用可行性**：具有现实可操作性

### 自主框架设计指导：
- **可以是6部分、8部分、10部分或其他结构**
- **根据研究方向特点自主调整**
- **每个部分的字数根据重要性分配**
- **可以增加特殊的分析维度**

### 思考过程展示：
请先思考：
1. 这个研究方向最需要哪些关键内容？
2. 什么样的结构最能展现其价值？
3. 哪些方面需要重点阐述？
4. 如何体现创新性和颠覆性？

## 📝 输出要求

请按照以下格式输出：

```markdown
<thinking>
让我分析这个研究方向的特点：

1. 研究方向特性分析：
   [分析该方向的独特性和重要性]

2. 最佳框架设计：
   [设计最适合的内容结构]

3. 重点内容规划：
   [确定每个部分的重点和字数分配]

4. 创新点挖掘：
   [识别独特的创新机会]
</thinking>

# 研究方向{direction_number}：{direction_title}

[根据thinking中的分析，生成完整的研究方向内容]

## 🎯 框架说明
[简要说明选择这种结构的原因]

## 📊 内容统计
- 总字数：[统计字数]
- 结构设计：[说明采用的框架]
- 创新等级：[评估创新程度]
```

## ⚠️ 重要提示

1. **完全自主**：不要被任何预设框架限制
2. **质量优先**：内容质量比格式统一更重要  
3. **创新驱动**：追求真正的突破性创新
4. **科学严谨**：确保所有内容有据可依
5. **实用导向**：考虑实际应用价值

现在请开始生成这个研究方向的内容，展现您的专业判断和创新思维！
"""
        
        try:
            logger.info(f"🧠 开始自适应生成第{direction_number}个研究方向...")
            response = self.llm.invoke(adaptive_prompt)
            
            # 处理响应
            if hasattr(response, 'content'):
                content = response.content
            else:
                content = str(response)
            
            # 分析生成的结构
            structure_analysis = self._analyze_generated_structure(content)
            
            result = {
                "direction": direction_title,
                "content": content,
                "structure_type": structure_analysis["structure_type"],
                "section_count": structure_analysis["section_count"],
                "word_count": len(content),
                "has_thinking": "<thinking>" in content,
                "innovation_level": self._assess_innovation_level(content),
                "direction_number": direction_number
            }
            
            logger.info(f"✅ 自适应生成完成 - 结构：{structure_analysis['structure_type']}, 字数：{len(content)}")
            return result
            
        except Exception as e:
            logger.error(f"❌ 自适应生成失败: {e}")
            return {
                "direction": direction_title,
                "content": f"# {direction_title}\n\n自适应生成遇到技术问题，但这仍是一个具有重要价值的研究方向。",
                "structure_type": "error",
                "section_count": 0,
                "word_count": 0,
                "has_thinking": False,
                "innovation_level": 0,
                "direction_number": direction_number
            }
    
    def _analyze_generated_structure(self, content: str) -> Dict[str, Any]:
        """分析生成内容的结构特征"""
        
        # 统计标题层级
        import re
        h1_count = len(re.findall(r'^# ', content, re.MULTILINE))
        h2_count = len(re.findall(r'^## ', content, re.MULTILINE))
        h3_count = len(re.findall(r'^### ', content, re.MULTILINE))
        
        # 判断结构类型
        if h2_count >= 8:
            structure_type = "详细型 (8+部分)"
        elif h2_count >= 6:
            structure_type = "标准型 (6-7部分)"
        elif h2_count >= 4:
            structure_type = "简洁型 (4-5部分)"
        else:
            structure_type = "自由型"
        
        return {
            "structure_type": structure_type,
            "section_count": h2_count,
            "subsection_count": h3_count,
            "total_headers": h1_count + h2_count + h3_count
        }
    
    def _assess_innovation_level(self, content: str) -> int:
        """评估创新水平 (1-10分)"""
        innovation_keywords = [
            "颠覆性", "突破性", "前所未有", "革命性", "创新性",
            "原创", "独特", "首次", "新颖", "先进",
            "变革", "重构", "重塑", "开创", "引领"
        ]
        
        content_lower = content.lower()
        keyword_count = sum(1 for keyword in innovation_keywords if keyword in content_lower)
        
        # 基于关键词密度和内容长度评分
        base_score = min(keyword_count * 1.5, 8)
        length_bonus = 1 if len(content) > 2000 else 0
        thinking_bonus = 1 if "<thinking>" in content else 0
        
        return min(int(base_score + length_bonus + thinking_bonus), 10)

def integrate_adaptive_generator(state, current_plan, directions_list, research_context):
    """
    集成自适应生成器到现有graph系统
    """
    from src.llms.llm import get_llm_by_type
    
    logger.info("🔄 启动自适应研究方向生成...")
    
    # 获取LLM
    llm = get_llm_by_type("BASIC_MODEL")
    
    # 创建自适应生成器
    generator = AdaptiveDirectionGenerator(llm)
    
    adaptive_results = []
    
    for i, direction in enumerate(directions_list[:20], 1):
        try:
            result = generator.generate_adaptive_direction(
                direction_title=direction,
                research_context=research_context,
                direction_number=i
            )
            adaptive_results.append(result)
            
            logger.info(f"📋 方向{i} - {result['structure_type']} - 创新度: {result['innovation_level']}/10")
            
        except Exception as e:
            logger.error(f"❌ 方向{i}生成失败: {e}")
            continue
    
    # 生成统计报告
    structure_stats = {}
    total_innovation = 0
    thinking_count = 0
    
    for result in adaptive_results:
        struct_type = result["structure_type"]
        structure_stats[struct_type] = structure_stats.get(struct_type, 0) + 1
        total_innovation += result["innovation_level"]
        if result["has_thinking"]:
            thinking_count += 1
    
    summary = {
        "total_directions": len(adaptive_results),
        "structure_diversity": len(structure_stats),
        "structure_distribution": structure_stats,
        "average_innovation": total_innovation / len(adaptive_results) if adaptive_results else 0,
        "thinking_percentage": (thinking_count / len(adaptive_results) * 100) if adaptive_results else 0,
        "generated_contents": adaptive_results
    }
    
    logger.info(f"🎯 自适应生成完成 - 多样性: {summary['structure_diversity']}种结构, 平均创新度: {summary['average_innovation']:.1f}/10")
    
    return summary 