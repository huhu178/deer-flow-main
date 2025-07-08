#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多模型管理器
整合配置管理和报告生成功能，支持同时使用多个模型生成报告
"""

import asyncio
import json
import logging
import os
import shutil
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import re

from langchain_core.messages import HumanMessage, SystemMessage

# 添加项目路径
current_dir = Path(__file__).parent.parent.parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from src.llms.llm import get_llm_by_model_name, get_all_available_models, is_multi_model_enabled
from src.config import load_yaml_config

logger = logging.getLogger(__name__)


class MultiModelConfigManager:
    """多模型配置管理器"""
    
    def __init__(self, config_path: str = None):
        """
        初始化配置管理器
        
        Args:
            config_path: 配置文件路径
        """
        if config_path is None:
            config_path = str(Path(__file__).parent.parent.parent / "conf.yaml")
        
        self.config_path = Path(config_path)
        self.backup_dir = self.config_path.parent / "config_backups"
        self.backup_dir.mkdir(exist_ok=True)
        
        logger.info(f"多模型配置管理器初始化完成")
        logger.info(f"配置文件: {self.config_path}")
    
    def get_available_models(self) -> List[str]:
        """获取可用的模型列表"""
        try:
            if is_multi_model_enabled():
                return get_all_available_models()
            else:
                return ["doubao"]  # 默认模型
        except Exception as e:
            logger.error(f"获取可用模型失败: {e}")
            return []
    
    def validate_model_config(self, model_name: str) -> Dict[str, Any]:
        """
        验证模型配置
        
        Args:
            model_name: 模型名称
            
        Returns:
            Dict[str, Any]: 验证结果
        """
        try:
            # 尝试获取模型实例
            llm = get_llm_by_model_name(model_name)
            
            # 获取配置信息
            config = load_yaml_config(str(self.config_path))
            model_config_map = {
                "doubao": "BASIC_MODEL",
                "deepseek": "DEEPSEEK_MODEL", 
                "qianwen": "QIANWEN_MODEL"
            }
            
            config_key = model_config_map.get(model_name)
            if config_key and config_key in config:
                model_config = config[config_key]
                return {
                    "valid": True,
                    "config": model_config,
                    "error": None
                }
            else:
                return {
                    "valid": False,
                    "config": None,
                    "error": f"模型配置键 {config_key} 未找到"
                }
                
        except Exception as e:
            return {
                "valid": False,
                "config": None,
                "error": str(e)
            }
    
    def show_current_status(self):
        """显示当前配置状态"""
        print("\n🔧 多模型配置状态:")
        print("=" * 50)
        
        available_models = self.get_available_models()
        print(f"📋 可用模型数量: {len(available_models)}")
        
        for model_name in available_models:
            validation = self.validate_model_config(model_name)
            status = "✅" if validation["valid"] else "❌"
            print(f"{status} {model_name.upper()}: {validation.get('error', '配置正常')}")
        
        print("=" * 50)


class MultiModelReportManager:
    """多模型报告管理器"""
    
    def __init__(self, output_dir: str = "./outputs/multi_model_reports"):
        """
        初始化报告管理器
        
        Args:
            output_dir: 报告输出目录
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 模型显示名称映射
        self.model_display_names = {
            "doubao": "豆包 Thinking Pro",
            "deepseek": "DeepSeek V3", 
            "qianwen": "千问 Plus"
        }
        
        logger.info(f"多模型报告管理器初始化完成")
        logger.info(f"输出目录: {self.output_dir}")
    
    async def generate_report_with_model(
        self, 
        model_name: str, 
        task_description: str, 
        research_findings: List[str] = None,
        locale: str = "zh-CN"
    ) -> Dict[str, Any]:
        """
        使用指定模型生成报告
        
        Args:
            model_name: 模型名称
            task_description: 任务描述
            research_findings: 研究发现列表
            locale: 语言区域
            
        Returns:
            Dict[str, Any]: 生成结果
        """
        start_time = time.time()
        
        try:
            # 获取模型实例
            llm = get_llm_by_model_name(model_name)
            
            # 构建提示消息
            messages = self._build_report_messages(task_description, research_findings, locale)
            
            # 生成报告
            display_name = self.model_display_names.get(model_name, model_name)
            logger.info(f"开始使用 {display_name} 生成报告...")
            
            # 设置更高的输出长度限制 - 大幅增加
            if hasattr(llm, 'max_tokens'):
                llm.max_tokens = 12000  # 修复：使用合理的数值
            elif hasattr(llm, 'model_kwargs'):
                llm.model_kwargs = llm.model_kwargs or {}
                llm.model_kwargs['max_tokens'] = 12000
            
            # 设置其他参数以确保完整输出
            if hasattr(llm, 'temperature'):
                llm.temperature = 0.7  # 适中的创造性
            elif hasattr(llm, 'model_kwargs'):
                llm.model_kwargs['temperature'] = 0.7
            
            # 针对不同模型使用不同的参数名称
            try:
                # 尝试设置豆包模型的特定参数
                if model_name == "doubao" and hasattr(llm, 'model_kwargs'):
                    llm.model_kwargs['max_completion_tokens'] = 12000
                    llm.model_kwargs['temperature'] = 0.7
                # 尝试设置其他模型的参数
                elif hasattr(llm, 'model_kwargs'):
                    if 'max_tokens' not in llm.model_kwargs:
                        llm.model_kwargs['max_tokens'] = 12000
                    if 'temperature' not in llm.model_kwargs:
                        llm.model_kwargs['temperature'] = 0.7
            except Exception as e:
                logger.warning(f"设置模型参数时出现警告: {e}")
                
            # 添加强制完成指令
            completion_instruction = """
## 🚨 重要提醒：必须完成所有20个研究方向

请确保：
1. 生成完整的20个研究方向详细阐述
2. 每个方向都包含完整的10个要点
3. 不要因为长度限制而省略任何方向
4. 如果接近输出限制，请优先保证20个方向的完整性
5. 可以适当简化其他部分，但研究方向必须完整

现在开始生成完整报告：
            """
            
            messages.append(HumanMessage(content=completion_instruction))
            
            response = await llm.ainvoke(messages)
            
            execution_time = time.time() - start_time
            
            # 检查输出是否完整
            content = response.content
            direction_count = content.count("研究方向") + content.count("### 研究方向") + content.count("## 研究方向")
            
            # 更精确的方向计数
            detailed_direction_patterns = [
                r"### 方向\d+",
                r"## 方向\d+", 
                r"### 研究方向\d+",
                r"## 研究方向\d+",
                r"方向\d+：.*?背景与意义",
                r"研究方向\d+：.*?背景与意义"
            ]
            
            detailed_count = 0
            for pattern in detailed_direction_patterns:
                matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
                detailed_count = max(detailed_count, len(matches))
            
            logger.info(f"{display_name} 检测到 {direction_count} 个研究方向提及，{detailed_count} 个详细方向")
            
            # 如果方向数量不足，尝试补充生成
            if detailed_count < 20:
                logger.warning(f"{display_name} 生成的详细方向不足({detailed_count}/20)，尝试补充生成...")
                
                # 分析已生成的内容，找出缺失的方向
                generated_directions = set()
                for i in range(1, 21):
                    direction_pattern = f"研究方向{i}：.*?背景与意义"
                    if re.search(direction_pattern, content, re.DOTALL | re.IGNORECASE):
                        generated_directions.add(i)
                
                missing_directions = [i for i in range(1, 21) if i not in generated_directions]
                
                if missing_directions:
                    logger.info(f"缺失的研究方向: {missing_directions}")
                    
                    # 构建更明确的补充生成提示
                    supplement_prompt = f"""
## 📝 继续完成剩余研究方向的详细阐述

您已经生成了研究方向概览表，但详细阐述部分不完整。请继续生成以下缺失方向的完整10要点分析：

缺失方向：{missing_directions}

请按照以下格式，为每个缺失的研究方向生成完整的10个要点：

### 研究方向X：[方向名称]

1. **背景与意义**
   [详细阐述背景和研究意义]

2. **立论依据与假说**
   [提出具体的研究假说和理论依据]

3. **研究内容与AI/ML策略**
   [详细描述研究内容和AI技术方案]

4. **研究目标**
   [明确的、可量化的研究目标]

5. **拟解决的关键科学问题**
   [核心科学问题和技术挑战]

6. **研究方案**
   [具体的实施方案和时间安排]

7. **可行性分析**
   [技术可行性和资源条件分析]

8. **创新性与颠覆性潜力**
   [突出创新点和潜在影响]

9. **预期时间表与成果**
   [时间规划和预期产出]

10. **研究基础与支撑条件**
    [现有基础和所需条件]

请现在开始生成缺失方向的详细内容：
                    """
                    
                    # 使用新的消息列表，避免累积过长的上下文
                    supplement_messages = [
                        messages[0],  # 保留系统消息
                        HumanMessage(content=supplement_prompt)
                    ]
                    
                    try:
                        # 设置更高的输出限制用于补充生成
                        if hasattr(llm, 'max_tokens'):
                            original_max_tokens = llm.max_tokens
                            llm.max_tokens = 15000  # 更高的限制
                        elif hasattr(llm, 'model_kwargs'):
                            original_max_tokens = llm.model_kwargs.get('max_tokens', 12000)
                            llm.model_kwargs['max_tokens'] = 15000
                        
                        supplement_response = await llm.ainvoke(supplement_messages)
                        
                        # 恢复原始设置
                        if hasattr(llm, 'max_tokens'):
                            llm.max_tokens = original_max_tokens
                        elif hasattr(llm, 'model_kwargs'):
                            llm.model_kwargs['max_tokens'] = original_max_tokens
                        
                        # 合并内容
                        supplement_content = supplement_response.content
                        content += "\n\n## 补充生成的研究方向详细阐述\n\n" + supplement_content
                        
                        # 重新计算方向数量
                        direction_count = content.count("研究方向") + content.count("### 研究方向") + content.count("## 研究方向")
                        detailed_count = 0
                        for pattern in detailed_direction_patterns:
                            matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
                            detailed_count = max(detailed_count, len(matches))
                        
                        logger.info(f"{display_name} 补充生成后：{direction_count} 个研究方向提及，{detailed_count} 个详细方向")
                        
                    except Exception as e:
                        logger.error(f"{display_name} 补充生成失败: {e}")
                else:
                    logger.info("未能识别缺失的具体方向编号")
            
            result = {
                "model_name": model_name,
                "model_display_name": display_name,
                "content": content,
                "execution_time": execution_time,
                "success": True,
                "error": None,
                "timestamp": datetime.now().isoformat(),
                "direction_count": direction_count,
                "detailed_direction_count": detailed_count  # 添加详细方向计数
            }
            
            logger.info(f"{display_name} 报告生成完成 (耗时: {execution_time:.2f}秒, 详细方向: {detailed_count}/20)")
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"模型 {model_name} 生成报告失败: {str(e)}"
            logger.error(error_msg)
            
            return {
                "model_name": model_name,
                "model_display_name": self.model_display_names.get(model_name, model_name),
                "content": None,
                "execution_time": execution_time,
                "success": False,
                "error": error_msg,
                "timestamp": datetime.now().isoformat()
            }
    
    def _build_report_messages(
        self, 
        task_description: str, 
        research_findings: List[str] = None,
        locale: str = "zh-CN"
    ) -> List[Any]:
        """
        构建报告生成的提示消息 - 使用系统的专业提示词
        
        Args:
            task_description: 任务描述
            research_findings: 研究发现
            locale: 语言区域
            
        Returns:
            List[Any]: 消息列表
        """
        # 使用系统的reporter.md提示词而不是自定义提示词
        try:
            # 导入系统提示词模板
            from src.prompts.template import apply_prompt_template
            from langchain_core.messages import HumanMessage
            
            # 构建state对象，模拟正常的reporter工作流程
            mock_state = {
                "messages": [
                    HumanMessage(content=f"# Research Requirements\n\n## Task\n\n{task_description}")
                ],
                "locale": locale,
                "observations": research_findings if research_findings else []
            }
            
            # 使用系统的reporter提示词模板
            messages = apply_prompt_template("reporter", mock_state)
            
            # 添加研究发现
            if research_findings and len(research_findings) > 0:
                findings_content = "\n\n".join([f"### 研究发现 {i+1}\n{finding}" for i, finding in enumerate(research_findings)])
                messages.append(HumanMessage(content=f"## 研究发现和背景资料\n{findings_content}"))
            
            # 添加强化的20个研究方向要求
            enforcement_message = HumanMessage(content="""
## 🎯 关键要求强化

**必须严格遵循以下要求：**

1. ✅ **生成完整的20个研究方向** - 不得少于20个，不得省略任何方向
2. ✅ **每个方向包含完整的10个要点**：
   - 背景与意义
   - 立论依据与假说
   - 研究内容与AI/ML策略
   - 研究目标
   - 拟解决的关键科学问题
   - 研究方案
   - 可行性分析
   - 创新性与颠覆性潜力
   - 预期时间表与成果
   - 研究基础与支撑条件

3. ✅ **必须包含研究方向概览表**
4. ✅ **必须包含丰富的参考文献**（15-20篇）
5. ✅ **体现Google Scholar和PubMed搜索过程**
6. ✅ **内容要专业、详细、具有实用价值**

**重要提醒**：这是一个多模型对比生成任务，您的输出质量将与其他模型进行对比。请确保生成最高质量的完整报告。

**开始生成包含20个完整研究方向的专业报告：**
            """)
            
            messages.append(enforcement_message)
            
            return messages
            
        except Exception as e:
            logger.error(f"使用系统提示词失败，回退到简化提示词: {e}")
            
            # 回退到改进的简化提示词
            system_prompt = """你是专业的医学AI科研报告专家，请严格按照系统要求生成报告。

## 核心任务
生成包含**完整20个研究方向**的详细科研报告。

## 绝对要求
1. 必须生成完整的20个研究方向
2. 每个方向必须包含10个要点
3. 必须包含研究方向概览表
4. 必须包含参考文献部分
5. 不得省略任何方向或要点

## 报告结构
```
# 标题

## 关键要点
- [3-5个要点]

## 概述
[概述内容]

## 研究方向概览表
| 编号 | 方向标题 | 主要目标 | AI策略 | 创新点 |
|------|---------|---------|--------|--------|
| 1-20 | [完整的20个方向] | ... | ... | ... |

## 20个研究方向详细阐述

### 研究方向1: [标题]
1. **背景与意义**: [详细内容]
2. **立论依据与假说**: [详细内容]
3. **研究内容与AI/ML策略**: [详细内容]
4. **研究目标**: [详细内容]
5. **拟解决的关键科学问题**: [详细内容]
6. **研究方案**: [详细内容]
7. **可行性分析**: [详细内容]
8. **创新性与颠覆性潜力**: [详细内容]
9. **预期时间表与成果**: [详细内容]
10. **研究基础与支撑条件**: [详细内容]

[继续到研究方向20...]

## 参考文献
[15-20篇参考文献]
```

重要：必须完成所有20个研究方向的完整阐述！"""
            
            messages = [SystemMessage(content=system_prompt)]
            messages.append(HumanMessage(content=f"## 任务\n{task_description}"))
            
            if research_findings and len(research_findings) > 0:
                findings_content = "\n\n".join([f"### 研究发现 {i+1}\n{finding}" for i, finding in enumerate(research_findings)])
                messages.append(HumanMessage(content=f"## 研究发现\n{findings_content}"))
            
            messages.append(HumanMessage(content="现在开始生成包含完整20个研究方向的报告："))
            
            return messages
    
    async def generate_parallel_reports(
        self, 
        task_description: str, 
        research_findings: List[str] = None,
        locale: str = "zh-CN",
        models: List[str] = None
    ) -> Dict[str, Any]:
        """
        并行生成多模型报告
        
        Args:
            task_description: 任务描述
            research_findings: 研究发现
            locale: 语言区域
            models: 指定使用的模型列表，None表示使用所有可用模型
            
        Returns:
            Dict[str, Any]: 所有模型的生成结果
        """
        # 获取可用模型
        config_manager = MultiModelConfigManager()
        available_models = config_manager.get_available_models()
        
        # 确定要使用的模型
        target_models = models if models else available_models
        target_models = [m for m in target_models if m in available_models]
        
        if not target_models:
            raise ValueError("没有可用的模型")
        
        logger.info(f"开始并行生成报告，使用模型: {target_models}")
        
        # 并行执行
        tasks = [
            self.generate_report_with_model(model, task_description, research_findings, locale)
            for model in target_models
        ]
        
        start_time = time.time()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        total_time = time.time() - start_time
        
        # 处理结果
        report_results = {}
        successful_reports = 0
        
        for i, result in enumerate(results):
            model_name = target_models[i]
            
            if isinstance(result, Exception):
                report_results[model_name] = {
                    "model_name": model_name,
                    "model_display_name": self.model_display_names.get(model_name, model_name),
                    "content": None,
                    "execution_time": 0,
                    "success": False,
                    "error": str(result),
                    "timestamp": datetime.now().isoformat()
                }
            else:
                report_results[model_name] = result
                if result["success"]:
                    successful_reports += 1
        
        # 生成汇总信息
        summary = {
            "task_description": task_description,
            "total_models": len(target_models),
            "successful_reports": successful_reports,
            "failed_reports": len(target_models) - successful_reports,
            "total_execution_time": total_time,
            "timestamp": datetime.now().isoformat(),
            "locale": locale
        }
        
        return {
            "summary": summary,
            "reports": report_results
        }
    
    def save_reports(self, results: Dict[str, Any], filename_prefix: str = None) -> Dict[str, str]:
        """
        保存报告到文件
        
        Args:
            results: 报告生成结果
            filename_prefix: 文件名前缀
            
        Returns:
            Dict[str, str]: 保存的文件路径
        """
        if not filename_prefix:
            filename_prefix = f"multi_model_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        saved_files = {}
        
        # 保存各个模型的报告
        for model_name, report in results["reports"].items():
            if report["success"] and report["content"]:
                filename = f"{filename_prefix}_{model_name}.md"
                filepath = self.output_dir / filename
                
                # 构建报告内容
                content = f"""# {report['model_display_name']} 生成报告

**生成时间**: {report['timestamp']}
**执行时间**: {report['execution_time']:.2f}秒
**模型**: {report['model_display_name']} ({report['model_name']})

---

{report['content']}

---

*本报告由 {report['model_display_name']} 自动生成*
"""
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                saved_files[model_name] = str(filepath)
                logger.info(f"已保存 {report['model_display_name']} 报告: {filepath}")
        
        # 保存汇总报告
        summary_filename = f"{filename_prefix}_summary.json"
        summary_filepath = self.output_dir / summary_filename
        
        with open(summary_filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        saved_files["summary"] = str(summary_filepath)
        
        # 生成对比报告
        comparison_filename = f"{filename_prefix}_comparison.md"
        comparison_filepath = self.output_dir / comparison_filename
        
        comparison_content = self._generate_comparison_report(results)
        with open(comparison_filepath, 'w', encoding='utf-8') as f:
            f.write(comparison_content)
        
        saved_files["comparison"] = str(comparison_filepath)
        
        logger.info(f"报告保存完成，共保存 {len(saved_files)} 个文件")
        return saved_files
    
    def _generate_comparison_report(self, results: Dict[str, Any]) -> str:
        """
        生成模型对比报告
        
        Args:
            results: 报告结果
            
        Returns:
            str: 对比报告内容
        """
        summary = results["summary"]
        reports = results["reports"]
        
        content = f"""# 多模型报告生成对比分析

## 任务概述
**任务描述**: {summary['task_description']}
**生成时间**: {summary['timestamp']}
**总执行时间**: {summary['total_execution_time']:.2f}秒

## 执行统计
- **参与模型数**: {summary['total_models']}
- **成功生成**: {summary['successful_reports']}
- **生成失败**: {summary['failed_reports']}

## 模型性能对比

| 模型 | 状态 | 执行时间(秒) | 内容长度(字符) | 备注 |
|------|------|-------------|---------------|------|
"""
        
        for model_name, report in reports.items():
            status = "✅ 成功" if report["success"] else "❌ 失败"
            exec_time = f"{report['execution_time']:.2f}" if report["execution_time"] else "N/A"
            content_length = len(report["content"]) if report["content"] else 0
            note = "正常" if report["success"] else report.get("error", "未知错误")[:50]
            
            content += f"| {report['model_display_name']} | {status} | {exec_time} | {content_length} | {note} |\n"
        
        content += "\n## 详细分析\n\n"
        
        # 成功的报告分析
        successful_reports = [r for r in reports.values() if r["success"]]
        if successful_reports:
            content += "### 成功生成的报告\n\n"
            for report in successful_reports:
                content += f"#### {report['model_display_name']}\n"
                content += f"- **执行时间**: {report['execution_time']:.2f}秒\n"
                content += f"- **内容长度**: {len(report['content'])}字符\n"
                content += f"- **生成时间**: {report['timestamp']}\n\n"
        
        # 失败的报告分析
        failed_reports = [r for r in reports.values() if not r["success"]]
        if failed_reports:
            content += "### 生成失败的报告\n\n"
            for report in failed_reports:
                content += f"#### {report['model_display_name']}\n"
                content += f"- **错误信息**: {report.get('error', '未知错误')}\n"
                content += f"- **尝试时间**: {report['timestamp']}\n\n"
        
        content += "\n## 使用建议\n\n"
        if successful_reports:
            fastest_model = min(successful_reports, key=lambda x: x["execution_time"])
            longest_content = max(successful_reports, key=lambda x: len(x["content"]))
            
            content += f"- **最快模型**: {fastest_model['model_display_name']} ({fastest_model['execution_time']:.2f}秒)\n"
            content += f"- **内容最详细**: {longest_content['model_display_name']} ({len(longest_content['content'])}字符)\n"
            content += f"- **建议**: 根据需求选择合适的模型，追求速度选择{fastest_model['model_display_name']}，追求详细度选择{longest_content['model_display_name']}\n"
        
        content += f"\n---\n*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"
        
        return content


class MultiModelManager:
    """多模型管理器 - 整合配置和报告功能"""
    
    def __init__(self, config_path: str = None, output_dir: str = "./outputs/multi_model_reports"):
        """
        初始化多模型管理器
        
        Args:
            config_path: 配置文件路径
            output_dir: 报告输出目录
        """
        self.config_manager = MultiModelConfigManager(config_path)
        self.report_manager = MultiModelReportManager(output_dir)
        
        logger.info("多模型管理器初始化完成")
    
    def show_status(self):
        """显示系统状态"""
        self.config_manager.show_current_status()
    
    def get_available_models(self) -> List[str]:
        """获取可用模型列表"""
        return self.config_manager.get_available_models()
    
    async def generate_multi_model_reports(
        self, 
        task_description: str, 
        research_findings: List[str] = None,
        locale: str = "zh-CN",
        models: List[str] = None,
        filename_prefix: str = None
    ) -> Dict[str, Any]:
        """
        生成多模型报告并保存
        
        Args:
            task_description: 任务描述
            research_findings: 研究发现
            locale: 语言区域
            models: 指定使用的模型列表
            filename_prefix: 文件名前缀
            
        Returns:
            Dict[str, Any]: 包含报告结果和保存文件路径的字典
        """
        # 生成报告
        results = await self.report_manager.generate_parallel_reports(
            task_description=task_description,
            research_findings=research_findings,
            locale=locale,
            models=models
        )
        
        # 保存报告
        saved_files = self.report_manager.save_reports(results, filename_prefix)
        
        return {
            "results": results,
            "saved_files": saved_files
        } 